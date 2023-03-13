import re
import time
import importlib
from typing import List, Union
from loguru import logger
from component import cache
from lib.collections import ReceiveMsg, HandleMsg, SendMsg, Message
from lib.argspraser import ArgsPraser


class MessageHandlerMinxin:

    #  ======================= message handle start ========================

    async def handle_message(self, receive_msg: ReceiveMsg) -> HandleMsg:
        handle_msg = HandleMsg(receive_msg=receive_msg)
        robot_config: dict = cache.robots.get(receive_msg.admin_robot_id)
        robot_function: dict = cache.robot2function.get(receive_msg.admin_robot_id)

        # 1.前缀命令触发, 2.模板匹配触发
        if not handle_msg.is_trigger:
            # 前缀命令触发处理
            if 1 in robot_config.get("trigger_mode"):
                res_data: dict = await self._handle_prefix_trigger(receive_msg, robot_config, robot_function)
                if res_data.get("errcode") == 0:
                    trigger_type = "prefix"
                    self._handle_res_data(handle_msg, trigger_type, res_data, robot_function)

        if not handle_msg.is_trigger:
            # 模板触发处理
            if 2 in robot_config.get("trigger_mode"):
                res_data: dict = await self._handle_template_trigger(receive_msg, robot_function)
                if res_data.get("errcode") == 0:
                    trigger_type = "template"
                    self._handle_res_data(handle_msg, trigger_type, res_data, robot_function)

        return handle_msg

    def _handle_res_data(self, handle_msg: HandleMsg, trigger_type: str, res_data: dict, robot_function: dict):
        function_data: dict = robot_function[res_data.get("function_id")]
        handle_msg.is_trigger = True
        handle_msg.trigger_type = trigger_type
        handle_msg.function_id = res_data.get("function_id")
        handle_msg.function_url = function_data.get("function__function_url")
        handle_msg.function_class = function_data.get("function__function_class")
        handle_msg.command_args = res_data.get("command_args")

    #  ====================== prefix trigger judge ======================
    async def _handle_prefix_trigger(self, receive_msg: ReceiveMsg, robot_config: dict, robot_function: dict):
        message = receive_msg.message
        function_id = None
        command_args = None

        res_data = self._handle_prefix(message, robot_config.get("command_prefix"))
        if res_data.get("errcode") == 0:
            message = res_data.get("message")
        else:
            return res_data

        res_data = self._handle_command(message, robot_function)
        if res_data.get("errcode") == 0:
            message = res_data.get("message")
            function_id = res_data.get("function_id")
        else:
            return res_data

        res_data = self._handle_command_args(message, robot_function, function_id)
        if res_data.get("errcode") == 0:
            command_args = res_data.get("command_args")
        else:
            return res_data

        return {"errcode": 0, "function_id": function_id, "command_args": command_args}

    def _handle_prefix(self, message: str, command_prefix: list):
        # 判断触发方式是否为前缀触发，如果是则去掉触发前缀
        for prefix in command_prefix:
            if prefix and message.startswith(prefix):
                return {"errcode": 0, "message": message.removeprefix(prefix).strip()}
        return {"errcode": 1}

    def _handle_command(self, message: str, functions: dict):
        # 判断消息是否触发功能词标识，如果触发则取出功能名并返回
        for func in functions.values():
            for command in func.get("trigger_command"):
                if message.startswith(command):
                    return {"errcode": 0, "message": message.removeprefix(command).strip(), "function_id": func.get("function_id")}
        return {"errcode": 1}

    def _handle_command_args(self, message: str, robot_function: dict, function_id: str):
        # 解析消息参数, 并将结果返回
        try:
            args_praser: ArgsPraser = robot_function[function_id].get("command_args")
            command_args = args_praser.parse_args(message)
            return {"errcode": 0, "command_args": command_args}
        except:
            return {"errcode": 1}

    #  ====================== template trigger judge ======================

    async def _handle_template_trigger(self, receive_msg: ReceiveMsg, robot_function: dict):
        message = receive_msg.message
        function_id = None
        command_args = None

        # 匹配匹配模板, 返回获取到参数
        res_data = self._hanlde_match_template(message, robot_function)
        if res_data.get("errcode") == 0:
            function_id = res_data.get("function_id")
            match_args = res_data.get("match_args")
        else:
            return res_data

        res_data = self._hanlde_template_args(match_args, robot_function, function_id)
        if res_data.get("errcode") == 0:
            command_args = res_data.get("command_args")
        else:
            return res_data

        return {"errcode": 0, "function_id": function_id, "command_args": command_args}

    def _hanlde_match_template(self, message: str, robot_function: dict):

        # 遍历所有功能的template进行匹配
        for func in robot_function.values():
            # 匹配排除模板, 匹配成功则直接跳过该功能的判断
            # [pattern_obj,...]
            is_except = False
            for except_pattern in func.get("exception_template"):
                is_except = re.findall(except_pattern, message)
                if is_except:
                    break
            if is_except:
                continue

            # trigger_template存放匹配模板，如果通过了不匹配判断，则判断匹配模板，如果匹配成功，则会触发该功能
            for trigger_pattern, args_dest in func.get("trigger_template").items():
                # 如果匹配成功并且匹配到的值不为空的数量与args_dest对应, 则将其匹配的值与args_dest对应
                trigger_match = re.findall(trigger_pattern, message)
                # 匹配成功直接返回
                if trigger_match:
                    trigger_match = trigger_match[0]
                    # 如果只匹配到一个内容, 则匹配结果将会是["字符串"], 为保证和匹配到多个内容时一致, 将其转化为[["字符串"]]
                    if not isinstance(trigger_match, (list, tuple)):
                        trigger_match = [trigger_match]

                    # 数量匹配则将其一一对应
                    if len(trigger_match) == len(args_dest):
                        match_args = dict(zip(args_dest, trigger_match))
                    # 数量不匹配则直接是空字典
                    else:
                        match_args = {}

                    function_id = func.get("function_id")
                    return {"errcode": 0, "function_id": function_id, "match_args": match_args}

        return {"errcode": 1}

    def _hanlde_template_args(self, match_args: dict, robot_function: dict, function_id: str):
        # 解析参数, 并将结果返回
        try:
            args_praser: ArgsPraser = robot_function[function_id].get("command_args")
            command_args = args_praser.parse_dict_args(match_args)
            return {"errcode": 0, "command_args": command_args}
        except:
            return {"errcode": 1}

    #  ======================= message handle end ========================

    async def handle_call_function(self, handle_msg: HandleMsg) -> SendMsg:
        send_msg = SendMsg()

        res_data: dict = await self._call_function(handle_msg)
        if res_data.get("errcode") == 0:
            send_msg.is_called = True
            send_msg.send_messages = res_data.get("send_messages")
            send_msg.from_type = handle_msg.receive_msg.from_type
            send_msg.group_id = handle_msg.receive_msg.group_id
            send_msg.user_id = handle_msg.receive_msg.user_id
            send_msg.time_stamp = int(time.time())
            send_msg.process_time = "{:.3f}s".format(time.time() - handle_msg.handle_time)

        return send_msg

    async def _call_function(self, handle_msg: HandleMsg) -> List[Message]:
        function_url = handle_msg.function_url

        # 尝试以plugin为根路径, 通过反射获取功能函数对象
        if not function_url.startswith("plugin."):
            function_url = f"plugin.{function_url}"

        try:
            module_path, function_name = function_url.rsplit('.', 1)
            module = importlib.import_module(module_path)
            function = getattr(module, function_name)

            # 如果调用有send_messages结果则返回0, 如果没有要发送的message则返回1
            send_messages: Union[Message, List[Message]] = await function(handle_msg)
            if send_messages:
                if not isinstance(send_messages, list):
                    send_messages = [send_messages]
                return {"errcode": 0, "send_messages": send_messages}

        except Exception as e:
            logger.error(f"调用功能时出错, 错误信息: {repr(e)}")
            logger.exception(e)

        return {"errcode": 1}
