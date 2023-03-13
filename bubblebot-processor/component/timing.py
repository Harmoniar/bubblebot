import importlib
from loguru import logger
from lib.common import scheduler
from component import cache

# timing_task = {"295983086@qq.com:295983086:timing_function_name": {}, ...}
timing_tasks = {}


def get_cron_time(cron: str) -> dict:
    cron = cron.strip()
    cron_time = {}
    keywords = ["minute", "hour", "day", "month", "day_of_week", "second"]
    var = cron.split()
    for k, v in zip(keywords, var):
        if k == "day_of_week" and v.isdigit():
            v = str(int(v) - 1)
        cron_time[k] = v
    return cron_time


async def close_not_exist_timings(current_timings_config: dict):
    # 筛选出已经存在于timing_task字典中, 但是最新的定时任务配置已经没有的任务
    not_exist_timings: list = [admin_robot_timing_id for admin_robot_timing_id in timing_tasks.keys() if admin_robot_timing_id not in current_timings_config]

    # 通过循环关闭这些任务, 并从任务字典中删除它们
    for admin_robot_timing_id in not_exist_timings:
        try:
            scheduler.remove_job(admin_robot_timing_id)
            timing_tasks.pop(admin_robot_timing_id)
        except Exception as e:
            logger.error(f"删除已关闭的BOT定时任务时出错, 错误信息: {repr(e)}")


async def close_update_timings(current_timings_config: dict):
    # 获取同时存在timing_task字典和最新定时任务配置中的配置
    intersect_timings: list = [admin_robot_timing_id for admin_robot_timing_id in current_timings_config if admin_robot_timing_id in timing_tasks]

    # 然后循环检查配置是否有改变, 有的话则删除旧的, 并创建新的
    for admin_robot_timing_id in intersect_timings:

        # 获取任务字典中的配置和缓存中的配置
        cache_timing_config = timing_tasks.get(admin_robot_timing_id)
        current_timing_config = current_timings_config.get(admin_robot_timing_id)

        # 如果两个配置不相等, 说明配置有更新过, 则删除旧任务, 等创建时一起创建新任务
        if cache_timing_config != current_timing_config:
            try:
                scheduler.remove_job(admin_robot_timing_id)
                timing_tasks.pop(admin_robot_timing_id)
            except Exception as e:
                logger.error(f"删除已更新的BOT定时任务时出错, 错误信息: {repr(e)}")


async def create_timings(current_timings_config: dict):
    # 获取存在最新定时任务配置中，但是timing_task中没有的定时任务
    reqire_create_timing_tasks: list = [admin_robot_timing_id for admin_robot_timing_id in current_timings_config if admin_robot_timing_id not in timing_tasks]

    # 添加进timing_task字典，并创建定时任务
    for admin_robot_timing_id in reqire_create_timing_tasks:

        try:
            timing_task_config: dict = current_timings_config.get(admin_robot_timing_id)

            # 获取功能对象
            timing_function_url: str = timing_task_config.get("timing_function__timing_function_url")

            # 尝试以timing为根路径
            if not timing_function_url.startswith("timing."):
                timing_function_url = f"timing.{timing_function_url}"

            # 通过反射获取功能函数对象
            module_path, function_name = timing_function_url.rsplit('.', 1)
            module = importlib.import_module(module_path)
            function_object = getattr(module, function_name)

            # 获取cron时间
            cron_time = get_cron_time(timing_task_config.get("timing_cron"))

            admin_user_id = timing_task_config.get("admin_user_id")
            robot_id = timing_task_config.get("robot_id")
            admin_robot_id = f"{admin_user_id}:{robot_id}"
            timing_config = timing_task_config.get("timing_function_config")

            scheduler.add_job(
                id=admin_robot_timing_id,
                func=function_object,
                args=(admin_robot_id, timing_config),
                trigger="cron",
                **cron_time,
                coalesce=True,
                replace_existing=True,
            )
            # 添加进timing_tasks字典
            timing_tasks[admin_robot_timing_id] = timing_task_config

        except Exception as e:
            logger.error(f"创建BOT定时任务时出错, 错误信息: {repr(e)}")


async def sync_robot_timing():
    current_timings_config = cache.robot2timing
    await close_not_exist_timings(current_timings_config)
    await close_update_timings(current_timings_config)
    await create_timings(current_timings_config)
