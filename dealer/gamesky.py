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

    def _process_p_blank(self, p: etree.Element) -> str:
        """
        不带任何属性的p标签，内含文本
        暂时考虑异常处理
        """
        text = p.xpath("./text()")[0]

        """
        应该单开一个类叫process_text
        """

        skips = (
            re.compile(r"\s*更多相关内容请关注.*?"),
            re.compile(r"\s*责任编辑.*?")
        )
        for skip in skips:
            if skip.match(text):
                return ""

        return text

    def _process_p_image(self, p: etree.Element) -> str:
        """
        带有class=GsImageLabel的p标签，下面的a标签的href属性是图片地址
        """
        return p.xpath("./a/@href")[0]

    def process_p(self, p: etree.Element) -> str:
        """
        目前包括以下情况
        1、不带任何属性的p标签，内含文本
        2、带有class=GsImageLabel的p标签，下面的a标签的href属性是图片地址

        不包括以下情况
        视频
        小标题
        ...
        """
        attribute_dict: dict = dict(p.attrib)
        match attribute_dict:
            case {"class": "GsImageLabel", **extra}:
                return self._process_p_image(p=p)
            case _:  # 空字典
                return self._process_p_blank(p=p)

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

    async def process_localize(self, post: GameskyPost) -> GameskyPost:
        save_dir = pathlib.Path("./results")
        if not save_dir.exists():
            save_dir.mkdir()

        save_path = save_dir / f"{post.title}.json"
        with save_path.open("w", encoding="utf-8") as f:
            json.dump(post.json, f, ensure_ascii=False, indent=4)

        return post

    async def deal(self):
        """
        不会存在post不存在url的情况下吧，我规定了一定要传入url的
        但是url是可能不合理的
        """

        async with self.session.get(url=self.post.url) as response:
            content = await self.process_response(response=response)
            self.post.content = content
            return await self.process_localize(post=self.post)


if __name__ == "__main__":
    pass
