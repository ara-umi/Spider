from typing import List
from tqdm import tqdm

import json
from model import GameskyPost


class PostListLoader:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def __call__(self):
        post_list = []
        with open(self.file_path, 'r', encoding='utf-8') as jsonl_file:
            data = json.load(jsonl_file)
            for post_data in data:
                post = GameskyPost.from_json(post_data)
                post_list.append(post)
        return post_list
