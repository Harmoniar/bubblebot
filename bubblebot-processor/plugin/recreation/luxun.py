import random
from lib.image_utils import BuildImage
from typing import List, Union
from aiocache import cached
from lib.conf import CONFIG
from lib.collections import HandleMsg, Message, MessageData


errors_info = {
    1: "我不能什么都不说",
    2: "太长了，我说不完...",
    3: "你话太多了, 我不想说",
    255: "该代码表示直接返回None, 不返回消息",
}

footnote_author = BuildImage(0, 0, plain_text="--鲁迅", font_size=32, font='msyh.ttf', font_color=(255, 255, 255))
LUXIN_IMG_PATH = f"{CONFIG.IMAGE_PATH}/other/luxun.jpg"


def split_msg_lines(img_handler: BuildImage, content: str):
    # 当文字所需x轴 > 图片宽度-40时, 将文字拆成两半并在尾部加上\n
    tmp_content = ""
    while img_handler.getsize(content)[0] > (img_handler.w - 40):
        n = int(len(content) / 2)
        tmp_content += f"{content[:n]}".rstrip(",，") + "\n"
        content = content[n:]
    tmp_content += content.lstrip(",，")
    return tmp_content


@cached(ttl=600)
async def luxunsay(handle_msg: HandleMsg) -> Union[Message, List[Message]]:

    errcode = None
    content: str = handle_msg.command_args.get("command_object").get("value")

    # 排除空文本
    if errcode == None:
        content = content.strip().lstrip(":：,，") if content else None
        if not content:
            content = errors_info.get(1)

    if errcode == None:
        if len(content) > 60:
            content = errors_info.get(random.randint(2, 3))

    if errcode == None:
        if len(content) <= 20:
            font_size = 36
        elif len(content) <= 25:
            font_size = 32
        else:
            font_size = 28

        img_handler = BuildImage(0, 0, font_size=font_size, background=LUXIN_IMG_PATH, font='msyh.ttf')
        tmp_content = split_msg_lines(img_handler, content)

    if errcode == None:
        if len(tmp_content.split('\n')) > 2:
            content = errors_info.get(random.randint(2, 3))
            tmp_content = split_msg_lines(img_handler, content)

    if errcode == None:
        x = int((480 - img_handler.getsize(tmp_content.split("\n")[0])[0]) / 2)
        y = 330 if len(tmp_content.split('\n')) == 1 else 300
        img_handler.text((x, y), tmp_content, (255, 255, 255))
        img_handler.paste(footnote_author, (345, 400), True)
        errcode = 0

    if errcode == 0:
        res_msg = Message(MessageData.image(img_handler.pic2bs64()))
    elif errcode == 255:
        res_msg = None
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg
