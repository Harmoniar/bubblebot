import os
import asyncio
from lib.common import scheduler
from lib.logger import logger
from lib.conf import CONFIG
from component import cache, health, timing


sync_args = [
    {
        "keys": ("admin_user_id", "robot_id"),
        "model_name": "Robots",
        "filter_conditions": {'robot_status': 1},
        "fields": [
            "admin_user_id",
            "robot_id",
            "robot_name",
            "master_id",
            "trigger_mode",
            "command_prefix",
            "user_function_permit",
            "comment",
        ],
    },
    {
        "keys": ("admin_user_id", "robot_id", "function_id"),
        "model_name": "Robot2Function",
        "filter_conditions": {'robot__robot_status': 1, 'function_status': 1, 'function__global_function_status': 1},
        "fields": [
            "admin_user_id",
            "robot_id",
            "function_id",
            "function__function_name",
            "function__function_url",
            "function__function_class",
            "function__explain",
            "trigger_command",
            "command_args",
            "trigger_template",
            "exception_template",
        ],
    },
    {
        "keys": ("admin_user_id", "robot_id", "timing_function_id"),
        "model_name": "Robot2Timing",
        "filter_conditions": {'robot__robot_status': 1, 'timing_status': 1, 'timing_function__global_function_status': 1},
        "fields": [
            "admin_user_id",
            "robot_id",
            "timing_function_id",
            "timing_function__timing_function_name",
            "timing_function__timing_function_url",
            "timing_function__timing_function_class",
            "timing_function__explain",
            "timing_cron",
            "timing_function_config",
        ],
    },
]


async def timing_task():
    # 定时同步最新数据到缓存
    for args in sync_args:
        await cache.sync_cache(**args)

    # 定时上报组件状态
    await health.health_report()

    # 定时更新BOT定时任务
    await timing.sync_robot_timing()

    logger.success("Main timing task execution succeeded.")


async def first_sync_cache(keys: list, model_name: str, filter_conditions: dict, fields: list = None):
    var_name = model_name.lower()
    for i in range(1, 61):
        errcode = await cache.sync_cache(keys, model_name, filter_conditions, fields)
        if errcode == 0:
            logger.success(f"First sync {var_name} cache success.")
            return
        else:
            logger.warning(f"First sync {var_name} cache failed, will try resync again: {i}")
        await asyncio.sleep(5)

    logger.error(f"First sync {var_name} cache failed, it's been tried resync 60 times, exit.")
    await asyncio.sleep(1)
    os._exit(1)


async def poststart():
    logger.info("Starting...")

    # 创建tmp目录
    try:
        os.makedirs("tmp")
    except:
        pass

    for args in sync_args:
        await first_sync_cache(**args)

    await timing.sync_robot_timing()

    scheduler.add_job(timing_task, trigger='interval', seconds=CONFIG.BASE_TIMING_INTERVAL, coalesce=True, replace_existing=True)
    scheduler.start()
