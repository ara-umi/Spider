from flask import Flask, request, jsonify
import datetime
import asyncio
from get_data_auto_update import main
from middleware.utils.import_sql import import_data_to_sql


def get_data_select_page(start_time: int, end_time: int = None, start_page: int = 1):
    if end_time:
        end_date = datetime.datetime.strptime(str(end_time), "%Y%m%d")
    else:
        end_date = datetime.datetime.now()
    if start_time:
        input_date = datetime.datetime.strptime(str(start_time), "%Y%m%d")
    else:
        input_date = datetime.datetime.combine(datetime.datetime.today().date(), datetime.time(0, 0, 0))
    start_datetime = datetime.datetime(year=input_date.year, month=input_date.month, day=input_date.day)
    end_datetime = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    # 获取单机游戏攻略
    asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, start_page, gl_class=18,
                                                     id_list_path="./record/id_list_new.json"))
    # 手游攻略
    asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, start_page, gl_class=21114,
                                                     id_list_path="./record/id_list_new.json"))

def get_data():
    start_time_input = input("输入日期 (YYYYMMDD) 留空则默认开始时间为今天凌晨0点: ")
    end_time_input = input("输入日期 (YYYYMMDD) 留空则默认结束时间为现在: ")

    if start_time_input:
        start_time = int(start_time_input)
    else:
        start_time = ''
    if end_time_input:
        end_time = int(start_time_input)
    else:
        end_time = ''

    get_data_select_page(start_time, end_time)


if __name__ == "__main__":
    get_data()
