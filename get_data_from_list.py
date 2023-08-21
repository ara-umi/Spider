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
from middleware.utils.load_post_list import PostListLoader


async def get_data_from_list():
    # 保存post_list
    post_list_loader = PostListLoader(file_path="./record/2017.json")
    post_list = post_list_loader()
    id_checker = IDChecker(post_list)
    post_list = id_checker()
    session = aiohttp.ClientSession()  # 之后session要做成注入参数
    for post in post_list:  # 这里后期要做并发
        deal = GameskyDealer(post=post, session=session)  # 这里后期post不能做成初始化参数
        post = await deal(raw=True, sleep_time=0.03)
        downloader = Downloader(post=post)
        await downloader.download_txt(path='./txt_results')
        await downloader.download_json(path='./json_results')
        # 保存到本地后才写入post_id
        id_checker.save_each_post_id(post)
    await session.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(get_data_from_list())
