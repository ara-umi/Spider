from typing import List
from tqdm import tqdm

import json
from model import GameskyPost


class PostListSaver:
    
    def __init__(self, post_list: List[GameskyPost]):
        self.post_list = post_list
    
    def __call__(self, file_path: str = './record/post_list.json', **kwargs):
        result = [post.post_list_json for post in tqdm(self.post_list)]
        with open(file_path, 'w', encoding="utf-8") as jsonl_file:
            json.dump(result, jsonl_file, ensure_ascii=False, indent=4)
        print('Saving complete')