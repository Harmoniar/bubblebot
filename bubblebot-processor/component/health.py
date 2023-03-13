from loguru import logger
from lib.conf import CONFIG
from lib.common import httpx_client
from lib.cipher import aes_cipher

# 用于健康上报 {user_id: {robot_id: 错误信息}, ...}
running_messages = {}


async def health_report():

    return_code = None

    url = CONFIG.HTTP_HEALTH_REPORT_URL
    data = {"id": CONFIG.COMPONENT_ID, "role": 2, "running_msg": running_messages}

    try:
        data = aes_cipher.encrypt(data)
        res = await httpx_client.post(url, data=data)

    except Exception as e:
        logger.warning(f"Heath report error, request link failed: {repr(e)}")
        return_code = 1

    if return_code == None:
        if res.status_code != 200:
            return_code = 1

    if return_code == None:
        try:
            res_data: dict = aes_cipher.decrypt(res.content, is_json=True)
        except Exception as e:
            logger.warning(f"Heath report error, decrypt response failed: {repr(e)}")
            return_code = 1

    if return_code == None:
        if res_data.get("errcode") == 0:
            global robots
            robots = res_data.get("data")
            logger.debug(f"Heath report success.")
            return_code = 0
        else:
            logger.warning(f"Heath report failed, error message: {res_data.get('info')}")
            return_code = 1

    return return_code


def update_running_messages(admin_id, robot_id, message):
    if not running_messages.get(admin_id):
        running_messages[admin_id] = {}
    running_messages[admin_id][robot_id] = message
