import time
from typing import List
import re


class MessageData:
    class Data:
        def __init__(self, type: str, data: dict):
            self.type = type
            self.data = data

        @property
        def cqdata(self) -> dict:
            return {"type": self.type, "data": self.data}

        @property
        def cqcode(self) -> str:
            code_list = [self.type]
            for k, v in self.data.items():
                if len(str(v)) > 54:
                    code_list.append(f"{k}={v[:53]}...")
                else:
                    code_list.append(f"{k}={v}")

            return "[CQ:{}]".format(",".join(code_list))

        def __str__(self) -> str:
            return self.cqcode

    def __init__(self, type: str, data: dict):
        return self.Data(type, data)

    valid_cqcode_type = ("face", "record", "at", "share", "music", "image", "reply", "redbag", "poke", "xml", "text")
    cqcode_pattern = re.compile("\[CQ:.*?\]")
    cqcode_data_pattern = re.compile("(.*?)=(.*)")

    @classmethod
    def phrase_cqcode_data(cls, cqcode: str) -> dict:
        """获取CQ码中的数据转化为字典"""
        if not re.match(cls.cqcode_pattern, cqcode):
            raise ValueError("Invalid cqcode format.")
        cqcode_string_list = cqcode.removeprefix(f"[CQ:").removesuffix("]").strip(", ").split(",")
        type = cqcode_string_list.pop(0)
        if not type:
            raise ValueError("The cqcode must have type of param.")
        elif type not in cls.valid_cqcode_type:
            raise ValueError(f"Unsupport cqcode type: {type}")
        data = (re.findall(cls.cqcode_data_pattern, data_str.strip())[0] for data_str in cqcode_string_list if data_str.strip())
        data = {i[0]: i[1] for i in data}
        return data

    @classmethod
    def get_text_message_data(cls, message: str) -> dict:
        """获取字符串中的CQ码并生成消息数据对象并放入字典中返回"""
        cqcode_list = re.findall(cls.cqcode_pattern, message)
        message_data_obj_dict = {}
        for cqcode in cqcode_list:
            try:
                message_data_obj_dict[cqcode] = cls.phrase_cqcode_data(cqcode)
            except Exception:
                pass
        return message_data_obj_dict

    @classmethod
    def text(cls, text: str) -> Data:
        """生成文本消息数据对象
        :param text: 文本消息
        """
        message_dict = {"type": "text", "data": {"text": str(text)}}
        return cls.Data(**message_dict)

    @classmethod
    def face(cls, id: str) -> Data:
        """生成表情数据对象
        :param id: 表情ID, 见: https://github.com/kyubotics/coolq-http-api/wiki/%E8%A1%A8%E6%83%85-CQ-%E7%A0%81-ID-%E8%A1%A8
        """
        message_dict = {"type": "face", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)

    @classmethod
    def record(cls, file: str = None, magic: str = None, cache: str = None, timeout: str = None) -> Data:
        """生成语音数据对象
        :param file:    语音文件名, 本地文件路径、或网络URL路径
        :param magic:   0或1 发送时可选, 默认0, 设置为1表示变声
        :param cache:   0或1 只在通过网络URL发送时有效, 默认1表示使用已缓存的文件
        :param timeout: 只在通过网络URL发送时有效, 单位秒, 表示下载网络文件的超时时间 , 默认不超时
        """
        message_dict = {"type": "record", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)

    @classmethod
    def at(cls, qq: str) -> Data:
        """生成表情数据对象
        :param qq: @的QQ号, all表示全体成员
        """
        message_dict = {"type": "at", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls(message_dict)

    @classmethod
    def share(cls, url: str, title: str, content: str = None, image: str = None) -> Data:
        """生成链接分享数据对象
        :param url:     分享链接URL
        :param title:   标题
        :param content: 发送时可选, 内容描述
        :param image:   发送时可选, 图片URL
        """
        message_dict = {"type": "share", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)

    @classmethod
    def music(cls, type: str, id: str = None, url: str = None, audio: str = None, title: str = None, content: str = None, image: str = None) -> Data:
        """生成音乐分享数据对象
        :param type:    qq/163/xm/custom 分别表示: QQ音乐/网易云音乐/虾米音乐/自定义
        :param id:      非自定义音乐分享时使用, 歌曲ID
        :param url:     自定义音乐分享时使用, 点击后跳转的目标URL
        :param audio:   自定义音乐分享时使用, 音乐URL
        :param title:   自定义音乐分享时使用, 标题
        :param content: 自定义音乐分享时可选, 内容描述
        :param image:   自定义音乐分享时可选, 图片URL
        """
        message_dict = {"type": "music", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)

    @classmethod
    def image(cls, file: str, type: str = None, url: str = None, cache: str = None) -> Data:
        """生成图片数据对象
        :param file:    图片文件名
        :param type:    图片类型, flash表示闪照, show表示秀图, 默认普通图片
        :param url:     图片 URL
        :param cache:   0或1 只在通过网络URL发送时有效, 默认1表示使用已缓存的文件

        图片最大不能超过30MB
        PNG格式不会被压缩, JPG可能不会二次压缩, GIF非动图转成PNG
        GIF动图原样发送(总帧数最大300张, 超过无法发出, 无论循不循环)
        """
        message_dict = {"type": "image", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)

    @classmethod
    def poke(cls, qq: str) -> Data:
        """生成戳一戳数据对象
        :param qq: 需要戳的成员

        仅群聊, 发送戳一戳消息无法撤回
        """
        message_dict = {"type": "poke", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)

    @classmethod
    def xml(cls, data: str, resid: str = None) -> Data:
        """生成XML 数据对象
        :param data: xml内容, xml中的value部分, 记得实体化处理
        :param resid: 可以不填

        注意: xml中的value部分, 记得html实体化处理后, 再打加入到数据中
        """
        message_dict = {"type": "xml", "data": {k: v for k, v in locals().items() if (k != 'cls' and v != None)}}
        return cls.Data(**message_dict)


# 接收消息类
class ReceiveMsg:
    def __init__(
        self,
        admin_id: int = None,
        robot_id: int = None,
        user_id: int = None,
        group_id: int = None,
        from_type: str = None,
        message: str = None,
        cqcode_data: dict = None,
        user_name: str = None,
        user_gender: str = None,
        time_stamp: int = None,
    ):
        self.admin_robot_id: str = f"{admin_id}:{robot_id}"
        self.admin_id = admin_id
        self.robot_id = robot_id
        self.user_id = user_id
        self.group_id = group_id
        self.from_type = from_type
        self.message = message
        self.cqcode_data = cqcode_data
        self.user_name = user_name
        self.user_gender = user_gender  # male or female or unknown
        self.time_stamp = time_stamp  # 秒级

    @classmethod
    def convert_gocqhttp(cls, admin_id: int, robot_id: int, message: dict):
        """通过GocqHttp消息获取ReceiveMsg对象"""
        sender: dict = message.get("sender")
        data = {
            "admin_id": admin_id,
            "robot_id": robot_id,
            "user_id": message.get("user_id"),
            "group_id": message.get("group_id"),
            "from_type": message.get("message_type"),
            "message": message.get("message"),
            "cqcode_data": MessageData.get_text_message_data(message.get("message")),
            "user_name": sender.get("nickname"),
            "user_gender": sender.get("sex"),
            "time_stamp": int(time.time()),
        }
        return cls(**data)

    def __str__(self):
        return str(self.__dict__)


# 处理消息类
class HandleMsg:
    def __init__(
        self,
        is_trigger: bool = False,
        trigger_type: str = False,
        function_id: str = None,
        function_url: str = None,
        function_class: str = None,
        command_args: dict = None,
        receive_msg: ReceiveMsg = None,
    ):
        self.is_trigger = is_trigger
        self.trigger_type = trigger_type  # prefix or template
        self.function_id = function_id
        self.function_url = function_url
        self.function_class = function_class
        self.command_args = command_args
        self.receive_msg = receive_msg

        self.handle_time = time.time()

    def __str__(self):
        res = self.__dict__.copy()
        res.pop("handle_time", None)
        return str(res)


# 一个SendMsgs中可以有多个Message, 对应Bot发送的多条消息
# 一个Message中可以有多个MessageData, 对应一条消息的多个部分
# 消息类 - 发送消息时用
class Message:
    def __init__(self, *message: MessageData):
        self.message = message

    @property
    def message_data(self):
        return [data.cqdata for data in self.message]

    def __str__(self):
        return "Message: {}".format([str(i) for i in self.message])


# 发送消息类
class SendMsg:
    def __init__(
        self,
        is_called: str = False,
        send_messages: List[Message] = None,
        from_type: str = None,
        group_id: int = None,
        user_id: int = None,
        process_time: float = None,
        time_stamp: int = None,
    ):
        self.is_called = is_called
        self.from_type = from_type
        self.group_id = group_id
        self.user_id = user_id
        self.time_stamp = time_stamp
        self.process_time = process_time

        if isinstance(send_messages, list):
            self.send_messages = send_messages
        else:
            self.send_messages = [send_messages]

    def __str__(self):
        res = self.__dict__.copy()
        res["send_messages"] = [str(i) for i in self.send_messages]
        return str(res)
