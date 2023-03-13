import aredis
from loguru import logger
from lib.conf import CONFIG
from lib.common import httpx_client
from lib.cipher import aes_cipher

robots = []


async def sync_cache():
    return_code = None

    url = CONFIG.HTTP_CURDAPI_URL
    data = {
        "method": "query",
        "model_name": "Robots",
        "filter_conditions": {'robot_status': 1},
        "data": [],
    }

    try:
        data = aes_cipher.encrypt(data)
        res = await httpx_client.post(url, data=data)
    except Exception as e:
        logger.warning(f"Cache sync error, request link failed: {repr(e)}")
        return_code = 1

    if return_code == None:
        if res.status_code != 200:
            return_code = 1

    if return_code == None:
        try:
            res_data: dict = aes_cipher.decrypt(res.content, is_json=True)
        except Exception as e:
            logger.warning(f"Cache sync error, decrypt response failed: {repr(e)}")
            return_code = 1

    if return_code == None:
        if res_data.get("errcode") == 0:
            global robots
            robots = res_data.get("data")
            if len(robots) > 0:
                logger.debug(f"Cache sync success.")
            else:
                logger.warning(f"Cache sync success, but the response robot data is empty.")
            return_code = 0
        else:
            logger.warning(f"Cache sync failed, error message: {res_data.get('info')}")
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

    asyncio.get_event_loop().run_until_complete(sync_cache())
    print(robots)
