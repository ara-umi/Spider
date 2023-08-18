import asyncio
import datetime
import time
from main import main


def get_data_auto_update(interval: int = 30):
    while True:
        start_datetime = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time(0, 0, 0))
        end_datetime = datetime.datetime.today()
        asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime))

        # embedding + FAISS merge
        # add to sql

        # 定时更新打印
        remaining_time = interval * 60
        while remaining_time > 0:
            minutes, seconds = divmod(remaining_time, 60)
            hours, minutes = divmod(minutes, 60)
            print(f"下一次更新将在 {hours:02d}:{minutes:02d}:{seconds:02d} 后进行")
            time.sleep(1)
            remaining_time -= 1
