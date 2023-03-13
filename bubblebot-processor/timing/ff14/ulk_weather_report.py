import time
import ctypes
import math
from datetime import datetime, timedelta
from loguru import logger
from core import manager
from lib.collections import SendMsg, Message, MessageData

# 防止天气连着出现时, 报多次已进入XX天气
LAST_NOTICE_MSG = None

class ULKWeatherReport:
    EORZEA_CLOCK_RATIO = 1440 / 70
    EORZEA_AREA_WEATHER = {
        "wind": {
            "name": "优雷卡-常风之地",
            "weather_rate": [
                {"rate": 30, "weather": "晴朗"},
                {"rate": 30, "weather": "强风"},
                {"rate": 30, "weather": "暴雨"},
                {"rate": -1, "weather": "小雪"},
            ],
        },
        "ice": {
            "name": "优雷卡-恒冰之地",
            "weather_rate": [
                {"rate": 10, "weather": "晴朗"},
                {"rate": 18, "weather": "薄雾"},
                {"rate": 18, "weather": "热浪"},
                {"rate": 18, "weather": "小雪"},
                {"rate": 18, "weather": "暴雷"},
                {"rate": -1, "weather": "暴雪"},
            ],
        },
        "fire": {
            "name": "优雷卡-涌火之地",
            "weather_rate": [
                {"rate": 10, "weather": "晴朗"},
                {"rate": 18, "weather": "热浪"},
                {"rate": 18, "weather": "打雷"},
                {"rate": 18, "weather": "暴雪"},
                {"rate": 18, "weather": "灵风"},
                {"rate": -1, "weather": "小雪"},
            ],
        },
        "water": {
            "name": "优雷卡-丰水之地",
            "weather_rate": [
                {"rate": 12, "weather": "晴朗"},
                {"rate": 22, "weather": "暴雨"},
                {"rate": 22, "weather": "妖雾"},
                {"rate": 22, "weather": "雷雨"},
                {"rate": -1, "weather": "小雪"},
            ],
        },
    }

    @property
    def current_et_timestamp(self):
        return time.time() * 1000 * self.EORZEA_CLOCK_RATIO

    @property
    def current_et_datetime(self):
        return self.millitimestamp_to_datetime(self.current_et_timestamp)

    def _get_weather_seeds(self, quantity: int):
        weather_seeds = []
        for i in range(quantity):
            # 艾欧泽亚时间+8小时
            itimestamp = self.current_et_timestamp + (i * 8) * 3600000
            itime = self.millitimestamp_to_datetime(itimestamp)
            ihour = int(itime.strftime("%H"))
            step1 = math.floor(itimestamp / 86400000) * 100 + (ihour + 8 - ihour % 8) % 24
            step2 = self.unsigned_right_shitf(step1 << 11 ^ step1, 1) * 2
            step3 = self.unsigned_right_shitf(self.unsigned_right_shitf(step2, 8) ^ step2, 1) * 2
            seed = step3 % 100
            weather_seeds.append(seed)
        return weather_seeds

    def _get_forecast(self, island: str, quantity: int):
        '''获取天气'''

        # [{"local_time":..., "et_time":..., "weather":...},...]
        weather_report = []

        forecast = []
        areaRateData = self.EORZEA_AREA_WEATHER.get(island)
        for seed in self._get_weather_seeds(quantity):
            for r in areaRateData.get("weather_rate"):

                if r.get("rate") == -1:
                    weather = r.get("weather")
                    break
                elif seed < r.get("rate"):
                    weather = r.get("weather")
                    break
                else:
                    seed -= r.get("rate")
            if weather:
                forecast.append(weather)
            else:
                forecast.append("N/A")

        base_time = self.millitimestamp_to_datetime(self.current_et_timestamp)
        base_time_hour = int(base_time.strftime("%H"))
        base_time = base_time.replace(hour=base_time_hour - base_time_hour % 8, minute=0, second=0, microsecond=0)

        for i, weather_name in enumerate(forecast):
            weather_et_time = base_time + timedelta(hours=i * 8)
            weather_local_time = math.floor((weather_et_time - datetime(1970, 1, 1)).total_seconds() * 1000 / self.EORZEA_CLOCK_RATIO) + 1
            weather_local_time = self.millitimestamp_to_datetime(weather_local_time) + timedelta(hours=8)
            weather_report.append({"local_time": weather_local_time, "et_time": weather_et_time, "weather": weather_name})

        return weather_report

    def get_weather_report(self, quantity: int = 48):
        weather_report = {}
        island_list = ["wind", "ice", "fire", "water"]
        for i in island_list:
            weather_report[i] = self._get_forecast(i, quantity)
        return weather_report

    @staticmethod
    def unsigned_right_shitf(n, i):
        '''兼容 js 的 >>> 位移使用'''

        def int_overflow(val):
            maxint = 2147483647
            if not -maxint - 1 <= val <= maxint:
                val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
            return val

        # 数字小于0，则转为32位无符号uint
        if n < 0:
            n = ctypes.c_uint32(n).value
        # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移
        if i < 0:
            return -int_overflow(n << abs(i))
        # print(n)
        return int_overflow(n >> i)

    @staticmethod
    def millitimestamp_to_datetime(timestamp: float):
        '''毫秒级时间戳转datetime对象'''
        return datetime(1970, 1, 1) + timedelta(milliseconds=timestamp)


