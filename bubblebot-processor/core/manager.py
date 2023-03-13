import pickle
import asyncio
from asyncio import AbstractEventLoop
from aredis import StrictRedis
from loguru import logger
from .filter import MessageFilterMixin
from .handler import MessageHandlerMinxin
from lib.conf import CONFIG
from lib.collections import ReceiveMsg, SendMsg
from component.cache import redis_connect


class RobotProcessManager(MessageFilterMixin, MessageHandlerMinxin):
    def __init__(self, loop: AbstractEventLoop, redis_connect: StrictRedis, process_queue_name: str, sentbuf_queue_name: str, msg_expire_time: int):
        self.loop = loop
        self.redis_connect = redis_connect
        self.process_queue_name = process_queue_name
        self.sentbuf_queue_name = sentbuf_queue_name
        self.msg_expire_time = msg_expire_time

    # ================== redis pop message ===================
    async def pop(self, timeout: int = 30):
        message = await self.redis_connect.blpop(self.process_queue_name, timeout=timeout)
        if message:
            receive_msg = pickle.loads(message[1])
        else:
            raise TimeoutError("Pop the queue timeout.")
        return receive_msg

    # ================== redis push message ===================
    async def push(self, admin_robot_id: str, send_msg: SendMsg):
        # 放入处理队列
        try:
            queue_name = f"{self.sentbuf_queue_name}:{admin_robot_id}"
            send_msg_data = pickle.dumps(send_msg)
            await self.redis_connect.rpush(queue_name, send_msg_data)
        except Exception as e:
            logger.error(f"消息推送至队列出错, 错误信息: {repr(e)}")
            logger.exception(e)

    # =================== message process ====================
    async def process(self, receive_msg: ReceiveMsg):
        # 过滤过期消息
        if await self.is_expire_message(receive_msg, self.msg_expire_time):
            logger.debug(f"从队列中取出消息, 但消息已经过期不再处理: ROBOT [{receive_msg.admin_robot_id}] - {receive_msg}")
            return

        # 过滤无效机器人
        if await self.is_invalid_robot(receive_msg):
            logger.debug(f"从队列中取出消息, 但缓存配置不存在该ROBOT不再处理: ROBOT [{receive_msg.admin_robot_id}] - {receive_msg}")
            return

        logger.info(f"收到消息, 准备进行处理: ROBOT [{receive_msg.admin_robot_id}] - {receive_msg}")

        # 判断是否触发命令, 并生成handle消息
        handle_msg = await self.handle_message(receive_msg)
        if not handle_msg.is_trigger:
            logger.debug(f"消息未触发命令, 不再处理: ROBOT [{receive_msg.admin_robot_id}] - {handle_msg}")
            return

        # 判断用户是否有handle_msg中的功能执行权限
        if await self.is_permission_denied(handle_msg):
            logger.debug(f"消息处理完毕, 但用户没有功能权限, 不再处理: ROBOT [{handle_msg.receive_msg.admin_robot_id}] - {handle_msg}")
            return

        logger.debug(f"消息处理完毕, 准备调用功能: ROBOT [{receive_msg.admin_robot_id}] - {handle_msg}")

        # 调用功能
        send_msg = await self.handle_call_function(handle_msg)
        if not send_msg.is_called:
            return

        logger.info(f"调用功能成功, 推送至发送队列: ROBOT [{receive_msg.admin_robot_id}] - {send_msg}")
        # 推送send_msg对象到队列
        await self.push(receive_msg.admin_robot_id, send_msg)

    # ===================== run server =======================
    async def run_server(self):
        while 1:
            # 取出消息
            try:
                receive_msg: ReceiveMsg = await self.pop()
            except TimeoutError:
                continue
            except Exception as e:
                logger.error(f"从队列获取消息失败, 错误信息: {repr(e)}")
                logger.exception(e)
                await asyncio.sleep(3)
                continue

            logger.debug(f"从队列中取出消息: ROBOT [{receive_msg.admin_robot_id}] - {receive_msg}")

            # 进行处理
            self.loop.create_task(self.process(receive_msg))


robot_process_manager: RobotProcessManager = None


def manager_setup(loop: AbstractEventLoop):
    global robot_process_manager
    robot_process_manager = RobotProcessManager(loop, redis_connect, CONFIG.PROCESS_QUEUE_NAME, CONFIG.SENTBUF_QUEUE_NAME, CONFIG.MSG_EXPIRE_TIME)
    return robot_process_manager
