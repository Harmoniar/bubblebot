import re
from typing import List, Union
from bs4 import BeautifulSoup
from aiocache import cached
from loguru import logger
from lib.common import httpx_client
from lib.collections import HandleMsg, Message, MessageData

errors_info = {
    1: "你想要查询的内容不能为空哦！",
    2: "调用翻译接口失败, 请稍后重试~",
    3: "非常抱歉, 没有找到你想要的结果",
    255: "该代码表示直接返回None, 不返回消息",
}


@cached(ttl=600)
async def baidu_baike(handle_msg: HandleMsg) -> Union[Message, List[Message]]:

    errcode = None
    content: str = handle_msg.command_args.get("command_object").get("value")

    if errcode == None:
        # 如果没有内容则返回错误信息
        if not content:
            # 模板触发直接不返回消息, 返回None
            if handle_msg.trigger_type == 'template':
                errcode = 255
            else:
                errcode = 1

    if errcode == None:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0 Safari/537.0'}
        try:
            url = f'https://baike.baidu.com/item/{content}'
            res = await httpx_client.post(url, headers=headers, follow_redirects=True)
            res.raise_for_status()
        except Exception:
            # 模板触发直接不返回消息, 返回None
            if handle_msg.trigger_type == 'template':
                errcode = 255
            else:
                errcode = 2

    if errcode == None:
        try:
            soup = BeautifulSoup(res.text, 'lxml')
            result_content = soup.find('meta', attrs={'name': 'description'}).attrs.get('content')
            result_content = re.sub(r'(.*)。.*', r'\1。', result_content, 1).strip()
            errcode = 0
        except Exception as e:
            logger.debug(f"请求百度百科接口出错, 错误信息: {repr(e)}")

            # 模板触发直接不返回消息, 返回None
            if handle_msg.trigger_type == 'template':
                errcode = 255
            else:
                errcode = 3

    if errcode == 0:
        res_msg = Message(MessageData.text(result_content))
    elif errcode == 255:
        res_msg = None
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg
