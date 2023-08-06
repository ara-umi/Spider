# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:10

import json
import random
import re
import time
import urllib.parse
from typing import Optional

import aiohttp
from attrs import define, field
from lxml import etree

from .interface import IGenerator


@define
class GameskyPost(object):
    title: str = field()
    url: str = field()
    overview: str = field(repr=False)
    time: str = field()


class GameskyGenerator(IGenerator):
    """
    使用的ajax动态加载
    由于它数据库设计比较垃圾，大概率没有索引和分表，所以越往后的页数越慢
    """

    start_url = "https://db2.gamersky.com/LabelJsonpAjax.aspx?callback={callback}&jsondata={json_data}&_={timestamp_ms}"
    encoding = "utf-8"

    def __init__(self, start_page: int = 1, end_page: Optional[int] = None):
        self.start_page = start_page
        self.end_page = end_page

    def shape_url(self, page: int) -> str:
        timestamp_ms = int(time.time() * 1e3)
        # 是一个随机数，不过网页上请求一直都是1830开头
        random_suffix = ''.join(random.choice("0123456789") for _ in range(20))
        callback = f"jQuery{random_suffix}_{timestamp_ms}"
        json_data = {
            "type": "updatenodelabel",
            "isCache": "true",
            "cacheTime": 60,
            "nodeId": "18",  # 只能是18，其他的都不行
            "isNodeId": "true",
            "page": page
        }
        json_data_quote = urllib.parse.quote(str(json_data))
        url = self.start_url.format(
            callback=callback,
            json_data=json_data_quote,
            timestamp_ms=timestamp_ms
        )
        return url

    async def create_client(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def release_client(self, client: aiohttp.ClientSession):
        await client.close()

    async def process(self, response: aiohttp.ClientResponse) -> str:
        """
        很神奇，它直接的返回竟然像一个json但是不是
        """
        patter = re.compile(r"jQuery\d+_\d+\((?P<json>.*?)\);", flags=re.S)
        text = await response.text(encoding=self.encoding)
        match = patter.match(text)  # 这里掐头去尾才是一个json
        body = json.loads(match.group("json"))["body"]
        html = etree.HTML(body)

        li_list = html.xpath("//li")
        for li in li_list:
            # li里面有两个div，一个是img，一个是con

            # img里面存的是头图和图片标题
            img = li.xpath("./div[@class='img']")[0]
            img_a = img.xpath("./a")[0]
            title_image = img_a.xpath("./@href")[0]
            # title = img_a.xpath("./@title")[0]  # 图片标题其实不用管，是图片的注释

            # con里面存的是tit、txt、tme
            con = li.xpath("./div[@class='con']")[0]
            # tit里面存的是标题和链接
            con_tit = con.xpath("./div[@class='tit']")[0]
            title = con_tit.xpath("./a/text()")[0]
            url = con_tit.xpath("./a/@href")[0]
            # txt存的简介
            con_txt = con.xpath("./div[@class='txt']")[0]
            overview = con_txt.xpath("./text()")[0]
            # tme存的时间
            tme = con.xpath("./div[@class='tme']")[0]
            tme_time = tme.xpath("./div[@class='time']")[0]
            post_time = tme_time.xpath("./text()")[0]
            # 后面还有个div叫link，不知道干什么的

            post = GameskyPost(
                title=title,
                url=url,
                overview=overview,
                time=post_time
            )

            print(post)

    async def process_next_page(self, response: aiohttp.ClientResponse) -> str:
        """
        它的下一页很神奇，不是直接给你url，而是通过js加载的
        """
        text = await response.text(encoding=self.encoding)
        html = etree.HTML(text)
        # 主体在叫Page contentpage的div里
        div = html.xpath("//div[@class='Page contentpage']")[0]
        # 下面会有一个叫pagecss的span
        span = div.xpath("./span[@class='pagecss']")[0]
        # 下面会有很多a，第一个是前一页，第二是个本页，第三个是下一页
        # 其实下一页的class一定是p2，本页是p3，上一页是p1 previous
        a_next = span.xpath("./a")[2]
        url = a_next.xpath("./")

        """
        其实只能通过这个方法来是否有下一页，不能获取到url
        """

    async def generate(self) -> "str":
        """
        先测试一下第一页
        :return:
        """
        url = self.shape_url(page=1)
        async with aiohttp.request(method="GET", url=url) as response:
            return await self.process(response)


if __name__ == "__main__":
    pass
