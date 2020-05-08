import os

path = r'/Users/lin/Desktop/特殊一轮-汇总' + '/'
file_list = os.listdir(path)
# print(file_list)
for file in file_list:
    old_path = path + file
    new_path = path + file.replace('商品预算模版—汇总', '商品预算模版-汇总')
    print(new_path)
    os.renames(old_path, new_path)
