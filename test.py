# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:44
import datetime
import unittest

from generator import GameskyPost, GameskyGenerator


class SpiderTest(unittest.IsolatedAsyncioTestCase):
    async def testGameskyGenerator(self):
        """
        没做嵌套并发
        拿到post_list再后续做逻辑并发吧
        """
        start_datetime = datetime.datetime(year=2023, month=8, day=1)
        end_datetime = datetime.datetime(year=2023, month=8, day=5)

        generator = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime)

        post_list: list[GameskyPost] = []
        async for post in generator.generate():
            post_list.append(post)

        for post in post_list:
            print(post)


if __name__ == "__main__":
    pass
