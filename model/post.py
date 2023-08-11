# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/7 下午10:29

import datetime
from abc import ABCMeta
from typing import Optional

import pytz
from attrs import define, field

__all__ = (
    "IPost",
    "GameskyPost",
)


@define
class IPost(metaclass=ABCMeta):
    pass


@define
class GameskyPost(IPost):
    title: str = field()
    title_img: Optional[str] = field(repr=False)
    url: str = field()
    overview: str = field(repr=False)
    time: str = field()

    timezone = pytz.timezone("Asia/Shanghai")  # 需要和GameskyGenerator的timezone一致，这里写死，大概率不用修改
    _content: str = field(default=None, repr=False)

    @property
    def time_datetime(self) -> datetime.datetime:
        return datetime.datetime.strptime(self.time, "%Y-%m-%d").astimezone(tz=self.timezone)

    @property
    def details(self) -> dict:
        return {
            "title": self.title,
            "title_img": self.title_img,
            "url": self.url,
            "overview": self.overview,
            "time": self.time,
        }

    @property
    def content(self) -> str:
        """
        不做太多处理
        """
        if self._content is None:
            raise AttributeError("content is not set yet")
        else:
            return self._content

    @content.setter
    def content(self, content: str):
        self._content = content

    @property
    def json(self) -> dict:
        return {
            "title": self.title,
            "title_img": self.title_img,
            "url": self.url,
            "overview": self.overview,
            "time": self.time,
            "content": self.content,
        }


if __name__ == "__main__":
    pass
