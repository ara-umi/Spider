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
    generate = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime, start_page=start_page)
    post_list = []
    async for post in generate():
        post_list.append(post)
        print(post)
    # 这里读取id_list想根据已经有的id去除post_list存在的id，并不写入新的post_id
    id_checker = IDChecker(post_list)
    post_list = id_checker()
    # 保存post_list
    post_list_saver = PostListSaver(post_list)
    post_list_saver()

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
    start_datetime = datetime.datetime(year=2023, month=7, day=1)
    end_datetime = datetime.datetime(year=2023, month=8, day=1)
    generate = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime)
    kwargs = {
        'post_id': 1482021,
        'title': '《艾尔登法环》支线完成顺序速览 1.04版本NPC支线顺序推荐',
        'title_img': 'https://imgs.gamersky.com/upimg/new_preview/2023/08/06/origin_202308061627487960.jpg',
            'url': 'https://www.gamersky.com/handbook/202010/1327388.shtml',
        'overview': '《博德之门3》中巴尔神殿想要进入非常复杂，还不知道具体方法的玩家请看下面...',
        'time': '2023-08-06'}
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
    # get_data_select_page(20020101, 20190101, start_page=1336)
    get_data_select_page(20000101, 20190101, start_page=1933)
    # main_test()
