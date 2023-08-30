# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/7 下午10:28
import json
import pathlib
import re
import time
from typing import Any

import aiohttp
from lxml import etree

from model import GameskyPost
from text_processor import GameskyTextProcessor
from .interface import IDealer
from middleware.utils.wrapper import CheckPostWrapper, RetryWrapper, ReachMaxRetryError, Stop


class GameskyTitleDealer(IDealer):
    encoding = "utf-8"

    def __init__(self, post: GameskyPost, session: aiohttp.ClientSession):
        """
        这里还是硬性要求传入一个session，因为是一定要并发的
        只能说传入session会在post较少的情况下，代码量多一点
        其实还要考虑generator是否也需要传入session，并且把session的维护放到generator外
        """

        self.post = post
        self.session = session

    @RetryWrapper(max_retry=3, sleep_seconds=1)
    async def get_response(self, url: str, session: aiohttp.ClientSession):
        response: aiohttp.ClientResponse = await session.get(url=url)
        return response

    async def process_response_all_tag(self, response: aiohttp.ClientResponse, raw: bool) -> Any:
        """
        保留所有有用tag里的内容，添加多页处理逻辑
        """
        text = await response.text(encoding=self.encoding, errors="ignore")  # 忽略非法字符，默认“strict”会抛出异常
        html = etree.HTML(text=text)
        # 获取网页的原始内容和过滤后的内容
        processor = GameskyTextProcessor(html)
        # 获取游戏名
        game_name = processor.get_game_name()
        return game_name

    async def __call__(self, raw: bool = False, sleep_time: float = 0):
        """
        不会存在post不存在url的情况下吧，我规定了一定要传入url的
        但是url是可能不合理的
        保留所有有用tag里的内容，添加多页处理逻辑
        """
        # 缓存
        url = self.post.url
        game_title = ""
        try:
            response: aiohttp.ClientResponse = await self.get_response(url=url, session=self.session)
            game_title = await self.process_response_all_tag(response=response, raw=raw)
            time.sleep(sleep_time)
        except Exception as e:
            self.save_err_links(url)
        self.post.game_name = game_title
        return self.post

    def save_err_links(self, link, save_path="./record/err_links.txt"):
        with open(save_path, 'a+') as f:
            f.write(f"{link}\n")


if __name__ == "__main__":
    pass
