import time
import json
import pickle
import asyncio
from asyncio import AbstractEventLoop
from loguru import logger
from aredis import StrictRedis
from lib.collections import ReceiveMsg, SendMsg
from lib.adapter import BotWebSocket


class GocqHttpReceiver(BotWebSocket):
    def __init__(
        self,
        socket_url: str,
        admin_robot_id: str,
        robot_config: dict,
        redis_connect: StrictRedis,
        process_queue_name: str,
        reconnect_times: int = None,
        reconnect_interval: int = None,
    ):
        super().__init__(
            admin_robot_id=admin_robot_id,
            socket_url=socket_url,
            message_is_json=True,
            reconnect_times=reconnect_times,
            reconnect_interval=reconnect_interval,
        )

        self.robot_config = robot_config
        self.redis_connect = redis_connect
        self.process_queue_name = process_queue_name

        self.filter_post_types = ["meta_event"]
        self.event_message_routes = {
            "message": self.message_handler,
            "*": self.all_event_handler,
        }

    # ===================== event message route ======================
    async def on_message(self, message: dict):
        if message.get("post_type") in self.filter_post_types:
            return

        for type_name in self.event_message_routes.keys():
            if message.get("post_type") == type_name:
                await self.event_message_routes.get(type_name)(message)
                return

        if "*" in self.event_message_routes:
            await self.event_message_routes.get("*")(message)
            return

    # ===================== message handler =========================

    async def group_filter(self, message: dict):
        group_id = message.get("group_id")
        # 获取群权限管理模式 (1.白名单 / 2.黑名单)
        group_permit_mode = self.robot_config.get("group_permit_mode")
        # 白名单模式: 群不在白名单排除
        if group_permit_mode == 1:
            if group_id not in self.robot_config.get("group_whitelist"):
                return 1
        # 黑名单模式: 群在黑名单排除
        elif group_permit_mode == 2:
            if group_id in self.robot_config.get("group_blacklist"):
                return 1

    async def simple_filter(self, message_type: str, message: dict):
        errcode = None

        listen_msg_type = self.robot_config.get("listen_msg_type")
        if (message_type == "group") and (1 not in listen_msg_type):
            errcode = 1
        elif (message_type == "private") and (2 not in listen_msg_type):
            errcode = 1

        if errcode == None:
            if message_type == "group":
                errcode = await self.group_filter(message)

        if errcode == None:
            # 排除黑名单用户
            if message.get("user_id") in self.robot_config.get("user_blacklist"):
                errcode = 1

        if errcode == None:
            # 排除机器人自己
            if message.get("user_id") == self.robot_id:
                errcode = 1

        if errcode == None:
            errcode = 0

        return errcode

    async def message_handler(self, message: dict):
        # 1.群消息 2.好友消息
        # ===================== group message ======================
        if message.get("message_type") == "group":
            # 简单过滤消息
            if await self.simple_filter("group", message) != 0:
                return
            # 生成消息对象
            receive_msg = ReceiveMsg.convert_gocqhttp(self.admin_id, self.robot_id, message)
            logger.info(f"ROBOT [{self.admin_robot_id}] - 收到群组消息: {receive_msg}")
            await self.push(receive_msg)

        # ==================== private message =====================
        elif message.get("message_type") == "private":
            # 简单过滤消息
            if await self.simple_filter("private", message) != 0:
                return
            # 生成消息对象
            receive_msg = ReceiveMsg.convert_gocqhttp(self.admin_id, self.robot_id, message)
            logger.info(f"ROBOT [{self.admin_robot_id}] - 收到私聊消息: {receive_msg}")
            await self.push(receive_msg)

    # =================== all event handler ========================
    async def all_event_handler(self, message: dict):
        logger.debug(f"ROBOT [{self.admin_robot_id}] - 收到未路由分发消息: {message}")

    # ================== push to redis queue =======================
    async def push(self, receive_msg: ReceiveMsg):
        # 放入处理队列
        try:
            receive_msg_data = pickle.dumps(receive_msg)
            await self.redis_connect.rpush(self.process_queue_name, receive_msg_data)
            logger.debug(f"ROBOT [{self.admin_robot_id}] - 消息推送至队列成功: {receive_msg}")
        except Exception as e:
            logger.error(f"ROBOT [{self.admin_robot_id}] - 消息推送至队列出错, 错误信息: {repr(e)}")
            logger.exception(e)


class GocqHttpTransmitter:
    def __init__(self, receiver: GocqHttpReceiver, loop: AbstractEventLoop, admin_robot_id: str, redis_connect: StrictRedis, sentbuf_queue_name: str, msg_expire_time: int):
        self.receiver = receiver
        self.loop = loop
        self.admin_robot_id = admin_robot_id
        self.redis_connect = redis_connect
        self.sentbuf_queue_name = sentbuf_queue_name
        self.msg_expire_time = msg_expire_time

    # ================== redis pop message ===================
    async def pop(self, timeout: int = 30):
        message = await self.redis_connect.blpop(self.sentbuf_queue_name, timeout=timeout)
        if message:
            receive_msg = pickle.loads(message[1])
        else:
            raise TimeoutError("Pop the queue timeout.")
        return receive_msg

    # ===================== send message =====================
    async def sendmsg(self, send_msg: SendMsg):
        for messages in send_msg.send_messages:
            try:
                data = {"message_type": send_msg.from_type, "user_id": send_msg.user_id, "group_id": send_msg.group_id, "message": messages.message_data}
                data = {"action": "send_msg", "params": data}
                await self.receiver.ws.send(json.dumps(data))
                logger.info(f"ROBOT [{self.admin_robot_id}] - 消息发送成功: {data}")
            except Exception as e:
                logger.error(f"ROBOT [{self.admin_robot_id}] - 消息发送至协议端出错, 错误信息: {repr(e)}")
                logger.exception(e)

    # 判断收到消息的延迟时间是否超过失效时间, 超过直接丢掉
    async def is_expire_message(self, send_msg: SendMsg, msg_expire_time: int) -> bool:
        receive_delay = int(time.time()) - send_msg.time_stamp
        if receive_delay > msg_expire_time:
            logger.debug(f"从队列中取出消息, 但消息已经过期不再处理: ROBOT [{self.admin_robot_id}] - {send_msg}")
            return True
        else:
            return False

    # ===================== run server =======================
    async def run(self):
        while 1:
            # 取出消息
            try:
                send_msg: SendMsg = await self.pop()
            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"ROBOT [{self.admin_robot_id}] - 从队列获取消息失败, 错误信息: {repr(e)}")
                logger.exception(e)
                await asyncio.sleep(3)
                continue

            # 排除已过期消息
            if await self.is_expire_message(send_msg, self.msg_expire_time):
                return

            logger.debug(f"ROBOT [{self.admin_robot_id}] - 收到待发送消息: {send_msg} - {send_msg}")
            # 进行发送
            self.loop.create_task(self.sendmsg(send_msg))
