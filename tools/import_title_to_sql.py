from datetime import datetime
import os
import json
import mysql.connector
from mysql.connector import IntegrityError
from tqdm import tqdm
from model import GameskyPost


def import_title_to_sql():
    # 连接到MySQL数据库
    db_conn = mysql.connector.connect(
        host="47.97.61.236",
        user="aigl",
        password="ziwah4ieL#9thoSi5koo",
        database="aigl",
    )
    cursor = db_conn.cursor()

    # 遍历文件夹中的每个 JSON 文件
    folder_path = "../json_results_title"
    # 用于保存出现异常的文件名列表
    error_files = []
    for filename in tqdm(os.listdir(folder_path)):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(folder_path, filename), "r", encoding="utf8") as json_file:
                    data = json.load(json_file)
                    post_id = data.get("post_id")
                    game_name = data.get("game_name")
                    sources = data.get("sources")
                    create_time = datetime.now()
                    # 检查 post_id 是否存在
                    post_id_query = "SELECT id FROM gl WHERE post_id = %s"
                    cursor.execute(post_id_query, (post_id,))
                    post_id_result = cursor.fetchone()
                    if post_id_result:
                        # post_id 存在，继续检查 game_name 和 sources
                        # 检查 game_name 表中是否存在对应的值
                        game_query = "SELECT id FROM game WHERE name = %s"
                        cursor.execute(game_query, (game_name,))
                        game_result = cursor.fetchone()  # 获取查询结果
                        if game_result:
                            game_id = game_result[0]
                        else:
                            # 在 game_name 表中插入新的 game_name
                            insert_game_query = "INSERT INTO game (name, create_time) VALUES (%s, %s)"
                            cursor.execute(insert_game_query, (game_name, create_time))
                            game_id = cursor.lastrowid

                        # 检查 sources 表中是否存在对应的值
                        sources_query = "SELECT id FROM platform WHERE name = %s"
                        cursor.execute(sources_query, (sources,))
                        sources_result = cursor.fetchone()  # 获取查询结果
                        if sources_result:
                            sources_id = sources_result[0]
                        else:
                            # 在 sources 表中插入新的 sources
                            insert_sources_query = "INSERT INTO platform (name, create_time) VALUES (%s, %s)"
                            cursor.execute(insert_sources_query, (sources, create_time))
                            sources_id = cursor.lastrowid

                        # 更新已有行的 game_name 和 sources 字段
                        update_query = "UPDATE gl SET game_id = %s, platform_id = %s WHERE post_id = %s"
                        cursor.execute(update_query, (game_id, sources_id, post_id))
            except json.decoder.JSONDecodeError as e:
                print(f"JSONDecodeError in file: {filename}")
                error_files.append(filename)
    # 提交事务（如果数据库支持事务的话）
    db_conn.commit()

    cursor.close()
    db_conn.close()
    print(error_files)
    with open('../record/error_files.txt', "w", encoding="utf8") as txt_file:
        for file_name in error_files:
            txt_file.write(file_name + "\n")


if __name__ == "__main__":
    import_title_to_sql()
