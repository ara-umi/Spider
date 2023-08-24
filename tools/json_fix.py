import os
import json
import multiprocessing

from tqdm import tqdm


# 定义一个函数，用于处理单个 JSON 文件
def process_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

        # 修改属性
        data['post_id'] = data.pop('id')  # 将 id 改为 post_id
        data['create_time'] = '2023-08-23'  # 新增 create_time 属性
        data['status'] = 0  # 新增 status 属性

        # 再次保存 JSON 数据到文件
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)




if __name__ == '__main__':
    # 指定包含 JSON 文件的文件夹路径
    json_folder = '../json_results'

    # 获取文件夹中的 JSON 文件列表
    file_list = [filename for filename in os.listdir(json_folder) if filename.endswith('.json')]

    # 使用多进程进行处理
    num_processes = multiprocessing.cpu_count()  # 获取 CPU 核心数
    with multiprocessing.Pool(processes=num_processes) as pool:
        tqdm(pool.map(process_json_file, [os.path.join(json_folder, filename) for filename in file_list]))
