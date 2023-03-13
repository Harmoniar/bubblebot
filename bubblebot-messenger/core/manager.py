from asyncio import AbstractEventLoop
from aredis import StrictRedis
from loguru import logger
from component import cache, health
from lib.conf import CONFIG
from .gocqhttp import GocqHttpReceiver, GocqHttpTransmitter

"""
多进程的实现方式:
假设有两个进程, 一个进程拿到了消息, 进行简单判断之后
如果符合消费条件, 则通过redis集合判断是否存在该消息ID, 如果如果存在则直接跳过, 如果不存在则立马将消息ID将其放入redis集合中, 同时判断插入结果, 且插入的ID过期过期时间为5秒,
如果插入返回成功, 则说明是这个进程插入的, 如果插入失败, 则表示可能已经被其他进程插入了
"""


class RobotTaskManager:
    def __init__(self, loop: AbstractEventLoop, redis_connect: StrictRedis, process_queue_name: str, sentbuf_queue_name: str, msg_expire_time: int):
        self.loop = loop
        self.redis_connect = redis_connect
        self.process_queue_name = process_queue_name
        self.sentbuf_queue_name = sentbuf_queue_name
        self.msg_expire_time = msg_expire_time

        # {"admin_robot_id": {...}}
        self.robot_config = {}
        # {"admin_robot_id": {"task_type": task_object,...}}
        self.robot_tasks = {}

    # ========================= cancel robot task ==========================
    async def close_robots(self, current_robots_config: dict):

        # 筛选出已经存在在任务字典中, 但是最新的配置文件已经没有的任务, 通过循环关闭这些任务, 然后从任务字典中删除它们
        not_exist_robots: list = [admin_robot_id for admin_robot_id in self.robot_tasks.keys() if admin_robot_id not in current_robots_config]
        for admin_robot_id in not_exist_robots:
            await self._close_robot_task(admin_robot_id)
            logger.warning(f"robot [{admin_robot_id}] alrealy not exist in current_robots_config, close it.")

    async def _close_robot_task(self, admin_robot_id):
        if self.robot_tasks.get(admin_robot_id):
            res_list = []
            for task in self.robot_tasks.get(admin_robot_id):
                res_list.append(task.cancel())
            self.robot_tasks.pop(admin_robot_id, None)
            self.robot_config.pop(admin_robot_id, None)
            if all(res_list):
                logger.info(f"ROBOT [{admin_robot_id}] task cancelled.")
            else:
                logger.error(f"ROBOT [{admin_robot_id}] task cancel failed.")

    # ===================== close updated robot task =======================
    async def close_update_robots(self, current_robots_config: dict):

        # 获取同时存在robots配置和任务字典中的admin_robot_id
        intersect_robots: list = [admin_robot_id for admin_robot_id in current_robots_config if admin_robot_id in self.robot_tasks]

        # 检查配置是否有改变, 有的话则删除旧的, 并创建新的
        for admin_robot_id in intersect_robots:

            # 获取任务字典中的配置和缓存中的配置
            robot_task_config = self.robot_config.get(admin_robot_id)
            robot_cache_config = current_robots_config.get(admin_robot_id)

            # 如果两个配置不相等, 说明配置有更新过, 则删除旧任务, 等create_robots一起创建新任务
            if robot_task_config != robot_cache_config:
                logger.warning(f"ROBOT [{admin_robot_id}] config alrealy update, will reload it.")
                await self._close_robot_task(admin_robot_id)

    # ========================= create robot task =========================
    async def create_robots(self, current_robots_config: dict):

        # 获取存在robots_config中, 但是不存在于task任务列表中的admin_robot_id
        reqire_create_robots: list = [admin_robot_id for admin_robot_id in current_robots_config if admin_robot_id not in self.robot_tasks]

        for admin_robot_id in reqire_create_robots:
            robot_data: dict = current_robots_config[admin_robot_id]
            self.robot_config[admin_robot_id] = robot_data
            # 1: GOCQ-HTTP
            if robot_data.get("protocol_server_mode") == 1:
                protocol_config = robot_data.get("protocol_server_config")
                # 创建Socket并将其添加进任务
                gocqhttp_receiver = GocqHttpReceiver(
                    socket_url="ws://{}:{}/".format(protocol_config.get("socket_host"), protocol_config.get("socket_port")),
                    admin_robot_id=admin_robot_id,
                    robot_config=robot_data,
                    redis_connect=self.redis_connect,
                    process_queue_name=self.process_queue_name,
                )
                await self._create_robot_task(admin_robot_id, "receiver", gocqhttp_receiver.run())
                # 添加接收器并添加进任务
                transmitter = GocqHttpTransmitter(
                    receiver=gocqhttp_receiver,
                    loop=self.loop,
                    admin_robot_id=admin_robot_id,
                    redis_connect=self.redis_connect,
                    sentbuf_queue_name=f"{self.sentbuf_queue_name}:{admin_robot_id}",
                    msg_expire_time=self.msg_expire_time,
                )
                await self._create_robot_task(admin_robot_id, "transmitter", transmitter.run())

    async def _create_robot_task(self, admin_robot_id, component_type, coro):
        # 创建任务, 并将任务对象插入robot_tasks用于后续管理
        task_obj = self.loop.create_task(coro)
        if not self.robot_tasks.get(admin_robot_id):
            self.robot_tasks[admin_robot_id] = []
        self.robot_tasks[admin_robot_id].append(task_obj)
        logger.info(f"ROBOT [{admin_robot_id}] - {component_type} added to task.")

    # ========================= get robot config =========================
    async def _get_robots_config(self, robots_config_list: list) -> dict:
        robots_config = {}

        # 排除协议端参数不符合要求的robot
        for robot in robots_config_list:
            robot_error = None

            # 判断协议端类型是否为空
            if robot_error == None:
                if robot.get('protocol_server_mode') == 0:
                    robot_error = "机器人协议端类型不能为空"

            # 判断协议端参数是否为空
            if robot_error == None:
                required_fields = ("socket_host", "socket_port")
                protocol_server_config = robot.get('protocol_server_config')
                if not protocol_server_config:
                    robot_error = "机器人协议端参数不能为空"

            # 判断协议端参数是否完整
            if robot_error == None:
                if not all(i in required_fields for i in protocol_server_config):
                    robot_error = "机器人协议端参数不完整"

            # 如果有问题则添加到errors字典中, 用于更新健康上报时的信息
            if robot_error:
                health.update_running_messages(robot.get('admin_user_id'), robot.get('robot_id'), robot_error)
            # 都没问题则添加到配置字典, 尝试进行启动
            else:
                robots_config[f"{robot.get('admin_user_id')}:{robot.get('robot_id')}"] = robot

        return robots_config

    async def reload_settings(self):
        current_robots_config = await self._get_robots_config(cache.robots)
        await self.close_robots(current_robots_config)
        await self.close_update_robots(current_robots_config)
        await self.create_robots(current_robots_config)

    async def run_server(self):
        await self.reload_settings()


robot_task_manager: RobotTaskManager = None


def manager_setup(loop: AbstractEventLoop):
    global robot_task_manager
    robot_task_manager = RobotTaskManager(loop, cache.redis_connect, CONFIG.PROCESS_QUEUE_NAME, CONFIG.SENTBUF_QUEUE_NAME, CONFIG.MSG_EXPIRE_TIME)
    return robot_task_manager
