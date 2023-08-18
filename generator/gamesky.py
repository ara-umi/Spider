# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:10
import datetime
import json
import random
import re
import time
import urllib.parse
from typing import Optional, NoReturn

import aiohttp
import pytz
from lxml import etree

from model import GameskyPost
from .interface import IGenerator


class LaterPostException(Exception):
    # print("指针位置还未到设定时间区间，继续检索……")
    pass


class EarlierPostException(Exception):
    """
    我们默认它是按照时间倒序的，所以这两种异常要分情况处理
    """
    pass


class ValidPost(Exception):
    pass


class GameskyGenerator(IGenerator):
    """
    使用的ajax动态加载
    由于它数据库设计比较垃圾，大概率没有索引和分表，所以越往后的页数越慢
    """

    start_url = "https://db2.gamersky.com/LabelJsonpAjax.aspx?callback={callback}&jsondata={json_data}&_={timestamp_ms}"
    encoding = "utf-8"
    start_page = 1
    timezone = pytz.timezone("Asia/Shanghai")

    def __init__(self, start_datetime: datetime.datetime, end_datetime: Optional[datetime.datetime] = None,
                 start_page: int = 1):
        """
        不传入end_datetime的话，就只爬取start_datetime这一天的数据
        """
        self.start_page = start_page
        self.start_datetime = self._format_input_datetime(input_datetime=start_datetime)
        self.end_datetime = self._format_input_datetime(end_datetime) \
            if end_datetime \
            else self._format_input_datetime(input_datetime=start_datetime)

        self.max_err_times = 3

        assert self.start_datetime <= self.end_datetime, "start_datetime must be less than or equal to end_datetime"
        assert self.end_datetime <= datetime.datetime.now(
            tz=self.timezone), "end_datetime must be less than or equal to now"

    async def create_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    async def release_session(self, session: aiohttp.ClientSession):
        await session.close()

    def _format_input_datetime(self, input_datetime: datetime.datetime) -> datetime.datetime:
        """
        只保留年月日
        """
        return datetime.datetime(
            year=input_datetime.year,
            month=input_datetime.month,
            day=input_datetime.day
        ).astimezone(tz=self.timezone)

    def _process_img(self, li: etree.Element) -> Optional[str]:
        try:
            img = li.xpath("./div[@class='img']/a/img/@src")[0]
            # img_title = li.xpath("./div[@class='img']/a/img/@alt")[0]  # 图片标题不重要，就没存，应该是和文章标题一样的
            return img

        # 是很有可能没有头图的
        except IndexError:
            return None

    def _process_id(self, url) -> int:
        post_id = int((re.search(r'(\d+)\.shtml', url)).group(1))
        return post_id

    def _process_title(self, li) -> str:
        """
        不能没有title吧
        """
        # con里面存的是tit、txt、tme
        con = li.xpath("./div[@class='con']")[0]
        # tit里面存的是标题和链接
        con_tit = con.xpath("./div[@class='tit']")[0]
        title = con_tit.xpath("./a/text()")[0]
        return title

    def _process_url(self, li) -> str:
        # con里面存的是tit、txt、tme
        con = li.xpath("./div[@class='con']")[0]
        # tit里面存的是标题和链接
        con_tit = con.xpath("./div[@class='tit']")[0]
        url = con_tit.xpath("./a/@href")[0]
        return url

    def _process_overview(self, li) -> Optional[str]:
        try:
            # con里面存的是tit、txt、tme
            con = li.xpath("./div[@class='con']")[0]
            # txt存的简介
            con_txt = con.xpath("./div[@class='txt']")[0]
            overview = con_txt.xpath("./text()")[0]
            return overview
        except IndexError:
            return None

    def _process_time(self, li) -> str:
        # con里面存的是tit、txt、tme
        con = li.xpath("./div[@class='con']")[0]
        # tme存的时间
        tme = con.xpath("./div[@class='tme']")[0]
        tme_time = tme.xpath("./div[@class='time']")[0]
        post_time = tme_time.xpath("./text()")[0]
        return post_time

    def _process_link(self, li) -> NoReturn:
        """
        tme_time后面还有一个div，不知道干什么的
        """
        pass

    async def process(self, response: aiohttp.ClientResponse):
        """
        很神奇，它直接的返回竟然像一个json但是不是
        -> AsyncGenerator[GameskyPost]  返回值的标注我暂时没搞懂，就先不写
        """
        patter = re.compile(r"jQuery\d+_\d+\((?P<json>.*?)\);", flags=re.S)
        text = await response.text(encoding=self.encoding)
        match = patter.match(text)  # 这里掐头去尾才是一个json
        body = json.loads(match.group("json"))["body"]
        html = etree.HTML(body)

        li_list = html.xpath("//li")
        for li in li_list:
            # for debug
            # print(etree.tostring(li, encoding="utf-8").decode("utf-8"))

            # li里面有两个div，一个是img，一个是con
            title = self._process_title(li=li)
            title_img = self._process_img(li=li)
            url = self._process_url(li=li)
            overview = self._process_overview(li=li)
            post_time = self._process_time(li=li)
            # 正则得到url后面的id
            post_id = self._process_id(url=url)

            post = GameskyPost(
                title=title,
                title_img=title_img,
                url=url,
                overview=overview,
                time=post_time,
                post_id=post_id,
            )

            yield post

    def shape_url(self, page) -> str:
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

    def post_check(self, post: GameskyPost) -> NoReturn:
        if self.start_datetime <= post.time_datetime <= self.end_datetime:
            raise ValidPost
        elif post.time_datetime > self.start_datetime:
            raise LaterPostException
        else:
            raise EarlierPostException

    async def __call__(self):
        """
        可能需要一个异常处理就是当页数超过限制
        """
        page = self.start_page
        session = await self.create_session()
        err_times = 0
        while True:
            try:
                url = self.shape_url(page=page)
                async with session.get(url=url) as response:
                    async for post in self.process(response):
                        try:
                            self.post_check(post=post)
                        except ValidPost:
                            yield post
                        except LaterPostException:
                            pass
                        except EarlierPostException:
                            print("指针位置的攻略早于设定时间区间，停止检索。")
                            await self.release_session(session=session)
                            return
                print(f"检索页数：{page}")
                page += 1
                err_times = 0
            except Exception as e:
                print("Error:", e)
                err_times += 1
                # 报错后默认重试 self.max_err_times 次，如果超过次数任异常，则跳过该page
                if err_times >= self.max_err_times:
                    self.save_err_pages(page)
                    print(f"page: {page}, err_times: {err_times}, saved!")
                    page += 1
                    err_times = 0

    def save_err_pages(self, page, save_path="./record/err_pages.txt"):
        with open(save_path, 'a+') as f:
            f.write(f"{page}\n")


if __name__ == "__main__":
    pass
