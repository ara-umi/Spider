import urllib.parse
from functools import wraps
import aiohttp
from typing import Optional, NoReturn, Callable
import asyncio


class CheckPostWrapper(object):

    def __call__(self, post_generator_from_response: Callable):
        @wraps(post_generator_from_response)
        async def async_wrapped(obj_self, response: aiohttp.ClientResponse):
            async for post in post_generator_from_response(obj_self, response=response):
                if obj_self.start_datetime <= post.time_datetime <= obj_self.end_datetime:
                    yield post
                elif post.time_datetime > obj_self.start_datetime:
                    continue
                else:
                    raise Stop()

        return async_wrapped


class ReachMaxRetryError(Exception):
    pass


class Stop(Exception):
    pass


class RetryWrapper(object):

    def __init__(self, max_retry: int = 3, sleep_seconds: int = 1):
        self.max_retry = max_retry
        self.sleep_seconds = sleep_seconds

    def __call__(self, get_response: Callable):
        @wraps(get_response)
        async def async_wrapped(obj_self, url: str, session: aiohttp.ClientSession):
            retry: int = 0
            while retry <= self.max_retry:
                try:
                    response: aiohttp.ClientResponse = await get_response(obj_self, url=url, session=session)
                    """
                    可以在这里添加response状态检查
                    也可以重新写一个类叫CheckResponseWrapper
                    """
                    return response
                except aiohttp.ClientError as e:
                    print(f"Aiohttp ClientError：{e.__class__.__name__}: {str(e)}, url: {url}")  # 这里最好做成log
                    await asyncio.sleep(self.sleep_seconds)
                    retry += 1
                    print(f"retry: {retry}, url: {url}")

            raise ReachMaxRetryError(f"retry: {retry}, url: {url}")

        return async_wrapped
