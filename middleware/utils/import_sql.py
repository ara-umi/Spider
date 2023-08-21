import os
import json
import mysql.connector
from mysql.connector import IntegrityError
from tqdm import tqdm


def import_data_to_sql(json_folder):
    # 连接到MySQL数据库
    conn = mysql.connector.connect(
        host="192.168.1.222",
        user="dufei",
        password="dufei123",
        database="ali213",
    )
    cursor = conn.cursor()

    # 遍历包含JSON文件的文件夹
    for filename in tqdm(os.listdir(json_folder)):
        try:
            if filename.endswith('.json'):
                with open(os.path.join(json_folder, filename), 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                    # 提取JSON中的属性
                    id = data['id']
                    title = data['title']
                    title_img = data['title_img']
                    url = data['url']
                    overview = data['overview']
                    time = data['time']
                    content = data['content']
                    raw = data['raw']

                    # 插入数据到数据库
                    insert_query = "INSERT INTO gl_ym (id, title, title_img, url, overview, time, content, raw) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    values = (id, title, title_img, url, overview, time, content, raw)
                    cursor.execute(insert_query, values)
                    conn.commit()
        except IntegrityError as e:
            # 处理主键重复异常
            print(f"ID {id} 已存在，跳过插入。")
            conn.rollback()  # 回滚事务以便继续下一个数据的插入
    # 关闭数据库连接
    conn.close()