async def report(admin_robot_id: str, timing_config: dict):

    group_list = timing_config.get("group")
    # 如果( 天气时间 - 地球时间 )相减刚好等于这里面的数, 则会告警, 但必须每隔1分钟执行一次该定时任务才会准确
    notice_countdown_time = timing_config.get("notice_countdown_time")
    #require_notice_weather = {"ice": ["暴雪", "薄雾"]}
    require_notice_weather = timing_config.get("require_notice_weather")


    ulk_weather_report = ULKWeatherReport()
    weather_report = ulk_weather_report.get_weather_report()

    island_weather = {"wind": {}, "ice": {}, "fire": {}, "water": {}}

    island_map = {"ice": "冰岛", "fire": "涌火之地", "water": "水岛", "wind": "风岛"}

    for island in weather_report:
        if island not in require_notice_weather:
            continue

        for forecast in weather_report.get(island):
            weather = forecast.get("weather")
            if (weather in require_notice_weather.get(island)) and (weather not in island_weather.get(island)):
                island_weather[island][weather] = forecast

    # 仅留下有数据的岛
    island_weather = {k: v for k, v in island_weather.items() if v}

    weather_msg_list = []
    for island, weather in island_weather.items():
        for weather_name, data in weather.items():
            island_name = island_map.get(island)

            now_datetime = datetime.now()
            weather_datetime = data.get("local_time")

            if weather_datetime <= now_datetime:

                difference_time = now_datetime - weather_datetime
                difference_minute = int(difference_time.seconds / 60)
                # 如果天气分钟时间等于地球分钟时间则发送已进入的通知
                if difference_minute == 0:
                    weather_msg_list.append("★ {}已进入【{}】天气".format(island_name, weather_name))

            else:

                difference_time = weather_datetime - now_datetime
                difference_minute = int(difference_time.seconds / 60)
                if difference_minute in notice_countdown_time:
                    weather_msg_list.append("★ {}下一个【{}】天气在 {} 分钟后".format(island_name, weather_name, difference_minute))

    if not weather_msg_list:
        return

    msg = "ULK好天气小助手提醒您：\n"
    msg += "\n".join(weather_msg_list)

    # 防止天气连着出现时, 报多次已进入XX天气
    # 只有在与上个天气通知的内容不同时，才会通知
    global LAST_NOTICE_MSG
    if msg == LAST_NOTICE_MSG:
        return
    else:
        LAST_NOTICE_MSG = msg

    for group_id in group_list:

        send_msg = SendMsg(
            from_type="group",
            group_id=int(group_id),
            send_messages=Message(MessageData.text(msg)),
            process_time="该定时功能不记录",
            time_stamp=int(time.time()),
        )

        # 推送至发送队列
        logger.info(f"调用定时任务功能成功, 推送至发送队列: ROBOT [{admin_robot_id}] - {send_msg}")
        await manager.robot_process_manager.push(admin_robot_id, send_msg)

        time.sleep(1)
