import os
import sys
from django.urls import reverse_lazy
from .conf import BASE_DIR, PROJECT_DIR, CONFIG
from loguru import logger


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = BASE_DIR
PROJECT_DIR = PROJECT_DIR
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = CONFIG.SECRET_KEY
API_KEY = CONFIG.API_KEY.encode('UTF-8')

# DEBUG
DEBUG = CONFIG.DEBUG

# LOG LEVEL
LOG_LEVEL = CONFIG.LOG_LEVEL

ALLOWED_HOSTS = ["*"]


# Application definition
INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'admin.apps.AdminConfig',
    'robot.apps.RobotConfig',
    'poststart.PostStartConfig',
]

MIDDLEWARE = [
    'core.middleware.log.LogMiddle',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {'environment': 'core.jinja2.environment'},
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': CONFIG.DB_HOST,
        'PORT': CONFIG.DB_PORT,
        'USER': CONFIG.DB_USER,
        'PASSWORD': CONFIG.DB_PASSWORD,
        'NAME': CONFIG.DB_NAME,
        'CHARSET': 'utf8',
        # 开启严格模式
        'DB_OPTIONS': {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# I18N translation
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_DIR, 'data/static')
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'data/media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# users model
AUTH_USER_MODEL = 'admin.Users'

# login
LOGIN_REDIRECT_URL = reverse_lazy('admin_home')
LOGIN_URL = reverse_lazy('admin_login')

# Redis
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': f'redis://{CONFIG.REDIS_HOST}:{CONFIG.REDIS_PORT}/{CONFIG.REDIS_DB}',
#         'TIMEOUT': None,
#         'OPTIONS': {
#             "PASSWORD": CONFIG.REDIS_PASSWORD,
#             "REDIS_CLIENT_KWARGS": {"health_check_interval": 30},
#             "CONNECTION_POOL_KWARGS": {"max_connections": 100},
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#             "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
#         },
#     }
# }

# 关闭默认日志输出
if not DEBUG:
    LOGGING = {'version': 1, 'disable_existing_loggers': True}

    # # 打印ORM模型SQL
    # LOGGING = {
    #     'version': 1,
    #     'disable_existing_loggers': False,
    #     'formatters': {
    #         'simple': {'format': '[%(asctime)s] %(message)s'},
    #     },
    #     'handlers': {
    #         'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'simple'},
    #     },
    #     'loggers': {
    #         'django': {
    #             'handlers': ['console'],
    #             'level': 'DEBUG',
    #         },
    #     },
    # }


# 日志配置
log_format = "<magenta>{time:YYYY-MM-DD HH:mm:ss:SSS}</magenta> <light-yellow><{name}</light-yellow>:<light-yellow>{function}</light-yellow>:<light-yellow>{line}></light-yellow> <level>[{level}]</level> -> <level>{message}</level>"

# 去掉默认的Handler，并添加自己的Handler
logger.remove(handler_id=0)
logger.add(
    os.path.join(PROJECT_DIR, CONFIG.LOG_DIR, "app.log"),
    format=log_format,
    level="INFO",
    rotation="5 MB",
    retention="15 days",
    compression="gz",
    colorize=False,
    enqueue=True,
    encoding="utf-8",
)
logger.add(sys.stdout, format=log_format, level="INFO", colorize=True, enqueue=True)

if __name__ == "__main__":
    logger.debug("This is Test Debug!")
    logger.info("This is Test Info!")
    logger.success("This is Test Success!")
    logger.error("This is Test Error!")
