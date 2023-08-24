import json

# 创建数字范围的列表
number_list = list(range(1, 1634799))

# 将列表保存为JSON文件
with open('../record/id_list.json', 'w') as json_file:
    json.dump(number_list, json_file)
