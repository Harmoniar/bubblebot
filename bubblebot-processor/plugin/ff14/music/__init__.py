import re
import os
import time
import base64
import asyncio
from typing import Union, List

import aiofiles
from aiocache import cached
from mido import MidiFile, MidiTrack, Message as MidiMessage

from lib.collections import HandleMsg, Message, MessageData
from .utils import midi_to_audio
from .data import NOTE_MAP


# 音符语法: C3: .1 / .C / C31 / C3-1 / C3C / C3-C / .1# / .C# / .#1 / .#C / C31# / C3#1 / C3C# / C31# / C3-1# / C3-C# / C3-#1 / C3-#C / .2b / .D# / .#D / .#D / C32# ... ...
# 全音符(四拍):C--- / 二分音符(两拍):C-- / 四分音符(一拍):C / 八分音符(半拍):-C / 十六分音符(四分之一拍):--C / 三十二分音符(八分之一拍):---C

errors_info = {
    1: "音谱内容不能为空哦！",
    2: "非常抱歉, 音谱最长只支持128个音符",
    3: "错误的音符语法, 请细细检查",
    4: "内部错误: 转化音频格式失败",
    5: "bpm必须为30~360范围内的数值, 请重新指定",
    6: "乐器类型必须为0~127范围内的数值, 请重新指定",
}


@cached(ttl=300)
async def generate_music(handle_msg: HandleMsg) -> Union[Message, List[Message]]:
    errcode = None
    command_args = handle_msg.command_args
    content: str = command_args.get("command_object").get("value")
    bpm = command_args.get("bpm").get("value")
    instrument = command_args.get("instrument").get("value")

    if errcode == None:
        # 如果没有内容则返回错误信息
        if not content:
            errcode = 1

    if errcode == None:
        # 否则取出内容中的乐符标识
        content = content.upper()
        content = re.split(r"[\s,|]", content.strip())
        notes_list = [i for i in content if i]

        # 如果乐符数超过64个则返回错误信息
        if len(notes_list) > 128:
            errcode = 2

    if errcode == None:
        # 如果BPM不为数值则返回错误信息, 或者BPM小于30或者大于360则返回错误信息
        if (not isinstance(bpm, int) and not bpm.isdigit()) or (int(bpm) < 30 or int(bpm) > 360):
            errcode = 5
        else:
            bpm = int(bpm)

    if errcode == None:
        # 如果乐器类型不为数值则返回错误信息, 或者乐器类型小于0或者大于127则返回错误信息
        if (not isinstance(instrument, int) and not instrument.isdigit()) or (int(instrument) < 0 or int(instrument) > 127):
            errcode = 6
        else:
            instrument = int(instrument)

    if errcode == None:
        # 判断音符语法是否合法
        for note in notes_list:
            note: str
            # 乐符不存在于乐符列表中则返回错误信息
            if note.strip("-") not in NOTE_MAP:
                errcode = 3
            # 乐符前后同时存在"-"则返回错误信息
            elif note.startswith("-") and note.endswith("-"):
                errcode = 3
            # 如果乐符以-开头, 则判断是否只以-或--或---开头, 如果不是则返回错误信息
            elif note.startswith("-") and not (note.startswith("-") or note.startswith("--") or note.startswith("---")):
                errcode = 3
            # 如果乐符以-结尾, 则判断是否只以---或--开头, 如果不是则返回错误信息
            elif note.endswith("-") and not (note.endswith("---") or note.endswith("--")):
                errcode = 3

    if errcode == None:
        # bpm越大, 音与音之间的间隔越大, 也就是说节奏越慢
        bpm = bpm
        meta_time = int(60 / bpm * 1000)

        # 生成临时文件名
        tmp_midi_path = f"tmp/ff14-music-{int(time.time())}.mid"
        tmp_mp3_path = tmp_midi_path.removesuffix(".mid") + ".mp3"

        loop = asyncio.get_event_loop()

        # 生成mid对象和音轨对象
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)

        # 添加音符到音轨
        track.append(MidiMessage('program_change', channel=0, program=instrument, time=0))
        for note in notes_list:
            # 如果是全分音符则乘以4
            if note.endswith("---"):
                note_time = int(meta_time * 4)
            # 如果是二分音符则乘以2
            elif note.endswith("--"):
                note_time = int(meta_time * 2)
            # 如果是四分音符则保持原样
            elif (not note.startswith("-")) and (not note.endswith("-")):
                note_time = meta_time
            # 如果是八分音符则除以2
            elif note.startswith("-"):
                note_time = int(meta_time / 2)
            # 如果是十六分音符则除以4
            elif note.startswith("--"):
                note_time = int(meta_time / 4)
            # 如果是三十二分音符则除以8
            elif note.startswith("---"):
                note_time = int(meta_time / 8)

            note_num = NOTE_MAP.get(note.strip("-"))

            track.append(MidiMessage('note_on', note=note_num, velocity=96, time=0))
            track.append(MidiMessage('note_off', note=note_num, velocity=96, time=note_time))

        # 保存midi文件
        await loop.run_in_executor(None, mid.save, tmp_midi_path)

        # 转换为mp3文件
        res_code = await midi_to_audio(tmp_midi_path, tmp_mp3_path)

        # 如果转换成功则读取并将音乐转化为base64格式, 否则返回错误信息
        if res_code == 0:
            async with aiofiles.open(tmp_mp3_path, 'rb') as f:
                content = await f.read()
                base64_str = base64.b64encode(content).decode()
                base64_str = base64_str if "base64://" in base64_str else "base64://" + base64_str
                errcode = 0
        else:
            errcode = 4

        # 删除临时文件
        try:
            loop.run_in_executor(None, os.remove, tmp_midi_path)
            loop.run_in_executor(None, os.remove, tmp_mp3_path)
        except:
            pass

    if errcode == 0:
        res_msg = Message(MessageData.record(file=base64_str))
    else:
        res_msg = Message(MessageData.text(errors_info.get(errcode)))

    return res_msg


if __name__ == "__main__":
    import asyncio

    handle_msg = HandleMsg()
    handle_msg.command_args = {
        "command_object": {
            "value": "1. 7 6 5 6-- 6 5 4 2 3-- 2-- 1 .7 1 3 2-- .7 .5 .6--- 6-- 7--- 1. 7 6 5 6-- 6 5 4 2 3-- 2-- 1 .7 1 3 2-- 3 6--- 1 2 3 6-- 5 5B 2 3--- 3 5 6-- 7-- 5--- 3 4 3 4 6 5--- 1 .7 1 3 2-- .7 .5 .6--- 1 .7 1 3 2-- .7 .5 .6--- 1 2 3 6-- 5 5B 2 3--- 3 5 6 7-- 5--- 3 4 3 4 6 5--- 1 .7 1 3 2-- .7 .5 .6---"
        },
        "bpm": {"value": "120"},
        "instrument": {"value": "0"},
    }
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(generate_music(handle_msg))
    print(res)
