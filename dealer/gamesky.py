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


class GameskyDealer(IDealer):
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

    async def process_response(self, response: aiohttp.ClientResponse) -> Any:
        text = await response.text(encoding=self.encoding)
        html = etree.HTML(text=text)
        # 正文目前来看是在Mid2L_con里面
        mid2l_con = html.xpath("//div[@class='Mid2L_con']")[0]
        # 内容都在下面的p标签里面
        p_list = mid2l_con.xpath("./p")
        content_list: list[str] = []
        for p in p_list:
            res = self.process_p(p=p)
            content_list.append(res)

        content: str = "\n".join(content for content in content_list if content)
        return content


    async def process_response_all_tag(self, response: aiohttp.ClientResponse, raw: bool) -> Any:
        """
        保留所有有用tag里的内容，添加多页处理逻辑
        """
        text = await response.text(encoding=self.encoding, errors="ignore")  # 忽略非法字符，默认“strict”会抛出异常
        html = etree.HTML(text=text)
        # 获取网页的原始内容和过滤后的内容
        processor = GameskyTextProcessor(html)
        content_list = processor.get_clean_content()
        raw_content = processor.get_raw_content() if raw else ""
        content: str = "\n".join(content.strip() for content in content_list if content)

        # 获取下一页的链接
        next_page_link = processor.get_next_page_link()
        return raw_content, content, next_page_link

    async def __call__(self, raw: bool = False, sleep_time: float = 0.5):
        """
        不会存在post不存在url的情况下吧，我规定了一定要传入url的
        但是url是可能不合理的
        保留所有有用tag里的内容，添加多页处理逻辑
        """
        # 缓存
        url = self.post.url
        all_pages_content = ""
        all_pages_raw_content = ""
        while url:
            try:
                # url不断迭代，筛选的是text为下一页的url，最后一页的url为None，跳出循环
                response: aiohttp.ClientResponse = await self.get_response(url=url, session=self.session)
                raw_content, content, next_page_link = await self.process_response_all_tag(response=response, raw=raw)
                all_pages_content += content
                if raw:
                    all_pages_raw_content += raw_content
                url = next_page_link
                # print(f"sleeping for {sleep_time}s……")
                time.sleep(sleep_time)
            except ReachMaxRetryError as e:
                """
                这里可以写达到最大重试次数后的存储逻辑
                """
                self.save_err_links(url)
                continue
            except Stop:
                break
        self.post.content = all_pages_content
        self.post.raw = all_pages_raw_content
        return self.post

    def save_err_links(self, link, save_path="./record/err_links.txt"):
        with open(save_path, 'a+') as f:
            f.write(f"{link}\n")


if __name__ == "__main__":
    pass
