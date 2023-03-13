import copy
from typing import Any, Union


class Argument:
    def __init__(self, option: list, dest: str, explain: str = None, default: Any = None, action: str = None):
        self.option = option
        self.dest = dest
        self.value = default
        self.explain = explain
        self.action = action if action in ("store", "store_false", "store_true") else "store"

    @property
    def data(self) -> dict:
        return copy.deepcopy(self.__dict__)

    def __str__(self) -> str:
        return str(self.__dict__)


class ArgsPraser:
    def __init__(self):
        self.all_arguments = {}
        self.add_argument(option=[], dest="command_object", explain="命令对象")

    @property
    def args_data(self):
        args_data = {k: v.__dict__ for k,v in self.all_arguments.items()}
        return args_data

    def add_argument(self, option: list, dest: str, explain: str = None, default: Any = None, action: str = None):
        self.all_arguments[dest] = Argument(option=option, dest=dest, explain=explain, default=default, action=action)

    def remove_argument(self, dest: str):
        self.all_arguments.pop(dest, None)

    def parse_args(self, command_line: Union[list, str]) -> dict:
        if isinstance(command_line, str):
            command_line = command_line.split()
        origin_command_line = command_line.copy()

        args_map = {}
        # 获取参数的索引位置
        argument: Argument
        for argument in self.all_arguments.values():
            args_map[argument.dest] = argument.data

            for opt in argument.option:
                # 对于参数全部都要解析, 无论是否相同, 以防出现相同参数导致没有解析
                for times in range(command_line.count(opt)):

                    opt_index = command_line.index(opt)
                    # store: 从命令行中获取值存储
                    if argument.action == "store":
                        # 获取命令行中, 参数所在位置的后面的内容, 如果有则判断是否是长参数值, 也就是用"或'包裹的值
                        args_next_index = opt_index + 1
                        # 判断数所在位置的后面, 命令行中是否有下一个内容
                        if len(command_line) > args_next_index:
                            args_next_content = command_line[args_next_index]
                            # 判断是否是长参数值, 也就是用"或'包裹的值
                            # 如果取出来的下一个参数是以'或"开头, 则遍历直到获取到下一个'或"为止, 并获取该索引位置作为end_idnex
                            end_index = None
                            for mark in ('"', "'"):
                                if end_index == None and args_next_content.startswith(mark):
                                    for tmp_index, tmp_part in enumerate(command_line[args_next_index:]):
                                        if tmp_part.endswith(mark):
                                            end_index = args_next_index + tmp_index + 1
                                            break
                            # 如果有end_index, 则表示获取到了以'或"开头、并且以'或"结尾的内容, 则将其作为参数的值
                            if end_index != None:
                                args_map[argument.dest]["value"] = " ".join(command_line[args_next_index:end_index]).strip("\"' ")
                                # 从command_line中删除已经获取到值的内容
                                del command_line[args_next_index:end_index]

                            # 如果没有以'或"开头、或者没有以'或"结尾的内容, 则直接使用第一个作为参数的值
                            else:
                                args_map[argument.dest]["value"] = args_next_content.strip()
                                # 从command_line中删除已经获取到值的内容
                                del command_line[args_next_index]

                        # 判断数所在位置的后面没有内容, value直接置None
                        else:
                            args_map[argument.dest]["value"] = None

                    # store_true: 有该参数就代表值为True
                    elif argument.action == "store_true":
                        args_map[argument.dest]["value"] = True
                    # store_false: 有该参数就代表值为False
                    elif argument.action == "store_false":
                        args_map[argument.dest]["value"] = False

                    # 从command_line中删除已经获取到值的参数
                    del command_line[opt_index]

        # 参数获取完后, 获取命令对象

        # 如果命令在上面的操作后没有匹配到任何参数, 则将一整串command_line都作为命令对象
        if len(command_line) == len(origin_command_line):
            args_map["command_object"]["value"] = " ".join(command_line).strip("'\"").strip() if command_line else None

        # 判断command_line是否还有值, 或者最后一个参数是不是一开始一样, 没有值了或者最后一个不一样则命令对象直接置None
        elif (not command_line) or (command_line[-1] != origin_command_line[-1]):
            args_map["command_object"]["value"] = None
        # 如果最后一个参数以'或"结尾, 则反向遍历, 获取到以'或"开头的内容的索引
        else:
            last_index = len(command_line) - 1
            start_index = None
            for mark in ('"', "'"):
                if start_index == None and command_line[last_index].endswith(mark):
                    for tmp_index, tmp_part in enumerate(command_line[::-1]):
                        # 如果是索引等于last_index, 并且内容只有"或'则跳过, 防止出现last_index的值为'时, 导致获取不到内容
                        # 因为取反了, 所以tmp_index为0时, 表示tmp_index=last_index
                        if (tmp_index == 0) and (command_line[last_index] == mark):
                            continue
                        if tmp_part.startswith(mark):
                            start_index = last_index - tmp_index
                            break
            # 如果有start_index, 则表示获取到了以'或"开头、并且以'或"结尾的内容, 则将其作为参数的值
            if start_index != None:
                args_map["command_object"]["value"] = " ".join(command_line[start_index : last_index + 1]).strip("\"' ")
            # 如果没有以'或"开头、或者没有以'或"结尾的内容, 则直接使用最后一个作为参数的值
            else:
                args_map["command_object"]["value"] = command_line[last_index].strip()

        return args_map

    def parse_dict_args(self, args_dict: dict) -> dict:
        # 解析类似于 {"argument": "value",...}
        args_map = {}
        # 获取参数的索引位置
        argument: Argument
        for argument in self.all_arguments.values():
            # args_map添加默认参数
            args_map[argument.dest] = argument.data
            # 如果传入的args存在于all_arguments的参数中, 则更新值为传入的参数
            if argument.dest in args_dict:
                args_map[argument.dest]["value"] = args_dict.pop(argument.dest).strip()
        return args_map


if __name__ == "__main__":
    command_args1 = {"option": ["-s", "--source", "--from"], "dest": "source_langue", "explain": "源语种", "default": "auto", "action": "store"}
    command_args2 = {"option": ["-t", "--to", "--dest"], "dest": "dest_langue", "explain": "目标语种", "default": "auto", "action": "store"}
    arg_praser = ArgsPraser()
    arg_praser.add_argument(**command_args1)
    arg_praser.add_argument(**command_args2)

    print(arg_praser.parse_dict_args({"source_langue": "123123123"}))
