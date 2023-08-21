# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:44

import datetime
import json
import pathlib
import time

import aiohttp
import asyncio
from dealer import GameskyDealer
from generator import GameskyGenerator
from model import GameskyPost
from middleware.downloader import Downloader
from middleware.request import IDChecker
from middleware.utils.save_post_list import PostListSaver


async def main(start_datetime: datetime, end_datetime: datetime, start_page: int = 1):
    year = start_datetime.year
    generate = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime, start_page=start_page)
    post_list = []
    async for post in generate():
        post_list.append(post)
        print(post)
    # 保存post_list
    post_list_saver = PostListSaver(post_list)
    post_list_saver(file_path=f"./record/{year}.json")

    # session = aiohttp.ClientSession()  # 之后session要做成注入参数
    # for post in post_list:  # 这里后期要做并发
    #     deal = GameskyDealer(post=post, session=session)  # 这里后期post不能做成初始化参数
    #     post = await deal(raw=True, sleep_time=0.03)
    #     downloader = Downloader(post=post)
    #     await downloader.download_txt(path='./txt_results')
    #     await downloader.download_json(path='./json_results')
    #     # 保存到本地后才写入post_id
    #     id_checker.save_each_post_id(post)
    # await session.close()


def main_test():
    start_datetime = datetime.datetime(year=2000, month=7, day=1)
    end_datetime = datetime.datetime(year=2023, month=8, day=1)
    generate = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime)
    kwargs = {
        'post_id': 856598,
        "title": "《战国之野望》云游四海玩法全攻略",
        "title_img": "null",
        "url": "https://www.gamersky.com/handbook/201701/856598.shtml",
        "overview": "　　《战国之野望》云游四海玩法全攻略，云游四海功能详解。\n游民星空《战国之野望》游戏最新区服：点击进入\n\n云游四海功能描述\n　　云游四海为ROLL骰子的游戏\n　　点",
        "time": "2017-01-09"}
    post = GameskyPost(**kwargs)

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession()
    dealer = GameskyDealer(post=post, session=session)
    post = loop.run_until_complete(dealer(raw=True))
    downloader = Downloader(post=post)
    loop.run_until_complete(downloader.download_txt(path='./txt_results'))
    loop.run_until_complete(downloader.download_json(path='./json_results'))
    loop.run_until_complete(session.close())


def get_data_select_page(start_time: int, end_time: int, start_page: int = 1):
    input_date = datetime.datetime.strptime(str(start_time), "%Y%m%d")
    end_date = datetime.datetime.strptime(str(end_time), "%Y%m%d")
    start_datetime = datetime.datetime(year=input_date.year, month=input_date.month, day=input_date.day)
    end_datetime = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    asyncio.get_event_loop().run_until_complete(main(start_datetime, end_datetime, start_page))


if __name__ == "__main__":
    get_data_select_page(20180101, 20190101, start_page=1325)
    # main_test()
