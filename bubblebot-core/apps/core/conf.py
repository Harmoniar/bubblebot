import os
from typing import Dict
import json
import yaml


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)


class Config(Dict):

    # 默认配置
    DEFAULT_CONFIG = {
        # Core配置
        'HTTP_HOST': '127.0.0.1',
        'HTTP_PORT': 8080,
        "WORKERS": 1,
        "THREADS": 1,
        "WORKER_CONNECTIONS": 1000,
        'SECRET_KEY': '',
        'API_KEY': '',
        'DEBUG': False,
        # 日志配置
        'LOG_LEVEL': 'DEBUG',
        'LOG_DIR': 'logs',
        # MySQL配置
        'DB_HOST': '127.0.0.1',
        'DB_PORT': 3306,
        'DB_USER': 'robot',
        'DB_PASSWORD': '',
        'DB_NAME': 'robot',
        # Redis配置
        # 'REDIS_HOST': '127.0.0.1',
        # 'REDIS_PORT': 6379,
        # 'REDIS_PASSWORD': '',
        # 'REDIS_DB': 0,
    }

    # 将值处理成默认值对应的类型 (读取环境变量配置时需要使用)
    def convert_type(self, k, v):
        default_value = self.DEFAULT_CONFIG.get(k)
        if default_value is None:
            return v
        default_value_type = type(default_value)
        # 处理bool类型
        if default_value_type is bool and isinstance(v, str):
            if v.lower() in ("true", "1"):
                return True
            else:
                return False
        # 处理list/dict类型
        if default_value_type in [list, dict] and isinstance(v, str):
            try:
                v = json.loads(v)
                return v
            except json.JSONDecodeError:
                return v
        try:
            if default_value_type in [list, dict]:
                v = json.loads(v)
            else:
                v = default_value_type(v)
        except Exception:
            pass
        return v

    def get_from_config(self, item):
        try:
            value = super().__getitem__(item)
        except KeyError:
            value = None
        return value

    def get_from_env(self, item):
        value = os.environ.get(item, None)
        if value is not None:
            value = self.convert_type(item, value)
        return value

    def get(self, item):
        # 先从配置文件中获取
        value = self.get_from_config(item)
        if value is not None:
            return value
        # 如果没有则从环境变量中获取
        value = self.get_from_env(item)
        if value is not None:
            return value
        # 如果还是没有则从默认配置中获取
        value = self.DEFAULT_CONFIG.get(item)
        return value

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, dict.__repr__(self))

    def __getitem__(self, key):
        return self.get(key)

    def __getattr__(self, item):
        return self.get(item)


class ConfigManager:
    def __init__(self, root_path: str = None):
        self.root_path = root_path if root_path else PROJECT_DIR
        self.config = Config()

    def from_mapping(self, mappings: Dict):
        for key, value in mappings.items():
            if key.isupper():
                self.config[key] = value
        return self.config

    def from_yaml(self, filename: str):
        filename = os.path.join(self.root_path, filename)
        try:
            with open(filename, 'rt', encoding='utf8') as f:
                return yaml.safe_load(f)
        except IOError as e:
            e.strerror = f'Unable to load configuration file ({e.strerror})'
            raise

    def check_config_exists(self):
        for i in ['config.yml', 'config.yaml']:
            filepath = os.path.join(self.root_path, i)
            if os.path.isfile(filepath):
                return filepath

    @classmethod
    def load_user_config(cls, root_path: str = None):
        root_path = root_path if root_path else PROJECT_DIR

        manager = cls(root_path)
        filepath = manager.check_config_exists()
        if not filepath:
            msg = """
            Error: No config file found.
            You can run `cp config_example.yaml config.yaml`, and edit it.
            """
            raise ImportError(msg)

        yaml_obj = manager.from_yaml(filepath)
        config = manager.from_mapping(yaml_obj)
        return config


CONFIG = ConfigManager.load_user_config()

if __name__ == '__main__':
    print(CONFIG.DB_USER)
    print(BASE_DIR)
    print(PROJECT_DIR)
