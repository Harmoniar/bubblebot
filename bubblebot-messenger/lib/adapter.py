import json
import asyncio
from socket import gaierror
import websockets
from websockets import client
from loguru import logger
from component.health import update_running_messages


class ClientSocketProtocol:
    def __init__(self, socket_url: str, message_is_json: bool = None, reconnect_times: int = None, reconnect_interval: int = None):
        self.url = socket_url
        self.ws = None

        # If message_is_json is True, the socket will serialize the message using JSON when it receives it.
        self.message_is_json = message_is_json if message_is_json else False
        # Retry connect default 5 times
        self.reconnect_times = reconnect_times if reconnect_times else 5
        # Retry connect interval default 3 seconds
        self.reconnect_interval = reconnect_interval if reconnect_interval else 3

    async def run(self):
        reconnect_count = 1
        while 1:
            try:
                self.ws = await client.connect(self.url, open_timeout=5)
                reconnect_count = 1
                await self.on_open()

                async for message in self.ws:
                    message = json.loads(message) if self.message_is_json else message
                    await self.on_message(message)

            except websockets.ConnectionClosed:
                await self.on_close(reconnect_count)
                if reconnect_count <= self.reconnect_times:
                    reconnect_count += 1
                    await asyncio.sleep(self.reconnect_interval)
                else:
                    break

            except ConnectionRefusedError:
                await self.on_refused(reconnect_count)
                if reconnect_count <= self.reconnect_times:
                    reconnect_count += 1
                    await asyncio.sleep(self.reconnect_interval)
                else:
                    break

            except Exception as e:
                await self.on_exception(e)
                break

    async def on_message(self, message):
        pass

    async def on_open(self):
        pass

    async def on_close(self, reconnect_count: int):
        pass

    async def on_refused(self, reconnect_count: int):
        pass

    async def on_exception(self, error):
        pass


class BotWebSocket(ClientSocketProtocol):
    def __init__(self, admin_robot_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_robot_id = admin_robot_id
        self.admin_id, self.robot_id = admin_robot_id.rsplit(":", 1)

    async def on_open(self):
        logger.info(f"ROBOT [{self.admin_robot_id}] socket connect success.")
        update_running_messages(self.admin_id, self.robot_id, "RUNNING")

    async def on_close(self, reconnect_count: int):
        if reconnect_count <= 5:
            logger.warning(f"ROBOT [{self.admin_robot_id}] socket disconnect, try to reconnect for the {reconnect_count} times...")
        else:
            logger.warning(f"ROBOT [{self.admin_robot_id}] socket reconnect failed, it's been reconnected {reconnect_count - 1} times, abort reconnection.")
            update_running_messages(self.admin_id, self.robot_id, "与协议端断开连接, 重试连接5次仍然失败, 放弃重试")

    async def on_refused(self, reconnect_count: int):
        if reconnect_count <= 5:
            logger.warning(f"ROBOT [{self.admin_robot_id}] socket connect refused, try to reconnect for the {reconnect_count} times...")
        else:
            logger.warning(f"ROBOT [{self.admin_robot_id}] socket connect refused, it's been reconnected {reconnect_count - 1} times, abort reconnection.")
            update_running_messages(self.admin_id, self.robot_id, "连接协议端失败, 协议端积极拒绝连接")

    async def on_exception(self, error):
        if isinstance(error, gaierror):
            logger.error(f"ROBOT [{self.admin_robot_id}] socket get connection address failed, please check your domain name, or use ip instead of domain name.")
            update_running_messages(self.admin_id, self.robot_id, "连接协议端失败, 无法解析域名地址, 请尝试使用IP作为协议端地址")
        else:
            logger.error(f"ROBOT [{self.admin_robot_id}] socket connect failed, connect error: {repr(error)}")
            update_running_messages(self.admin_id, self.robot_id, f"连接协议端失败, 报错信息: {repr(error)}")
