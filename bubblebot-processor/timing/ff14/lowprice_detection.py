# coding: utf-8

import time
from loguru import logger
from lib.common import httpx_client
from lib.collections import SendMsg, Message, MessageData
from core import manager


async def low_price_detection(admin_robot_id: str, timing_config: dict):
    errcode = None

    world_name = timing_config.get("world_name")
    group_list = timing_config.get("group_list")

    profit_notice_threshold = timing_config.get("profit_notice_threshold")
    if isinstance(profit_notice_threshold, str) and profit_notice_threshold.isdigit():
        profit_notice_threshold = int(profit_notice_threshold)
    elif not isinstance(profit_notice_threshold, int):
        profit_notice_threshold = 50000

    max_price_per_unit = timing_config.get("max_price_per_unit")
    if isinstance(max_price_per_unit, str) and max_price_per_unit.isdigit():
        max_price_per_unit = int(max_price_per_unit)
    elif not isinstance(max_price_per_unit, int):
        max_price_per_unit = None

    entries = timing_config.get("query_entries")
    if isinstance(entries, str):
        if entries.isdigit():
            entries = int(entries)
    elif not isinstance(entries, int):
        entries = 50

    if entries < 1:
        entries = 1
    elif entries > 200:
        entries = 200

    if max_price_per_unit < 1:
        max_price_per_unit = None



    for world in world_name:

        notice_item_data_dict = {}

        # 获取最近更新的板子item数据
        if errcode == None:
            try:
                url = f"https://universalis.app/api/v2/extra/stats/most-recently-updated?world={world}&entries={entries}"
                res = await httpx_client.get(url)
                res.raise_for_status()
                recently_updated_items = [str(i.get("itemID")) for i in res.json().get("items")]
            except Exception as e:
                logger.error(f"请求交易板数据查询接口时出错, 错误信息: {repr(e)}")
                continue

        # 遍历查询item是否可以捡漏
        if errcode == None:

            try:
                ids = ",".join(recently_updated_items)
                url = f'https://universalis.app/api/v2/{world}/{ids}'
                res = await httpx_client.get(url)
                res.raise_for_status()
                item_dashboard_data_list: dict = res.json().get("items")
            except Exception as e:
                logger.error(f"请求交易板数据查询接口时出错, 错误信息: {repr(e)}")

            for item_id, item_dashboard_data in item_dashboard_data_list.items():

                # 判断是否有该物品的交易板, 如果没有获取到则跳过
                if len(item_dashboard_data.get("listings")) < 1:
                    continue

                average_transaction_price = int(item_dashboard_data.get("averagePrice"))

                last_update_time = time.localtime(item_dashboard_data.get("lastUploadTime") / 1000)
                last_update_time = time.strftime("%Y-%m-%d %H:%M:%S", last_update_time)

                item_price_listings = sorted(item_dashboard_data.get("listings"), key=lambda x: x['pricePerUnit'])[:10]

                # 获取价格最低的商品的单价和数量
                first_item_price_per_unit = item_price_listings[0].get("pricePerUnit")
                first_item_quantity = item_price_listings[0].get("quantity")
                first_world_name = item_price_listings[0].get("worldName")

                if max_price_per_unit and (first_item_price_per_unit >= max_price_per_unit):
                    continue

                # 如果板子条目大于2个才进行比较
                second_item_price_per_unit = None
                if len(item_price_listings) > 2:
                    second_item_price_per_unit = item_price_listings[1].get("pricePerUnit")
                    # 如果第二条的价格减去第一条的价格大于等于预设利润值, 则添加到通知列表
                    profit = (second_item_price_per_unit - first_item_price_per_unit) * first_item_quantity
                else:
                    profit = (average_transaction_price - first_item_price_per_unit) * first_item_quantity
                if profit >= profit_notice_threshold:
                    notice_item_data_dict[int(item_id)] = {
                        "item_id": item_id,
                        "first_world_name": first_world_name,
                        "profit": profit,
                        "first_item_price_per_unit": first_item_price_per_unit,
                        "first_item_quantity": first_item_quantity,
                        "average_transaction_price": average_transaction_price,
                        "last_update_time": last_update_time,
                        "second_item_price_per_unit": second_item_price_per_unit,
                    }

        # 查询物品名称
        try:
            ids = [str(i) for i in notice_item_data_dict.keys()]
            if len(ids) == 0:
                return

            # 只取1个结果, 所以当使用模糊匹配可能会出现并非想要的物品信息, 所以最好输入完整物品名
            item_search_url = "https://cafemaker.wakingsands.com/item"
            data = {"ids": ",".join(ids)}
            res = await httpx_client.post(item_search_url, json=data)
            res.raise_for_status()
            item_data: dict = res.json()
        except Exception as e:
            logger.error(f"请求物品id查询接口时出错, 错误信息: {repr(e)}")

        for i in item_data.get("Results"):
            # {'Pagination': {'Page': 1, 'PageNext': None, 'PagePrev': None, 'PageTotal': 1, 'Results': 1, 'ResultsPerPage': 100, 'ResultsTotal': 1}, 'Results': [{'ID': 7038, 'Icon': '/i/025000/025051.png', 'Name': '庄园蜡', 'Url': '/Item/7038', 'UrlType': 'Item', '_': 'item', '_Score': '45.780636'}], 'SpeedMs': 1}
            item_id = int(i.get("ID"))
            item_name = i.get("Name")
            notice_item_data_dict[item_id]["item_name"] = item_name

        # 推送通知
        for notice_data in notice_item_data_dict.values():
            notice_data: dict
            item_id = notice_data.get("item_id")
            item_name = notice_data.get("item_name") if notice_data.get("item_name") else item_id

            first_world_name = notice_data.get("first_world_name")
            profit = notice_data.get("profit")
            first_item_price_per_unit = notice_data.get("first_item_price_per_unit")
            first_item_quantity = notice_data.get("first_item_quantity")
            average_transaction_price = notice_data.get("average_transaction_price")
            second_item_price_per_unit = notice_data.get("second_item_price_per_unit")
            last_update_time = notice_data.get("last_update_time")

            msg = f"{first_world_name} <{item_name}> 低价通知\n"
            msg += "======================\n"
            msg += f"预计利润: {profit}\n"
            msg += f"最低单价: {first_item_price_per_unit}\n"
            msg += f"物品数量: {first_item_quantity}\n"
            msg += f"价格第二单价: {second_item_price_per_unit}\n"
            msg += f"平均成交单价: {average_transaction_price}\n"
            msg += "======================\n"
            msg += f"更新时间: {last_update_time}\n"

            for group_id in group_list:

                send_msg = SendMsg(
                    from_type="group",
                    group_id=int(group_id),
                    send_messages=Message(MessageData.text(msg)),
                    process_time="该定时功能不记录",
                    time_stamp=int(time.time()),
                )

                # 推送至发送队列
                logger.info(f"调用定时任务功能成功, 推送至发送队列: ROBOT [{admin_robot_id}] - {send_msg}")
                await manager.robot_process_manager.push(admin_robot_id, send_msg)

                time.sleep(1)
