import re

import mysql.connector
from tqdm import tqdm

# 连接到数据库
connection = mysql.connector.connect(
        host="47.97.61.236",
        user="aigl",
        password="ziwah4ieL#9thoSi5koo",
        database="aigl",
    )
cursor = connection.cursor(buffered=True)

# 查询gl表中的所有行
select_query = "SELECT id, title FROM gl WHERE game_id IS NULL"
cursor.execute(select_query)
gl_rows = cursor.fetchall()

# 遍历每一行
for gl_row in tqdm(gl_rows):
    gl_id, title = gl_row

    # 检查title是否存在书名号
    if '《' not in title or '》' not in title:
        continue  # 跳过没有书名号的行
    # 提取游戏名（假设游戏名在书名号中间）
    game_name = title.split('《', 1)[-1].split('》', 1)[0]
    game_name = re.sub(r'[\s:：]', '', game_name).lower()

    # 查询game表是否存在该游戏名
    game_query = "SELECT id FROM game WHERE name = %s"
    cursor.execute(game_query, (game_name,))
    game_result = cursor.fetchone()

    if game_result:
        game_id = game_result[0]
    else:
        # 在game表中创建新的行，并获取新的id
        insert_game_query = "INSERT INTO game (name) VALUES (%s)"
        cursor.execute(insert_game_query, (game_name,))
        connection.commit()
        game_id = cursor.lastrowid

    # 更新gl表的game_id字段
    update_gl_query = "UPDATE gl SET game_id = %s WHERE id = %s"
    cursor.execute(update_gl_query, (game_id, gl_id))
    connection.commit()

# 关闭连接
cursor.close()
connection.close()