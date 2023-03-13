# coding: utf-8

import time
import hashlib
from typing import Union, List
from loguru import logger
from aiocache import cached
from lib.common import httpx_client
from lib.collections import HandleMsg, Message, MessageData

errors_info = {
    1: "翻译内容不能为空哦！",
    2: "无法理解你输入的语种名~",
    3: "调用翻译接口失败, 请稍后重试~",
}


language_map = {
    'zh': ['chinese', '中', '中文', '中国语', '天朝语', '国语'],
    'en': ['english', '英', '英语', '英文', '英格兰语', '鸟语', '洋文'],
    'ja': ['japanese', '日', '日语', '日本语', '日文'],
    'ru': ['russian', '俄', '俄语', '毛子语', '俄罗斯语'],
}


@cached(ttl=600)
async def youdao_translate(handle_msg: HandleMsg) -> Union[Message, List[Message]]:
    errcode = None

    command_args = handle_msg.command_args
    content: str = command_args.get("command_object").get("value")

    if errcode == None:
        # 如果没有内容则返回错误信息
        if not content:
            errcode = 1

    if errcode == None:
        for arg_name in ("source_langue", "dest_langue"):
            arg_value = command_args.get(arg_name).get("value")
            if (arg_value in language_map) or (arg_value == 'auto'):
                continue
            # 将输入的语言解析成对应代码
            for map_key, map_value in language_map.items():
                if arg_value in map_value:
                    command_args[arg_name]["value"] = map_key
                    break
            # 如果没有匹配的则返回错误信息
            else:
                errcode = 2

    # 调用接口
    if errcode == None:
        lts = str(int(time.time() * 1000))
        salt = str(int(time.time() * 10000))
        sign = f'fanyideskweb{content}{salt}Ygy_4c=r#e#4EX^NUGUc5'
        sign = hashlib.md5(sign.encode('utf-8')).hexdigest()

        headers = {
            'Cookie': 'OUTFOX_SEARCH_USER_ID=0@172.0.0.1;',
            'Referer': 'https://fanyi.youdao.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        }

        data = {
            'i': content,
            'from': command_args.get("source_langue").get("value"),
            'to': command_args.get("dest_langue").get("value"),
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': salt,
            'sign': sign,
            'lts': lts,
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME',
        }

        try:
            url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'

            res = await httpx_client.post(url, headers=headers, data=data)
            res.raise_for_status()
        except Exception as e:
            logger.debug(f"请求有道翻译接口出错, 错误信息: {repr(e)}")
            errcode = 3

    # 判断调用结果
    if errcode == None:
        res_data: dict = res.json()
        if res_data.get("errorCode") != 0:
            errcode = 3

    # 处理结果
    if errcode == None:
        translate_result = "".join([i.get("tgt") for i in res_data.get("translateResult")[0]])
        errcode = 0

    if errcode == 0:
        res_msg = Message(MessageData.text(translate_result))
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg


if __name__ == '__main__':
    import asyncio

    handle_msg = HandleMsg(
        command_args={
            'command_object': {
                'option': [],
                'dest': 'command_object',
                'value': 'hello world! i am super hero. but i think you are a foolish man, so i want to use my big fuck insert you are ass. can you help me? so you can, i will do.',
                'explain': '命令对象',
                'action': 'store',
            },
            'source_langue': {
                'option': ['-s', '--source'],
                'dest': 'source_langue',
                'value': '英文',
                'explain': '源语种',
                'action': 'store',
            },
            'dest_langue': {
                'option': ['-d', '--dest'],
                'dest': 'dest_langue',
                'value': '中文',
                'explain': '目标语种',
                'action': 'store',
            },
        }
    )

    print(asyncio.get_event_loop().run_until_complete(youdao_translate(handle_msg)))
