import sys
import time
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.db.utils import OperationalError
from django.core import management
from loguru import logger


# Django启动时会执行的启动钩子
class PostStartConfig(AppConfig):
    name = 'poststart'

    def ready(self):
        check_database_connection()
        perform_db_migrate()
        collect_static()

        scheduler = BackgroundScheduler()
        scheduler.add_job(check_component_status, trigger='interval', seconds=60, coalesce=True, replace_existing=True)
        scheduler.add_job(check_robot_running_status, trigger='interval', seconds=30, coalesce=True, replace_existing=True)
        scheduler.start()


def check_component_status():
    from robot.models import Components

    # 定时检查组件最近健康报告时间, 如果组件超过1分钟没有上报, 则将对应组件的状态更新为离线
    component: Components
    for component in Components.objects.all():
        if component.last_report_time and component.component_status == 1:
            # 都转成秒级时间戳, 进行判断
            last_report_time = int(component.last_report_time.timestamp())
            current_time = int(datetime.datetime.now().timestamp())
            # 间隔时间超过60秒则设为离线, 并保存
            if current_time - last_report_time > 60:
                component.component_status = 0
                component.save()


def check_robot_running_status():
    from robot.models import Components, Robots

    # 更新Robot启动时间

    # 获取所有robot信息和组件的running_msg信息
    robot_objects = Robots.objects.only("admin_user_id", "robot_id", "start_time")
    component_list = Components.objects.filter(component_role=1, component_status=1).only("running_msg")

    robot: Robots
    for robot in robot_objects:
        # 判断Robot目前状态是否正常运行
        # {user_id: {robot_id: 错误信息}, ...}
        robot_running_state = None
        for component in component_list:
            admin_robot_msg = component.running_msg.get(robot.admin_user_id) if component.running_msg else None
            robot_running_state = admin_robot_msg.get(str(robot.robot_id)) if admin_robot_msg else None
            if robot_running_state == "RUNNING":
                break

        if robot.robot_status == 1 and robot_running_state == "RUNNING":
            # 如果正常运行则判断是否有启用时间
            # 如果没有启用时间, 并且组件中有RUNNING状态的, 则更新时间为当前时间, 如果已经有启用时间则跳过更新
            if robot.start_time == None:
                robot.start_time = datetime.datetime.now()
                robot.save()
        else:
            # 将没有正常运行的Bot的启用时间改为None
            if robot.start_time != None:
                robot.start_time = None
                robot.save()


def check_database_connection():
    """检查数据库连接是否可用"""
    for i in range(1, 61):
        logger.info(f"Check database connection: {i}")
        try:
            management.call_command('check', '--database', 'default')
            logger.info("Database connect success")
            return
        except OperationalError:
            logger.info('Database not setup, retry')
        time.sleep(5)
    logger.error("Connection database failed, exit")
    sys.exit(1)


def perform_db_migrate():
    """执行数据库迁移"""
    logger.info("Check database structure change ...")
    logger.info("Migrate model change to database ...")
    try:
        management.call_command('makemigrations')
        management.call_command('migrate')
    except Exception as e:
        logger.error('Perform migrate failed, exit', exc_info=True)
        logger.exception(e)
        sys.exit(11)


def collect_static():
    """采集静态资源"""
    logger.info("Collect static files...")
    try:
        management.call_command('collectstatic', '--no-input', '-c', verbosity=0, interactive=False)
        logger.info("Collect static files done")
    except:
        pass
