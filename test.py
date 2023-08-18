# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:44

import datetime
import unittest

from dealer import GameskyDealer
from generator import GameskyGenerator
from model import GameskyPost


class SpiderTest(unittest.IsolatedAsyncioTestCase):
    async def testGameskyGenerator(self):
        """
        没做嵌套并发
        拿到post_list再后续做逻辑并发吧
        """
        start_datetime = datetime.datetime(year=2023, month=8, day=3)
        end_datetime = datetime.datetime(year=2023, month=8, day=6)

        generator = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime)

        post_list: list[GameskyPost] = []
        async for post in generator():
            post_list.append(post)
            # 动态展示
            # print(post)
            print(post.details)  # 会展示更多细节

        # 集中展示
        # for post in post_list:
        #     print(post)
        #     print(post.details)  # 会显示更多细节

    async def testGameskyDealer(self):
        kwargs = {'title': '《博德之门3》巴尔神殿进入方法',
                  'title_img': 'https://imgs.gamersky.com/upimg/new_preview/2023/08/06/origin_202308061627487960.jpg',
                  'url': 'https://www.gamersky.com/handbook/202308/1628547.shtml',
                  'overview': '《博德之门3》中巴尔神殿想要进入非常复杂，还不知道具体方法的玩家请看下面“丶易风雪”带来的《博德之门3》巴尔神殿进入方法，希望能够帮助大家。',
                  'time': '2023-08-06'}
        post = GameskyPost(**kwargs)

        import aiohttp
        session = aiohttp.ClientSession()

        dealer = GameskyDealer(post=post, session=session)
        post = await dealer()
        print(post.content)

        await session.close()


if __name__ == "__main__":
    pass
