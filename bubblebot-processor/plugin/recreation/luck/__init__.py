import random
import base64
import random
from typing import List, Union
from lib.conf import CONFIG
from lib.collections import HandleMsg, Message, MessageData
from .data import LUCK_DATA


errors_info = {
    1: "发生未知错误, 请联系管理员",
    255: "该代码表示直接返回None, 不返回消息",
}
LUCK_IMAGE_DIR = f"{CONFIG.IMAGE_PATH}/luck/"


async def luck(handle_msg: HandleMsg) -> Union[Message, List[Message]]:

    # 玄学之循环77次取出77个值，再从其中获取7个，再随机获取这7个中的一个作为最终签
    random_num_list = []
    for i in range(77):
        random_num_list.append(random.randint(1, 100))
    random_num_list = random.choices(random_num_list, k=7)
    random_num = random.choice(random_num_list)


    luck_data = LUCK_DATA.get(random_num)

    msg = f'{luck_data.get("name")}\n'
    msg += '〖解曰〗\n'
    msg += "\n".join(luck_data.get("explain"))

    image_path = LUCK_IMAGE_DIR + luck_data.get("image_file")

    with open(image_path, 'rb') as f:
        base64_str = base64.b64encode(f.read()).decode()
        base64_str = base64_str if "base64://" in base64_str else "base64://" + base64_str

    res_msg = Message(MessageData.image(base64_str), MessageData.text(msg))

    return res_msg
