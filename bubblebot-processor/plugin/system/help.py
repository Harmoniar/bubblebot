import yaml
from typing import List, Union
from lib.collections import HandleMsg, Message, MessageData
from component.cache import robot2function

# 测试数据
# import re
# robot2function = {
#     "985816089@qq.com:295983086": {
#         'baidu baike': {
#             'admin_user_id': '985816089@qq.com',
#             'robot_id': 1803867128,
#             'function_id': 'baidu baike',
#             'function__function_name': '百度百科',
#             'function__function_url': 'wiki.baidu.baidu_baike',
#             'function__function_class': 'wiki',
#             'trigger_command': ['whatis'],
#             'command_args': None,
#             'trigger_template': {re.compile('(.*?)是(?:什么|啥)(?:东西|玩意|鬼|意思)?[?？ ]*?$'): ['command_object']},
#             'exception_template': [],
#         }
#     }
# }

errors_info = {
    1: "指定的功能不存在",
    2: "没有更多的功能",
    255: "该代码表示直接返回None, 不返回消息",
}


async def help(handle_msg: HandleMsg) -> Union[Message, List[Message]]:

    errcode = None
    content = handle_msg.command_args.get("command_object").get("value")

    # 获取Robot所有功能
    admin_robot_id = handle_msg.receive_msg.admin_robot_id
    robot_functions: dict = robot2function.get(admin_robot_id)

    # 如果指定了功能, 但功能又不存在, 则返回错误信息
    if errcode == None:
        if (content != None) and (content not in robot_functions):
            errcode = 1

    if errcode == None:
        # 如果指定了功能, 则只返回指定功能的完整信息
        if content:
            function_data: dict = robot_functions.get(content)
            function_msg = "功能ID: {fid}\n功能名称: {fname}\n".format(
                fid=function_data.get("function_id"),
                fname=function_data.get("function__function_name"),
            )

            if function_data.get("function__explain"):
                tmp_data = function_data.get("function__explain")
                function_msg += f'功能说明: {tmp_data}\n'

            if function_data.get("function__function_class"):
                tmp_data = function_data.get("function__function_class")
                function_msg += f'功能分类: {tmp_data}\n'

            if function_data.get("trigger_command"):
                tmp_data = function_data.get("trigger_command")
                function_msg += f'触发命令: {tmp_data}\n'

            if function_data.get("command_args"):
                args_data: dict = function_data.get("command_args").args_data
                tmp_data = {}
                # 删除除option和explain之外所有参数
                for arg_name, arg_data in args_data.items():
                    tmp_data[arg_name] = {k: v for k, v in arg_data.items() if k in ("option", "explain")}

                function_msg += f'触发参数: \n{yaml.safe_dump(tmp_data, allow_unicode=True, default_flow_style=False, sort_keys=False)}'

            if function_data.get("trigger_template"):
                tmp_data = [i.pattern for i in function_data.get("trigger_template").keys()]
                function_msg += f'触发模板: \n{yaml.safe_dump(tmp_data, allow_unicode=True, default_flow_style=False, sort_keys=False)}'

            if function_data.get("exception_template"):
                tmp_data = [i.pattern for i in function_data.get("exception_template")]
                function_msg += f'排除模板: \n{yaml.safe_dump(tmp_data, allow_unicode=True, default_flow_style=False, sort_keys=False)}'

        # 如果没有指定功能, 则返回所有功能的简短信息
        else:
            function_msg_list = []
            for function_name, function_data in robot_functions.items():
                tmp_msg = "功能ID: {fid}\n功能名称: {fname}\n".format(
                    fid=function_data.get("function_id"),
                    fname=function_data.get("function__function_name"),
                )
                if function_data.get("function__explain"):
                    tmp_msg += f'功能说明: {function_data.get("function__explain")}\n'

                tmp_msg += "... ...\n"
                function_msg_list.append(tmp_msg)
            function_msg = "======================\n".join(function_msg_list)

        if function_msg:
            errcode = 0
        else:
            errcode = 2

    if errcode == 0:
        res_msg = Message(MessageData.text(function_msg.strip()))
    elif errcode == 255:
        res_msg = None
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg


if __name__ == "__main__":
    from lib.collections import ReceiveMsg
    import asyncio

    handle_msg = HandleMsg()
    handle_msg.command_args = {"command_object": None}
    handle_msg.receive_msg = ReceiveMsg("985816089@qq.com", "295983086")

    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(help(handle_msg))

    print(res)
