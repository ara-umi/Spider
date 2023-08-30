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
from typing import Optional, NoReturn, Callable

import aiohttp
import pytz
from lxml import etree

from model import GameskyPost
from .interface import IGenerator
from middleware.utils.wrapper import CheckPostWrapper, RetryWrapper, ReachMaxRetryError, Stop


class CustomException(Exception):
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
                 start_page: int = 1, gl_class: int = 18, sources: str = 'gamersky'):
        """
        不传入end_datetime的话，就只爬取start_datetime这一天的数据
        """
        self.sources = sources
        self.gl_class = gl_class
        # 18是攻略数据库，19秘籍
        # 20354是奖杯成就数据库，20352是疑难数据库 20351游戏资料
        # 21114手游攻略，保持更新，20994老手游攻略，22年就不更新了
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
        if con.xpath("./div[@class='tme']"):
            tme = con.xpath("./div[@class='tme']")[0]
        else:
            return "2077-07-07"
        tme_time = tme.xpath("./div[@class='time']")[0] if tme.xpath("./div[@class='time']") else ""
        post_time = tme_time.xpath("./text()")[0] if tme_time.xpath("./text()") else ""
        return post_time


    def _process_link(self, li) -> NoReturn:
        """
        tme_time后面还有一个div，不知道干什么的
        """
        pass

    @CheckPostWrapper()
    async def post_generator_from_response(self, response: aiohttp.ClientResponse):
        """
        很神奇，它直接的返回竟然像一个json但是不是
        -> AsyncGenerator[GameskyPost]  返回值的标注我暂时没搞懂，就先不写
        """
        try:
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
                    sources=self.sources,
                )

                yield post
        except json.decoder.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # 在这里可以记录日志或者执行其他适当的处理
            raise CustomException("JSON decode error occurred")  # 引发自定义异常

    def shape_url(self, page) -> str:
        timestamp_ms = int(time.time() * 1e3)
        # 是一个随机数，不过网页上请求一直都是1830开头
        random_suffix = ''.join(random.choice("0123456789") for _ in range(20))
        callback = f"jQuery{random_suffix}_{timestamp_ms}"
        json_data = {
            "type": "updatenodelabel",
            "isCache": "true",
            "cacheTime": 60,
            "nodeId": str(self.gl_class),
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

    @RetryWrapper(max_retry=3, sleep_seconds=1)
    async def get_response(self, url: str, session: aiohttp.ClientSession):
        response: aiohttp.ClientResponse = await session.get(url=url)
        return response

    async def __call__(self):
        """
        可能需要一个异常处理就是当页数超过限制
        """
        page = self.start_page
        session = await self.create_session()
        while True:
            try:
                url: str = self.shape_url(page=page)
                response: aiohttp.ClientResponse = await self.get_response(url=url, session=session)
                async for post in self.post_generator_from_response(response):
                    yield post
                response.release()
                print(f"Page {page} done")
                page += 1
            except ReachMaxRetryError as e:
                self.save_err_pages(page)
                print(f"Page {page} reach max retry: {e}")
                page += 1
                continue
            except Stop:
                break
            except CustomException as ee:
                self.save_err_pages(page)
                print(f"Page {page} not load correctly: {ee}")
                page += 1
                continue
            except Exception as everye:
                self.save_err_pages(page)
                print(f"Page {page} not load correctly: {everye}")
                page += 1
                continue

        await self.release_session(session=session)

    def save_err_pages(self, page, save_path="./record/err_pages.txt"):
        with open(save_path, 'a+') as f:
            f.write(f"{page}\n")


if __name__ == "__main__":
    pass
