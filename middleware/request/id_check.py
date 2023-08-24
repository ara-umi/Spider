from model import GameskyPost
from .interface import IIDChecker
import pathlib
import json


class IDChecker(IIDChecker):
    def __init__(self, post_list: list[GameskyPost], id_list_path: str = "./record/id_list.json"):
        self.post_list = post_list
        self.id_list: set = set()
        self.id_list_path = id_list_path

    def __call__(self):
        # 检查id记录是否存在，不存在就新建集合
        file_path = pathlib.Path(self.id_list_path)
        save_path = pathlib.Path("./record/")
        if not save_path.exists():
            save_path.mkdir()
        if file_path.exists():
            with open(file_path, 'r') as json_file:
                loaded_id = json.load(json_file)
            # 将加载的数据转换为集合
            self.id_list = set(loaded_id)
        else:
            self.id_list = set()
        # id已经存在的post被丢弃
        posts_to_remove = []
        for post in self.post_list:
            if post.post_id in self.id_list:
                print(f"post id: {post.post_id} already viewed.")
                posts_to_remove.append(post)
        for post in posts_to_remove:
            self.post_list.remove(post)
        return self.post_list

    def save_each_post_id(self, post: GameskyPost):
        self.id_list = set(self.id_list)
        self.id_list.add(post.post_id)
        self.id_list = list(self.id_list)
        with open(pathlib.Path(self.id_list_path), 'w') as json_file:
            json.dump(self.id_list, json_file)

    def post_id_check(self, post):
        # 检查id记录是否存在，不存在就新建集合
        file_path = pathlib.Path(self.id_list_path)
        save_path = pathlib.Path("./record/")
        if not save_path.exists():
            save_path.mkdir()
        if file_path.exists():
            with open(file_path, 'r') as json_file:
                loaded_id = json.load(json_file)
            # 将加载的数据转换为集合
            self.id_list = set(loaded_id)
        else:
            self.id_list = set()

        if post.post_id in self.id_list:
            print(f"post id: {post.post_id} already viewed.")
            return False
        return True
