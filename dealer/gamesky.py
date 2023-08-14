# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/7 下午10:28
import json
import pathlib
import re
from typing import Any

import aiohttp
from lxml import etree

from model import GameskyPost
from text_processor import GameskyTextProcessor
from .interface import IDealer


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

    async def process_response_all_tag(self, response: aiohttp.ClientResponse) -> Any:
        """
        保留所有有用tag里的内容
        """
        text = await response.text(encoding=self.encoding, errors="ignore")  # 忽略非法字符，默认“strict”会抛出异常
        html = etree.HTML(text=text)
        processor = GameskyTextProcessor(html)
        content_list = processor.get_text()
        content: str = "\n".join(content.strip() for content in content_list if content)
        return content

    async def process_localize(self, post: GameskyPost) -> GameskyPost:
        save_dir = pathlib.Path("./results")
        if not save_dir.exists():
            save_dir.mkdir()

        # save_path = save_dir / f"{post.title}.json"
        # with save_path.open("w", encoding="utf-8") as f:
        #     json.dump(post.json, f, ensure_ascii=False, indent=4)

        # 改为txt存储
        save_path = save_dir / f"{post.title}.txt"
        txt = post.title + ' ##>>## ' + post.content
        with save_path.open("w", encoding="utf-8") as f:
            f.write(txt)
        return post

    async def deal(self):
        """
        不会存在post不存在url的情况下吧，我规定了一定要传入url的
        但是url是可能不合理的
        """
        async with self.session.get(url=self.post.url) as response:
            # content = await self.process_response(response=response)
            content = await self.process_response_all_tag(response=response)
            self.post.content = content
            if len(self.post.content) > 100:
                return await self.process_localize(post=self.post)
            else:
                return self.post


if __name__ == "__main__":
    pass
