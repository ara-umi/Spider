from model import GameskyPost
from .interface import IIDChecker
import pathlib
import json


class IDChecker(IIDChecker):
    def __init__(self, post_list: list[GameskyPost], ):
        self.post_list = post_list

    def __call__(self):
        # 检查id记录是否存在，不存在就新建集合
        file_path = pathlib.Path("./record/id_list.json")
        save_path = pathlib.Path("./record/")
        if file_path.exists():
            with open(file_path, 'r') as json_file:
                loaded_id = json.load(json_file)
            # 将加载的数据转换为集合
            id_list = set(loaded_id)
        else:
            save_path.mkdir()
            id_list = set()
        # id已经存在的post被丢弃
        posts_to_remove = []
        for post in self.post_list:
            if post.post_id in id_list:
                print(f"post id: {post.post_id} already viewed.")
                posts_to_remove.append(post)
            else:
                id_list.add(post.post_id)
        for post in posts_to_remove:
            self.post_list.remove(post)
        # 保存已经查过的集合
        id_list = list(id_list)
        with open(file_path, 'w') as json_file:
            json.dump(id_list, json_file)
        return self.post_list
