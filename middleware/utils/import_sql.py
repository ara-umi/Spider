import os
import json
from datetime import datetime

import mysql.connector
from mysql.connector import IntegrityError
from tqdm import tqdm
from model import GameskyPost


def check_waijian(cursor, table: str, name):
    query = f"SELECT id FROM {table} WHERE name = %s"
    cursor.execute(query, (name,))
    result = cursor.fetchone()  # 获取查询结果
    if result:
        result_id = result[0]
    else:
        # 在 game_name 表中插入新的 game_name
        create_time = datetime.now()
        insert_game_query = f"INSERT INTO {table} (name, create_time) VALUES (%s, %s)"
        cursor.execute(insert_game_query, (name, create_time))
        result_id = cursor.lastrowid
    return result_id


def import_data_to_sql(post: GameskyPost):
    # 连接到MySQL数据库
    conn = mysql.connector.connect(
        host="47.97.61.236",
        user="aigl",
        password="ziwah4ieL#9thoSi5koo",
        database="aigl",
    )
    cursor = conn.cursor()

    with open(f'./json_results_new/{post.title}.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        # 提取JSON中的属性
        post_id = data['post_id']
        title = data['title']
        title_img = data['title_img']
        url = data['url']
        overview = data['overview']
        time = data['time']
        content = data['content']
        raw = data['raw']
        create_time = data['create_time']
        status = data['status']
        game_name = data['game_name']
        game_id = check_waijian(cursor, 'game', game_name)
        platform = data['sources']
        platform_id = check_waijian(cursor, 'platform', platform)
        try:
            # 插入数据到数据库
            insert_query = "INSERT INTO gl " \
                           "(post_id, title, title_img, url, overview, time, content, raw, create_time, status, game_id, platform_id) " \
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            values = (post_id, title, title_img, url, overview, time, content, raw, create_time, status, game_id, platform_id)
            cursor.execute(insert_query, values)
            conn.commit()
            print(f'Import to sql: {post.title} 已导入数据库。')
        except IntegrityError as e:
            # 处理主键重复异常
            conn.rollback()  # 回滚事务以便继续下一个数据的插入
            raise
    conn.close()
