import re
import aredis
from loguru import logger
from lib.conf import CONFIG
from lib.common import httpx_client
from lib.cipher import aes_cipher
from lib.argspraser import ArgsPraser

robots = {}
robot2function = {}
robot2timing = {}


async def sync_cache(keys: list, model_name: str, filter_conditions: dict, fields: list = None):
    return_code = None
    var_name = model_name.lower()

    url = CONFIG.HTTP_CURDAPI_URL
    data = {
        "method": "query",
        "model_name": model_name,
        "filter_conditions": filter_conditions,
        "data": fields if fields else [],
    }

    try:
        data = aes_cipher.encrypt(data)
        res = await httpx_client.post(url, data=data)
    except Exception as e:
        logger.warning(f"{model_name} cache sync error, request link failed: {repr(e)}")
        return_code = 1

    if return_code == None:
        if res.status_code != 200:
            return_code = 1

    if return_code == None:
        try:
            res_data: dict = aes_cipher.decrypt(res.content, is_json=True)
        except Exception as e:
            logger.warning(f"{model_name} cache sync error, decrypt response failed: {repr(e)}")
            return_code = 1

    if return_code == None:
        if res_data.get("errcode") == 0:

            # 将数据处理成字典
            tmp_data = {}
            for botfunc in res_data.get("data"):

                key_values = [str(botfunc.get(k)) for k in keys]
                if model_name in ("Robots", "Robot2Timing"):
                    tmp_data[":".join(key_values)] = botfunc

                elif model_name == "Robot2Function":
                    if not tmp_data.get(":".join(key_values[:2])):
                        tmp_data[":".join(key_values[:2])] = {}
                    # 将template的正则表达式转化为pattern对象, 以提供更高效的匹配
                    # 默认: {"template_regexp": []} 转化为: {pattern_obj: ["args_name1", "args_name2"]}
                    tmp_patterns = {}
                    for k, v in botfunc.get("trigger_template").items():
                        try:
                            pattern = re.compile(k)
                        except:
                            continue
                        tmp_patterns[pattern] = v
                    botfunc["trigger_template"] = tmp_patterns

                    # 默认: ["template_regexp",...] 转化为: [pattern_obj,...]
                    tmp_patterns = []
                    for i in botfunc.get("exception_template"):
                        try:
                            pattern = re.compile(i)
                        except:
                            continue
                        tmp_patterns.append(pattern)
                    botfunc["exception_template"] = tmp_patterns

                    # 将命令参数转化为解析器对象, 方便解析命令行
                    # [{"option": [str, ...], "dest": "...", "default": "...", "explain": "...", "action": "store"}, ...]
                    args_praser = ArgsPraser()
                    for argument in botfunc.get("command_args"):
                        try:
                            args_praser.add_argument(**argument)
                        except Exception as e:
                            logger.exception(e)
                            continue
                    botfunc["command_args"] = args_praser
                    tmp_data[":".join(key_values[:2])][":".join(key_values[2:])] = botfunc

            globals()[var_name] = tmp_data

            if len(tmp_data) > 0:
                logger.debug(f"{model_name} cache sync success.")
            else:
                logger.debug(f"{model_name} cache sync success, but the response robot data is empty.")

            return_code = 0
        else:
            logger.warning(f"{model_name} cache sync failed, error message: {res_data.get('info')}")
            return_code = 1

    return return_code


redis_pool = aredis.ConnectionPool(
    host=CONFIG.REDIS_HOST,
    port=CONFIG.REDIS_PORT,
    password=CONFIG.REDIS_PASSWORD,
    db=CONFIG.REDIS_DB,
)

redis_connect = aredis.StrictRedis(connection_pool=redis_pool)


if __name__ == "__main__":
    from lib.conf import CONFIG
    from lib.common import httpx_client
    from lib.cipher import aes_cipher
    import asyncio

    asyncio.get_event_loop().run_until_complete(
        sync_cache(
            ("admin_user_id", "robot_id"),
            "Robots",
            {'robot_status': 1},
            fields=["admin_user_id", "robot_id", "robot_name", "master_id", "trigger_mode", "command_prefix", "command_prefix", "user_function_permit", "comment"],
        )
    )

    asyncio.get_event_loop().run_until_complete(
        sync_cache(
            ("admin_user_id", "robot_id", "function_id"),
            "Robot2Function",
            {'robot__robot_status': 1, 'function_status': 1, 'function__global_function_status': 1},
            fields=[
                "admin_user_id",
                "robot_id",
                "function_id",
                "function__function_name",
                "function__function_url",
                "function__function_class",
                "function__comment",
                "trigger_command",
                "command_args",
                "trigger_template",
                "exception_template",
            ],
        )
    )
    print(robot2function)
