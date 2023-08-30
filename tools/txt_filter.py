import os
import multiprocessing
from tqdm import tqdm

def count_files_with_string(folder_path, search_string):
    count = 0

    # 获取文件夹内的 txt 文件列表
    txt_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.txt')]

    for filename in tqdm(txt_files):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if search_string in content:
                count += 1
                # 删除包含指定字符串的文件
                os.remove(file_path)
    return count

def replace_text_in_file(folder_path):
    with open(folder_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 执行文本替换
    modified_content = content.replace('游民小编', '小编')
    modified_content = modified_content.replace('游民速攻', '速攻')
    modified_content = modified_content.replace('游民论坛', '论坛')

    with open(folder_path, 'w', encoding='utf-8') as file:
        file.write(modified_content)


def process_file(folder_path):
    try:
        replace_text_in_file(folder_path)
        print(f"文件 {folder_path} 处理完成")
    except Exception as e:
        print(f"处理文件 {folder_path} 时发生错误：{e}")


if __name__ == '__main__':
    folder_path = "../txt_results"  # 指定文件夹路径
    file_count = count_files_with_string(folder_path, '游民')
    print(file_count)

    # # 获取文件夹内的 txt 文件列表
    # txt_files = [filename for filename in os.listdir(folder_path) if filename.endswith('.txt')]
    # file_path_lists = [(os.path.join(folder_path, filename)) for filename in txt_files]
    # # 使用多进程进行处理
    # num_processes = multiprocessing.cpu_count()  # 获取 CPU 核心数
    # with multiprocessing.Pool(processes=num_processes) as pool:
    #     tqdm(pool.map(process_file,
    #                       file_path_lists))