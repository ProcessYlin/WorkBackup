# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
Workbook类初始化时有encoding和style_compression参数
encoding:设置字符编码，一般要这样设置：w = Workbook(encoding='utf-8')，就可以在excel中输出中文了。
"""
import xlwt
from impala.dbapi import connect
from impala.util import as_pandas
conn = connect(host='', port=)

def load_data(data_sql):
    # 打开游标
    cursor = conn.cursor()
    # 提取数据
    cursor.execute(data_sql)
    # 查询数据结果和字段名称
    data = cursor.fetchall()
    fields = cursor.description
    cursor.close()
    return data, fields

def write_excel(data, fields ):
    wbk = xlwt.Workbook(encoding='utf-8')
    sheet = wbk.add_sheet('sheet 1')
    for field in range(0, len(fields)):
        sheet.write(0, field, fields[field][0])
    c = 1
    for d in data:
        print d
        for index in range(len(d)):
            sheet.write(c, index, d[index])
            # print c, index, d[index]
        c += 1
    for index_o in range(len(data)):
        Str = ['E', str(index_o+2), '+', 'F', str(index_o+2)]
        website = ''.join(Str)
        # print website
        sheet.write(index_o+1, 9, xlwt.Formula(website))
    # 添加的公式--公式不能固定，要灵活

    wbk.save(r'/Users/lin/Desktop/test_excel_func.xls')
    print 'EXCEL 创建完成'

if __name__ == "__main__":
    # 查询数据
    data_sql = """ select * from bi_test.ylin_inventory_roll_tmp_test limit 20;"""
    # 1.载入数据
    print "---------- 1.load data ------------"
    # 2.保存所属的类别文件
    data, fields = load_data(data_sql)
    print type(data),type(fields)
    print "---------- 2.save subCenter ------------"
    write_excel(data, fields)



