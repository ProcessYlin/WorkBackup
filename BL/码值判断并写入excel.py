# -*- coding:utf-8 -*-
# !/usr/bin/env python

import xlwt
import pandas as pd
import copy
data = pd.read_excel(io="/Users/断码数据.xls", )
data = data.fillna(0)
# for indexs in data.index:
num = []
for m in range(len(data)):
    n = 0
    recode = []
    for i in range(data.columns.size):
        if i > 2 and data.loc[m].values[i] > 0:
            n = n+1
        elif i > 2 and data.loc[m].values[i] == 0:
            n = 0
        recode.append(n)
    num.append(max(recode))
# 深度拷贝码值数
size_pro = copy.deepcopy(num)
# 对码值数量转换
for i in range(len(num)):
    if num[i] < 3:
        num[i] = '残码'
    elif num[i] == 3:
        num[i] = '断码'
    elif num[i] > 3:
        num[i] = '齐码'
data_num = pd.DataFrame(num)
data_size = pd.DataFrame(size_pro)
print data_size
data_size.columns = ['码值连续数']
data_num.columns = ['码值情况']
data_one = pd.concat([data_size, data_num], axis=1)
data_final = pd.concat([data, data_one], axis=1)

# 数据写入Excel
borders = xlwt.Borders()
borders.left = xlwt.Borders.THIN
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
borders.left_colour = 0x40
borders.right_colour = 0x40
borders.top_colour = 0x40
borders.bottom_colour = 0x40
style = xlwt.XFStyle()
style.borders = borders

wbk = xlwt.Workbook(encoding='utf-8')
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER
# style = xlwt.XFStyle()
style.alignment = alignment
# cell_overwrite_ok=True 表示允许覆盖单元格内容
sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
for i in range(len(data_final.columns)):
    sheet.write(0, i, data_final.columns[i], style)
c = 1
for d in data_final.loc[data_final.index].values:
    for index in range(data_final.columns.size):
        sheet.write(c, index, d[index], style)
    c += 1
    # 设置字体居中
alignment = xlwt.Alignment()
alignment.horz = xlwt.Alignment.HORZ_CENTER
alignment.vert = xlwt.Alignment.VERT_CENTER
style.alignment = alignment
wbk.save(r'/Users/lin/Desktop/码值表.xls')
