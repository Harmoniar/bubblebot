import asyncio

from loguru import logger


DEFAULT_SOUND_FONT_PATH = 'resources/lib/Default_MuseScore.sf2'
DEFAULT_SAMPLE_RATE = 44900

# 将midi文件转化为mp3
async def midi_to_audio(midi_file_path: str, audio_file_path: str, sound_font_path: str = DEFAULT_SOUND_FONT_PATH, sample_rate: int = DEFAULT_SAMPLE_RATE):
    cmd = f"fluidsynth -ni {sound_font_path} {midi_file_path} -F {audio_file_path} -r {sample_rate}"
    res = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    # 有错误输出代表转换失败, 没有错误输出代表转换成功
    stdout, stderr = await res.communicate()

    if (not stderr) or (stderr.decode().startswith("fluidsynth: warning:")):
        errcode = 0
    else:
        logger.error(f"MID文件转换为MP3文件时出错, 错误信息: {stderr}")
        errcode = 1
    return errcode
