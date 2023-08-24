import json

# 读取JSON文件
with open('../record/id_list.json', 'r') as file:
    data = json.load(file)

print(len(data))
# 定义要删除的数字范围
min_value = 1233083
max_value = 1326132

# 过滤出不在指定范围内的数字
filtered_numbers = [num for num in data if num < min_value or num > max_value]
print(len(filtered_numbers))
input("回车确认删除")
# 将过滤后的列表重新写入JSON文件
with open('../record/id_list.json', 'w') as file:
    json.dump(filtered_numbers, file)

