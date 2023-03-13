import os
import sys
from .conf import CONFIG, PROJECT_DIR
from loguru import logger

# 日志配置
log_format = "<magenta>{time:YYYY-MM-DD HH:mm:ss:SSS}</magenta> | <light-yellow><{name}</light-yellow>:<light-yellow>{function}</light-yellow>:<light-yellow>{line}></light-yellow> | <level>[{level}]</level> -> <level>{message}</level>"

# 去掉默认的Handler，并添加自己的Handler
logger.remove(handler_id=0)
logger.add(
    os.path.join(PROJECT_DIR, CONFIG.LOG_DIR, "app.log"),
    format=log_format,
    level="DEBUG",
    rotation="5 MB",
    retention="15 days",
    compression="gz",
    colorize=False,
    enqueue=True,
    encoding="utf-8",
)
logger.add(sys.stdout, format=log_format, level=CONFIG.LOG_LEVEL, colorize=True, enqueue=True)

if __name__ == "__main__":
    logger.debug("This is Test Debug!")
    logger.info("This is Test Info!")
    logger.success("This is Test Success!")
    logger.error("This is Test Error!")
