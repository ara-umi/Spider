# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:44

import unittest

from generator import GameskyGenerator


class SpiderTest(unittest.IsolatedAsyncioTestCase):

    async def testGameskyGenerator(self):
        generator = GameskyGenerator(start_page=1, end_page=2)
        await generator.generate()


if __name__ == "__main__":
    pass
