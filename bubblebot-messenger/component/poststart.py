import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from lib.logger import logger
from lib.conf import CONFIG
from component import cache, health
from core import manager


async def timing_task():
    await cache.sync_cache()
    await manager.robot_task_manager.reload_settings()
    await health.health_report()
    logger.success("Timing task execution succeeded.")


async def first_sync_cache():
    for i in range(1, 61):
        errcode = await cache.sync_cache()
        if errcode == 0:
            logger.success("First sync cache success.")
            return
        else:
            logger.warning(f"First sync cache failed, will try resync again: {i}")
        await asyncio.sleep(5)

    logger.error(f"First sync cache failed, it's been tried resync 60 times, exit.")
    await asyncio.sleep(1)
    os._exit(1)


async def poststart():
    logger.info("Starting...")

    await first_sync_cache()

    scheduler = AsyncIOScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(timing_task, trigger='interval', seconds=CONFIG.BASE_TIMING_INTERVAL, coalesce=True, replace_existing=True)
    scheduler.start()
