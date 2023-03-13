import time
from loguru import logger
from core import manager
from lib.collections import SendMsg, Message, MessageData


async def test(admin_robot_id: str, timing_config: dict):

    group_list = timing_config.get("group")

    for group_id in group_list:
        start_time = time.time()

        # 生成发送消息
        send_msg = SendMsg(
            from_type="group",
            group_id=int(group_id),
            send_messages=Message(MessageData.text("Hello, World!")),
            process_time="{:.3f}s".format(time.time() - start_time),
            time_stamp=int(time.time()),
        )

        # 推送至发送队列
        logger.info(f"调用定时任务功能成功, 推送至发送队列: ROBOT [{admin_robot_id}] - {send_msg}")
        await manager.robot_process_manager.push(admin_robot_id, send_msg)
