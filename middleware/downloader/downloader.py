import json
import pathlib
import re

from .interface import IDownloader
from model import GameskyPost


class Downloader(IDownloader):
    def __init__(self, post: GameskyPost):
        self.post = post

    async def download_txt(self, path: str, threshold: int = 100):
        """
        txt格式存储到指定路径
        """
        if len(self.post.content) > threshold:
            if path == "":
                path = pathlib.Path('./txt_results')
            else:
                path = pathlib.Path(path)
            if not path.exists():
                path.mkdir()
            # check title's '\'
            # 加入\\删除一部分标题中的“\”符号
            self.post.title = re.sub(r'[\/:*?"<>|\\]', '', self.post.title)
            self.post.title = re.sub(r'\t', '', self.post.title)
            # 处理后的干净文本为txt存储，方便对接之前的代码生成向量数据库
            save_path = path / f"{self.post.title}.txt"
            txt = self.post.title + ' ##>>## ' + self.post.content
            with save_path.open("w", encoding="utf-8") as f:
                f.write(txt)
            print(f'Saved as .txt: {self.post.title}, time: {self.post.time}')
        else:
            pass

    async def download_json(self, path: str, threshold: int = 100):
        """
        txt格式存储到指定路径
        """
        if len(self.post.content) > threshold:
            if path == "":
                path = pathlib.Path('./json_results')
            else:
                path = pathlib.Path(path)
            if not path.exists():
                path.mkdir()
            # check title's '\'
            # 加入\\删除一部分标题中的“\”符号
            self.post.title = re.sub(r'[\/:*?"<>|\\]', '', self.post.title)
            self.post.title = re.sub(r'\t', '', self.post.title)
            # 原始数据存json，备用
            save_path = path / f"{self.post.title}.json"
            with save_path.open("w", encoding="utf-8") as f:
                json.dump(self.post.json, f, ensure_ascii=False, indent=4)
            print(f'Saved as .json: {self.post.title}, time: {self.post.time}')
        else:
            pass
