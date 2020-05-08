# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
定义 random_choice = ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'b', 'b', 'b']
则a的概率为60%，b的概率为30%，在需要随机的测试中用两个值来设定概率，以此可以放大到多个条件
放大到满减的活动，在第一次满减之后，挑选一定比例（两件占比20%）的单品在减去最低折扣的一半
"""

import multiprocessing
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from multiprocessing import Pool
import datetime
import random
import numpy as np
import pandas as pd
import xlwt
# 编写活动参数模块
def load_active_data_disct(file_path_active):
    data = pd.read_excel(io=file_path_active)
    dict_data = data.set_index('active').T.to_dict('list')
    return dict_data

def load_data(file_path):
    # 此处读取的整数默认是先读入float类型，然后转换成int类型,但是部分数据还是会少读取一个数
    data = pd.read_excel(io=file_path, dtype={'store': float})
    return data

# 折扣和满减的活动顺序
def order_choice(data, frequency, sign, dict_data, random_choice ):
    p = Pool(10)  # 采用进城池实现多进程，apply_async()默认是非阻塞的模式,开10个进程
    if sign == 1:
        result = p.apply_async(discount_saloff, args=(data, frequency, dict_data, random_choice, ))
    elif sign == 0:
        result = p.apply_async(saloff_discount, args=(data, frequency, dict_data, random_choice, ))
    p.close()  # 关闭进程池
    p.join()
    return result

# 先满减再折扣
def saloff_discount(data, frequency, dict_data,random_choice):
    pro_one = []
    all_gmv = []
    a = random_choice
    pro = data['product']
    price = data['price']
    store = data['store']
    len = data.iloc[:, 0].size
    # 多次模拟买货流程
    count = 0
    while (count < frequency):
        count += 1
        if count % 100 == 0:
            print count
        for i in range(0, len, 1):
            j = 0
            n = price[i]
            w_product = pro[i]
            gmv = 0
            dis_price_one = 0
            while(j < store[i] ):
                dis_price_one = n
                j += 1
                random_value = random.sample(a, 1)
                for ka, va in dict_data.items():
                    if ka == 'OFF' and va[0] > n >= va[1]:
                         dis_price_one = dis_price_one - va[2]
                    elif ka == 'OFF1' and va[0] > n >= va[1]:
                         dis_price_one = dis_price_one - va[2]
                    elif ka == 'OFF2' and va[0] > n >= va[1]:
                         dis_price_one = dis_price_one - va[2]
                    elif ka == 'OFF3' and va[0] > n >= va[1]:
                          dis_price_one = dis_price_one - va[2]
                print dis_price_one
                # 折扣阶段验证完毕，代码格式勿动，此处很坑
                # print dis_price_one, n, random_value
                # print gmv
            #     gmv = dis_price_one + gmv
            # print gmv
                for k, v in dict_data.items():
                    if k == 'dis' and random_value == ['b']:
                        dis_price_one = dis_price_one * v[0]
                        # print dis_price_one, n, random_value
                    elif k == 'dis' and random_value == ['c']:
                        dis_price_one = dis_price_one * v[1]
                        # print dis_price_one, n, random_value
                    elif k == 'dis1':
                       dis_price_one = dis_price_one * v[2]
                # print dis_price_one
                gmv = dis_price_one + gmv
            # print '$', gmv, dis_price_one
            all_gmv.append(int(gmv))
            pro_one.append(w_product)
        # 合并SKU价格和最终gmv,最后可改为商品编码作为标识
        gmv_last = pd.DataFrame(all_gmv)
        pro_last = pd.DataFrame(pro_one)
        data_final = pd.concat([pro_last, gmv_last], axis=1)
        data_final.columns = ['product_no',  'GMV']
    data_ananly = data_final.groupby('product_no')['GMV']
    return data_ananly

# 先折扣再满减
def discount_saloff(data, frequency, dict_data, random_choice):
    pro_one = []
    all_gmv = []
    a = random_choice
    pro = data['product']
    price = data['price']
    store = data['store']
    len = data.iloc[:, 0].size
    # 多次模拟买货流程
    count = 0
    while (count <= frequency):
        count += 1
        if count % 100 == 0:
            print count
        for i in range(0, len, 1):
            j = 0
            n = price[i]
            w_product = pro[i]
            gmv = 0
            dis_price_one = 0
            while(j < store[i]):
                j += 1
                random_value = random.sample(a, 1)
                # 此处先折扣后满减
                for k, v in dict_data.items():
                    if k == 'dis' and random_value == ['b']:   # 两件的占比
                        dis_price_one = n * v[0]
                    elif k == 'dis' and random_value == ['c']:  # 三件的占比
                        dis_price_one = n * v[1]
                        # print dis_price_one, n, random_value
                    elif k == 'dis1':
                       dis_price_one = n * v[2]
                # 折扣阶段验证完毕，代码格式勿动，此处很坑
                # print dis_price_one, n, random_value
                # print gmv
            #     gmv = dis_price_one + gmv
            # print gmv
                for ka, va in dict_data.items():
                    if ka == 'OFF1' and va[0] > dis_price_one >= va[1]:
                         dis_price_one = dis_price_one - va[2]
                    elif ka == 'OFF2' and va[0] > dis_price_one >= va[1]:
                         dis_price_one = dis_price_one - va[2]
                    # elif ka == 'OFF3' and va[0] > dis_price_one >= va[1]:
                    #      dis_price_one = dis_price_one - va[2]
                    # 因为两件的客户占比为20%，肯定会触发最低折扣线，所以随机对20%的商品减去最低优惠的一半,概率可调整
                    elif ka == 'OFF2' and random_value == ['b']:
                         dis_price_one = dis_price_one - (va[2] / 2)
                # print dis_price_one
                gmv = dis_price_one + gmv
            # print gmv
            all_gmv.append(int(gmv))
            pro_one.append(w_product)
        # 合并SKU价格和最终gmv,最后可改为商品编码作为标识
        gmv_last = pd.DataFrame(all_gmv)
        pro_last = pd.DataFrame(pro_one)
        data_final = pd.concat([pro_last, gmv_last], axis=1)
        data_final.columns = ['product_no',  'GMV']
    data_ananly = data_final.groupby('product_no')['GMV']
    return data_ananly

def write_excel(data, all_gmv):
    data = pd.merge(data, all_gmv, how='left', on='product')
    data['总成本'] = data.apply(lambda row: round(row['cost'] * row['store']), axis=1)
    data['最低成交均价'] = data.apply(lambda row: round(row['GMV_MIN'] / (row['store'] + 1)), axis=1)
    data['最高成交均价'] = data.apply(lambda row: round(row['GMV_MAX'] / (row['store'] + 1)), axis=1)
    data['最高折扣'] = data.apply(lambda row: str(round(row['最低成交均价'] / row['price'] * 100, 2)) + '%', axis=1)
    data['最低折扣'] = data.apply(lambda row: str(round(row['最高成交均价'] / row['price'] * 100, 2)) + '%', axis=1)
    data['最终毛利额_Min'] = data.apply(lambda row: round(row['GMV_MIN'] - row['总成本']), axis=1)
    data['最终毛利额_Max'] = data.apply(lambda row: round(row['GMV_MAX'] - row['总成本']), axis=1)
    data['最终毛利率_Max'] = data.apply(lambda row: str(round( (row['GMV_MAX'] - row['总成本']) / (row['GMV_MAX'] + 1) * 100, 2)) + '%', axis=1)
    data['最终毛利率_Min'] = data.apply(lambda row: str(round( (row['GMV_MIN'] - row['总成本']) / (row['GMV_MIN'] + 1) * 100, 2)) + '%', axis=1)
    style = xlwt.XFStyle()
    wbk = xlwt.Workbook(encoding='utf-8')
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    style.alignment = alignment
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    sheet = wbk.add_sheet('sheet 1', cell_overwrite_ok=True)
    for i in range(len(data.columns)):
        sheet.write(0, i, data.columns[i], style)
    c = 1
    for d in data.loc[data.index].values:
        for index in range(data.columns.size):
            sheet.write(c, index, d[index], style)
        c += 1
    wbk.save(r'/Users/lin/Desktop/7.27-7.28品牌团预估.xls')

if __name__ == "__main__":
    # 每件的概率，a表示一件，b表示两件，c表示三件
    random_choice = ['a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a', 'a']
    data_name = []
    starttime = datetime.datetime.now()
    file_path = "/Users/lin/desktop/7.27-7.28品牌团.xlsx"
    # 活动类型数据
    # 1.导入数据
    print "---------- 1.load data ------------"
    file_path_active = "/Users/lin/desktop/活动统计表.xls"
    dict_data = load_active_data_disct(file_path_active)
    data = load_data(file_path)
    # 2.活动顺序，1--先折扣后满减，0--先满减后折扣
    # 参数含义：活动数据，计算次数，计算规则，件数概率模拟
    result = order_choice(data, 1, 0, dict_data, random_choice)
    # 3.活动计算
    print "---------- 3.computer discount ----"
    df = result.get()   # 计算后的返回值
    describe_df = df.describe()  # 描述性统计
    part_data = pd.DataFrame(describe_df[['min', 'max']].values)
    # 获取聚合之后的商品编号
    for name, group in df:
        data_name.append(name)
    data_name = pd.DataFrame(data_name)
    part_data = pd.concat([data_name, part_data], axis=1)
    # 重命名拼接数据
    part_data.columns = ['product', 'GMV_MIN', 'GMV_MAX']  # 对取出来的gmv最值列命名
    # 4.数据写入
    print "---------- 4.save data ----"
    write_excel(data, part_data)
    # 测试计算时间
    endtime = datetime.datetime.now()
    print 'time:', (endtime - starttime).seconds


