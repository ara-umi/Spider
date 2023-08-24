from flask import Flask, request, jsonify
import datetime
import asyncio
from get_data_auto_update import main
from middleware.utils.import_sql import import_data_to_sql


def get_data_select_page(start_time: int, end_time: int = None, start_page: int = 1):
    # Your existing function code
    input_date = datetime.datetime.strptime(str(start_time), "%Y%m%d")
    if end_time:
        end_date = datetime.datetime.strptime(str(end_time), "%Y%m%d")
    else:
        end_date = datetime.datetime.now()
    start_datetime = datetime.datetime(year=input_date.year, month=input_date.month, day=input_date.day)
    end_datetime = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    # 获取单机游戏攻略
    asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, start_page, gl_class=18,
                                                     id_list_path="./record/id_list_new.json"))
    # 手游攻略
    asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, start_page, gl_class=21114,
                                                     id_list_path="./record/id_list_new.json"))
    # 入库
    import_data_to_sql('./json_results_new')
def get_data():
    start_time = int(input("Enter start date (YYYYMMDD): "))
    end_time_input = input("Enter end date (YYYYMMDD) or leave empty for current date: ")

    if end_time_input:
        end_time = int(end_time_input)
    else:
        end_time = int(datetime.datetime.now().strftime("%Y%m%d"))

    get_data_select_page(start_time, end_time)


if __name__ == "__main__":
    get_data()
