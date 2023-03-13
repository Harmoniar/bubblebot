# /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import platform
from loguru import logger
from apps.core.conf import CONFIG

# 当前路径的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Django Project项目路径
APP_DIR = os.path.join(BASE_DIR, 'apps')
# 添加Django Project路径插入到文件查找列表中
sys.path.insert(0, APP_DIR)
# 指定Django要使用的配置文件路径, 通过环境变量进行配置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# 创建程序需要的静态文件目录
for path in (CONFIG.LOG_DIR, "data/static", "data/media"):
    try:
        os.makedirs(os.path.join(CONFIG.PROJECT_DIR, path))
    except:
        pass


def start_services():
    bind = f"{CONFIG.HTTP_HOST}:{CONFIG.HTTP_PORT}"
    try:
        # 如果是Windows系统则使用Django自带的wsgi启动Web服务
        if platform.system().lower() == 'windows':
            import django
            from django.core import management

            django.setup()
            management.call_command('runserver', (bind, "--noreload"))

        # 如果是Linux系统则使用gunicorn启动Web服务
        elif platform.system().lower() == 'linux':
            wsgi = "core.wsgi:application"
            workers = "--workers={}".format(CONFIG.WORKERS)
            threads = "--threads={}".format(CONFIG.THREADS)
            worker_connections = "--worker-connections={}".format(CONFIG.WORKER_CONNECTIONS)
            worker_dir = "--chdir=./apps"
            bind_args = ("-b", bind)

            os.system(" ".join(('gunicorn', wsgi, workers, threads, worker_connections, worker_dir, *bind_args)))

    except KeyboardInterrupt:
        logger.info('Cancel ...')
        time.sleep(2)
    except Exception as e:
        logger.error(f"Start service error: {repr(e)}")
        logger.exception(e)
        time.sleep(2)


if __name__ == '__main__':
    start_services()
