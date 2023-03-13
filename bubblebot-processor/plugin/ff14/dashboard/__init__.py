# coding: utf-8

import time
from typing import Union, List
from loguru import logger
from aiocache import cached
from lib.common import httpx_client
from lib.collections import HandleMsg, Message, MessageData
from .data import DATA_CENTER_NAMES, WORLD_NAMES

errors_info = {
    1: "没有找到您指定的大区或服务器!",
    2: "没有找到您指定的物品!",
    3: "请求查询接口时出错, 请稍后重试~",
    4: "没有在交易板上查找到该物品的信息!",
}


@cached(ttl=30)
async def prices(handle_msg: HandleMsg) -> Union[Message, List[Message]]:
    errcode = None

    command_args = handle_msg.command_args
    # 获取要查询的物品的名称
    item_name: str = command_args.get("command_object").get("value")
    # 获取要查询的物品的价格的大区, 如果指定的是大区下的服务器, 则会返回查询的物品的历史价格数据
    world_name: str = command_args.get("world_name").get("value")

    # 判断世界类型, 大区则是:DATA_CENTER, 大区下的服务器则是:WORLD
    if errcode == None:
        if world_name in DATA_CENTER_NAMES:
            world_type = "DATA_CENTER"
            world_name = DATA_CENTER_NAMES.get(world_name)
        elif world_name in WORLD_NAMES:
            world_type = "WORLD"
        else:
            errcode = 1

    # 获取物品ID数据
    if errcode == None:
        try:
            # {'Pagination': {'Page': 1, 'PageNext': None, 'PagePrev': None, 'PageTotal': 1, 'Results': 1, 'ResultsPerPage': 100, 'ResultsTotal': 1}, 'Results': [{'ID': 7038, 'Icon': '/i/025000/025051.png', 'Name': '庄园蜡', 'Url': '/Item/7038', 'UrlType': 'Item', '_': 'item', '_Score': '45.780636'}], 'SpeedMs': 1}
            # 只取1个结果, 所以当使用模糊匹配可能会出现并非想要的物品信息, 所以最好输入完整物品名
            item_search_url = "https://cafemaker.wakingsands.com/search"
            data = {"indexes": "Item", "string": item_name, "limit": 1}
            res = await httpx_client.post(item_search_url, json=data)
            res.raise_for_status()
            item_data: dict = res.json()
        except Exception as e:
            logger.error(f"请求物品id查询接口时出错, 错误信息: {repr(e)}")
            errcode = 3

    # 判断是否有该物品ID, 如果没有获取到返回失败信息
    if errcode == None:
        if item_data.get("Pagination").get("Results") >= 1:
            item_id = item_data["Results"][0]["ID"]
            item_name = item_data["Results"][0]["Name"]
        else:
            errcode = 2

    # 查询物品的交易板数据
    if errcode == None:
        try:
            item_dashboard_query_url = f"https://universalis.app/api/v2/{world_name}/{item_id}"
            res = await httpx_client.get(item_dashboard_query_url)
            res.raise_for_status()
            item_dashboard_data: dict = res.json()
        except Exception as e:
            logger.error(f"请求交易板数据查询接口时出错, 错误信息: {repr(e)}")
            errcode = 3

    # 判断是否有该物品的交易板, 如果没有获取到返回失败信息
    if errcode == None:
        if len(item_dashboard_data.get("listings")) < 1:
            errcode = 4

    # 处理数据结果
    if errcode == None:
        min_price = item_dashboard_data.get("minPrice")
        max_price = item_dashboard_data.get("maxPrice")
        average_transaction_price = int(item_dashboard_data.get("averagePrice"))

        last_update_time = time.localtime(item_dashboard_data.get("lastUploadTime") / 1000)
        last_update_time = time.strftime("%Y-%m-%d %H:%M:%S", last_update_time)

        item_price_listings = sorted(item_dashboard_data.get("listings"), key=lambda x: x['pricePerUnit'])
        item_price_listings = item_price_listings[:10]

        row_separator = "======================\n"
        display_msg = f"{world_name} <{item_name}> 交易板数据如下:\n"
        display_msg += row_separator
        display_msg += f"最低单价: {min_price}\n最高单价: {max_price}\n平均成交单价: {average_transaction_price}\n"
        display_msg += row_separator
        for item_price_data in item_price_listings:
            item_price_data: dict
            price_per_unit = item_price_data.get("pricePerUnit")
            quantity = item_price_data.get("quantity")
            world_name = item_price_data.get("worldName")
            retainer_name = item_price_data.get("retainerName")
            total = item_price_data.get("total")
            display_msg += f"{price_per_unit} x {quantity} = {total}\t"
            if world_type == "DATA_CENTER":
                display_msg += f"{world_name}\n"
            elif world_type == "WORLD":
                display_msg += f"{retainer_name}\n"
        display_msg += row_separator
        display_msg += f"更新时间: {last_update_time}"

        errcode = 0

    if errcode == 0:
        res_msg = Message(MessageData.text(display_msg))
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg