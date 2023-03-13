import asyncio
from component.poststart import poststart
from core.manager import manager_setup
from loguru import logger

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    loop.run_until_complete(poststart())
    robot_process_manager = manager_setup(loop)
    loop.create_task(robot_process_manager.run_server())
    logger.catch(loop.run_forever)()