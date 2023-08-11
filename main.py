# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/4 下午11:44

import datetime
import aiohttp
import asyncio
from dealer import GameskyDealer
from generator import GameskyGenerator
from model import GameskyPost


def main():
    start_datetime = datetime.datetime(year=2023, month=8, day=3)
    end_datetime = datetime.datetime(year=2023, month=8, day=6)

    generator = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime)

    post_list = []

    async def process_posts():
        async for post in generator.generate():
            post_list.append(post)
            print(post.details)  # 会展示更多细节

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process_posts())

    for post in post_list:
        print(post)

    kwargs = {'title': '《博德之门3》巴尔神殿进入方法',
              'title_img': 'https://imgs.gamersky.com/upimg/new_preview/2023/08/06/origin_202308061627487960.jpg',
              'url': 'https://www.gamersky.com/handbook/202308/1628536.shtml',
              'overview': '《博德之门3》中巴尔神殿想要进入非常复杂，还不知道具体方法的玩家请看下面...',
              'time': '2023-08-06'}
    post = GameskyPost(**kwargs)

    session = aiohttp.ClientSession()

    dealer = GameskyDealer(post=post, session=session)
    post = loop.run_until_complete(dealer.deal())
    print(post.content)

    loop.run_until_complete(session.close())


async def main_example():
    start_datetime = datetime.datetime(year=2023, month=8, day=10)
    end_datetime = datetime.datetime(year=2023, month=8, day=10)
    generator = GameskyGenerator(start_datetime=start_datetime, end_datetime=end_datetime)
    post_list = []
    async for post in generator.generate():
        post_list.append(post)
        print(post)

    session = aiohttp.ClientSession()  # 之后session要做成注入参数
    for post in post_list:  # 这里后期要做并发
        dealer = GameskyDealer(post=post, session=session)  # 这里后期post不能做成初始化参数
        await dealer.deal()
    await session.close()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_example())
