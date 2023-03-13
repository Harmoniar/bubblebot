from typing import List, Union
from lib.collections import HandleMsg, Message, MessageData
from aiocache import cached
from .data import FF14_JARGON


errors_info = {
    1: "你想要查询的术语不能为空哦！",
    2: "你查询的术语我还不懂！",
    255: "该代码表示直接返回None, 不返回消息",
}


@cached(ttl=600)
async def jargon(handle_msg: HandleMsg) -> Union[Message, List[Message]]:

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
        result_content = FF14_JARGON.get(content.upper())

        # 如果要查询的术语不存在
        if not result_content:
            # 模板触发直接不返回消息, 返回None
            if result_content and handle_msg.trigger_type == 'template':
                errcode = 255
            else:
                errcode = 2
        else:
            errcode = 0

    if errcode == 0:
        res_msg = Message(MessageData.text(result_content))
    elif errcode == 255:
        res_msg = None
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg
