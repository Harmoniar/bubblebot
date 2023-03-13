import time
from loguru import logger
from component import cache
from lib.collections import ReceiveMsg, HandleMsg


class MessageFilterMixin:

    # 判断收到消息的延迟时间是否超过失效时间, 超过直接丢掉
    async def is_expire_message(self, receive_msg: ReceiveMsg, message_expiration_time: int) -> bool:
        receive_delay = int(time.time()) - receive_msg.time_stamp
        if receive_delay > message_expiration_time:
            return True
        else:
            return False

    async def is_invalid_robot(self, receive_msg: ReceiveMsg) -> bool:
        if receive_msg.admin_robot_id not in cache.robots:
            return True
        else:
            return False

    async def is_permission_denied(self, handle_msg: HandleMsg) -> bool:
        # 达成允许条件直接返回False, 其他不在列的情况返回True表示拒绝

        user_id = handle_msg.receive_msg.user_id
        admin_robot_id = handle_msg.receive_msg.admin_robot_id
        function_id = handle_msg.function_id
        function_class = handle_msg.function_class

        robot_config: dict = cache.robots.get(admin_robot_id)
        master_list = robot_config.get("master_id")
        user_function_permit_list = robot_config.get("user_function_permit")

        # 如果调用者是master则允许
        if user_id in master_list:
            return False

        # 如果功能在默认权限列表则允许
        if function_id in user_function_permit_list:
            return False

        # 如果默认权限中含ALL、并且调用的功能并非管理员功能则允许
        if "ALL" in user_function_permit_list and function_class != "admin":
            return False

        # 其他情况则拒绝
        return True
