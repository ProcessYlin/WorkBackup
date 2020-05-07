# -*- coding:utf-8 -*-
# !/usr/bin/env python
# description：进销存滚动表,支持货品同学完成补货预估和参考
# author     ：ylin
# created    ：2018-12-07
# updatelog  ：1.调整采购未到周期;2.季末目标库存为滚动周期后一个月的目标或者同期销售

import sys
reload(sys)
sys.setdefaultencoding('utf8')
import pandas as pd
import xlwt
from impala.dbapi import connect
conn = connect(host='10.101.10', port=, user='', password='')
cur = conn.cursor(user='lin.y')

def load_data(oday, xday, starday,realday,lastday, reason_end ,rate):
    """
    :param oday:  起始日前推6个月
    :param xday:  起始月前推一个月的最后一天库存
    :param starday: 起始月
    :param realday: 实际完成月的下一个月
    :param lastday: 截至月
    :param rate:    o2o销售占比
    :return:        滚动表基础数据
    """
    # 提取销售/库存数据
    df = pd.read_sql(sql_sal, conn)
    df_src = pd.read_sql(sql_src, conn)
    # 读入售罄率数据
    df_sal_rate = pd.read_sql(sql_rate, conn)
    # 构造全品牌+一级/三级分类，用来作为源，关联销售数据
    res = df_src
    # 实际销售+o2o销售
    cond1 = df['report_date'] >= starday
    cond2 = df['report_date'] <= realday
    cond  = df['report_date'] < realday
    cond4 = df['report_date'] <= lastday
    cond7 = df['report_date'] >= realday
    cond8 = df['report_date'] >= oday
    cond_end = df['report_date'] == reason_end
    # 季末目标库存
    data_season = df[cond_end].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['sale_total_amount']].sum().reset_index()
    data_season.rename(columns={'sale_total_amount': '季末目标库存'}, inplace=True)
    # 预估的o2o销售
    df_tar_o2o = df[cond7 & cond4].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['total_num']].sum().reset_index()
    df_tar_o2o['o2o_fur'] = df_tar_o2o.apply(lambda row: round(row['total_num'] * rate), axis=1)
    df_tar_o2o = df_tar_o2o[['brand_name', 'catname_one', 'catname_three', 'o2o_fur']]
    df_tar_o2o.rename(columns={'o2o_fur': 'o2o预估'}, inplace=True)

    # 采购未到
    df_not_arr = df[cond8].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['arr_not']].sum().reset_index()
    df_not_arr.rename(columns={'arr_not': '采购未到'}, inplace=True)
    # 库存
    cond9 = df['report_date'] == xday
    data_inv = df[cond9].groupby(['brand_name', 'catname_one', 'catname_three'])[['total_kucun']].sum().reset_index()
    data_inv.rename(columns={'total_kucun': '期初库存'}, inplace=True)

    # 采购已到和退货，此处采购已到也是前推6个月
    data_sto = df[cond1].groupby(['brand_name', 'catname_one', 'catname_three'])[['storage_num', 'purback_store_num']].sum().reset_index()
    data_sto.rename(columns={'storage_num': '采购已到', 'purback_store_num':'采购退货'}, inplace=True)
    res = res.merge(data_inv, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    res = res.merge(df_not_arr, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    res = res.merge(data_sto, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    res = res.merge(df_tar_o2o, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    # 单独计算实际发生的o2o
    data_o2o = df[cond1 & cond2].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['o2o_sale_amount']].sum().reset_index()
    data_o2o.rename(columns={'o2o_sale_amount': 'o2o销售'}, inplace=True)
    res = res.merge(data_o2o, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    # 计算实际发生销售额
    data_con = []
    for i in df[cond1 & cond]['report_date'].drop_duplicates().sort_values():
        cond = df['report_date'] == i
        data = df[cond].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['sale_total_amount']].sum().reset_index()
        data.rename(columns={'total_num': 'tar_' + i, 'sale_total_amount': 'sale_' + i}, inplace=True)
        data_con.append(data)
    for i in range(len(data_con)):
        res = pd.merge(res, data_con[i], on=['brand_name', 'catname_one', 'catname_three'], how='left')
    #############################################################################################
    # 预估月之后的目标
    cond3 = df['report_date'] > realday
    cond4 = df['report_date'] <= lastday
    data_tar = []
    for i in df[cond3 & cond4]['report_date'].drop_duplicates().sort_values():
        cond = df['report_date'] == i
        data1 = df[cond].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['total_num']].sum().reset_index()
        data1.rename(columns={'total_num': 'tar_' + i}, inplace=True)
        data_tar.append(data1)
    # 构造全品牌+一级/三级分类DF，用来作为源，做左关联
    res_num = df_src
    # 单独取需要预估月的目标和平均达成率
    cond5 = df['report_date'] >= '2018-03'
    cond6 = df['report_date'] < realday
    # 预估月的目标
    df_num = df[df['report_date'] == realday].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['total_num']].sum().reset_index()

    # 平均达成率
    df_rate = df[cond5 & cond6].groupby([df['brand_name'], df['catname_one'], df['catname_three']])[['rate']].mean().reset_index()
    # 月的销售预估
    data_num_rate = (df_src.merge(df_num, on=['brand_name', 'catname_one', 'catname_three'], how='left')
                         ).merge(df_rate, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    data_num_rate['sal_' + realday] = data_num_rate.apply(lambda row: round(row['rate'] * row['total_num']), axis=1)
    data_fur = data_num_rate[['brand_name', 'catname_one', 'catname_three', 'sal_' + realday]]
    # 拼接数据
    res_num = pd.merge(res_num, data_fur, on=['brand_name', 'catname_one', 'catname_three'], how='left')
    for i in range(len(data_tar)):
        res_num = pd.merge(res_num, data_tar[i], on=['brand_name', 'catname_one', 'catname_three'], how='left')
    data_final_one = (res.merge(res_num, on=['brand_name', 'catname_one', 'catname_two', 'catname_three'], how='left')).sort_values(by=['brand_name', 'catname_one', 'catname_two'], ascending=False)
    # 按照指定行顺序排序
    list_custom_one = ['女鞋', '男鞋', '包']
    list_custom = ['女士单鞋', '女士凉鞋', '女靴', '男士单鞋', '男士凉鞋', '男靴', '包']
    list_custom_three = ['满帮鞋', '浅口鞋', '鱼嘴鞋', '中空凉鞋', '后空凉鞋', '纯凉鞋', '拖鞋','凉靴', '短靴','低靴',
                         '中靴', '长靴','超长靴', '打孔鞋','包']
    data_final_one['catname_one'] = data_final_one['catname_one'].astype('category')
    data_final_one['catname_two'] = data_final_one['catname_two'].astype('category')
    data_final_one['catname_three'] = data_final_one['catname_three'].astype('category')
    data_final_one['catname_one'].cat.reorder_categories(list_custom_one, inplace=True)
    data_final_one['catname_two'].cat.reorder_categories(list_custom, inplace=True)
    data_final_one['catname_three'].cat.reorder_categories(list_custom_three, inplace=True)
    data_final_one.sort_values(by=['brand_name', 'catname_one', 'catname_two', 'catname_three'], inplace=True)
    data_final = data_final_one.merge(df_sal_rate, on=['brand_name', 'catname_one', 'catname_two', 'catname_three'], how='left').fillna(0)
    # 季末目标库存改成一个月的销售或者目标，比如9-2,用3月份的销售,3-8,就用9月份的销售和目标
    data_final = data_final.merge(data_season, on=['brand_name', 'catname_one', 'catname_three'], how='left').fillna(0)
    data_final['o2o销售额'] = data_final.apply(lambda row: row[8:10].sum(), axis=1)
    data_final['销售额'] = data_final.apply(lambda row: row[10:-2].astype('float').sum(), axis=1)
    data_final['月末库存'] = data_final.apply(lambda row: (row[4:7].sum() - row['采购退货']) - (row['销售额'] - row['o2o销售额']) , axis=1)
    # data_final['季末目标库存'] = (data_final.apply(lambda row: round((row['销售额'] - row['o2o销售额']) * (1 - row['rate'])), axis=1))
    data_final['预估售罄率'] = data_final.apply(lambda row: str(round((row['销售额'] - row['o2o销售额']) / (row[4:7].sum() - row['采购退货'] + 10) * 100,2)) + '%', axis=1)
    data_final['补货空间'] = data_final.apply(lambda row: (row[4:7].sum() - row['采购退货']) - (row['销售额'] - row['o2o销售额']) - row['季末目标库存'],axis=1)
    data_final['预警空间'] = data_final.apply(lambda row: (row[4:7].sum() - row['采购退货']) - (row['销售额'] - row['o2o销售额']),axis=1)
    # 拷贝计算好的文件，以免影响源数据，调整列顺序
    data_copy = data_final
    data_copy.rename(columns={'brand_name': '品牌', 'catname_one': '一级分类', 'catname_two': '二级分类', 'catname_three': '三级分类'}, inplace=True)
    data_space = data_copy['补货空间']
    data_copy = data_copy.drop('补货空间', axis=1)
    data_copy.insert(8, '补货空间', data_space)
    # 调整预警空间和采购已到的位置
    data_space = data_copy['预警空间']
    data_arr = data_copy['采购已到']
    data_copy = data_copy.drop('预警空间', axis=1)
    data_copy.insert(9, '预警空间', data_space)
    data_copy = data_copy.drop('采购已到', axis=1)
    data_copy.insert(5, '采购已到', data_arr)
    return data_copy

def write_excel(data):
    # 设置边框
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
    for i in range(len(data.columns)):
        sheet.write(0, i, data.columns[i], style)
    c = 1
    for d in data.loc[data.index].values:
        for index in range(data.columns.size):
            sheet.write(c, index, d[index], style)
        c += 1
    # 设置字体居中
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    style.alignment = alignment
    wbk.save(r'/Users/lin/Desktop/全品牌滚动表20190524.xls')

if __name__ == "__main__":
    # 查询数据
    sql_sal = 'select distinct * from test.table;'
    sql_src = 'select distinct brand_name,' \
              'catname_one,' \
              '(case when catname_two  like "%包%" then "包" else catname_two  end) as catname_two,' \
              '(case when catname_three  like "%包%" then "包" else catname_three  end) as catname_three ' \
              'from bi_test.ylin_inventory_roll_all;'
    sql_rate = 'select * from bi_test.reason_target_rate;'
    # 1.载入数据
    print "---------- 1.load data ------------"
    #        参数对应'采购未到起始日期'+'期初库存日期'+'起始月 '+ '预估月'  + '结束月'+ '季末目标库存月' +'o2o销售占比'
    data_copy = load_data('2019-03', '2019-02', '2019-03', '2019-05', '2019-08', '2018-03', 0.15)
    # 2.数据写入Excel
    print "---------- 2.Create Excel ------------"
   #  write_excel(data_copy)
