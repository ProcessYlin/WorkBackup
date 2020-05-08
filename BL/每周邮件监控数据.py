# -*- coding:utf-8 -*-
# !/usr/bin/env python
"""
每周一执行改邮件脚本
"""
from datetime import datetime
import datetime as dy
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import traceback
import pandas as pd
import xlwt
from impala.dbapi import connect
conn = connect(host='impala.bjds.belle.lan', port=21051, auth_mechanism='LDAP', user='lin.y', password='061038ly')
cur = conn.cursor(user='lin.y')

def Hive_data(Monday, Sunday, Monday_after, Sunday_after):
    yesdata = """
      select
distinct
t1.brand_name                      as brand_name,
t4.commodity_style_no              as style_no,
t1.product_code                    as product_code,
t1.catname_one                     as catname_one,
t1.catname_two                     as catname_two,
t1.catname_three                   as catname_three,
t1.CHANNEL                         as CHANNEL,
t1.COMMODITY_YEARS                 as YEARS,
t1.COMMODITY_SEASON                as SEASON,
t1.db                              as db,
t1.hb                              as hb,
t1.hd                              as hd,
t1.hn                              as hn,
t1.hz                              as hz ,
t1.ly                              as ly ,
t1.xb                              as xb ,
t1.xn                              as xn ,
t1.YPUBLIC_PRICE                   as YPUBLIC_PRICE,
nvl(t3.tb_price,0)                 as tb_price,
nvl(t3.jd_price,0)                 as jd_price,
nvl(t3.wph_price,0)                as wph_price,
t1.online                          as online,
round(nvl(t2.nation_avg,0))        as nation,
t1.cpz
from
(
select
       a.brand_name        as brand_name,a.product_code      as product_code,
       a.catname_one       as catname_one,a.catname_two       as catname_two,
       a.catname_three     as catname_three,a.CHANNEL           as CHANNEL,a.COMMODITY_YEARS   as COMMODITY_YEARS,
       a.COMMODITY_SEASON  as COMMODITY_SEASON,
       max(YPUBLIC_PRICE)  as YPUBLIC_PRICE,a.cpz               as cpz,
       round(max(nvl(case when a.region_name='东北'        then a.region_avg end  ,0)  ) )  as    db         ,
       round(max(nvl(case when a.region_name='华北'        then a.region_avg end  ,0)  ) )  as    hb         ,
       round(max(nvl(case when a.region_name='华东'        then a.region_avg end  ,0)  ) )  as    hd         ,
       round(max(nvl(case when a.region_name='华南'        then a.region_avg end  ,0)  ) )  as    hn         ,
       round(max(nvl(case when a.region_name='华中'        then a.region_avg end  ,0)  ) )  as    hz         ,
       round(max(nvl(case when a.region_name='鲁豫'        then a.region_avg end  ,0)  ) )  as    ly         ,
       round(max(nvl(case when a.region_name='西北'        then a.region_avg end  ,0)  ) )  as    xb         ,
       round(max(nvl(case when a.region_name='西南'        then a.region_avg end  ,0)  ) )  as    xn         ,
       round(max(nvl(case when a.region_name='电商'        then a.region_avg end  ,0)  ) )  as    online

from
(
select
       catname_one,catname_two,catname_three,CHANNEL,COMMODITY_YEARS,COMMODITY_SEASON,brand_name,
       product_code,region_name,cpz, max(YPUBLIC_PRICE) as YPUBLIC_PRICE,
       sum(sal)/sum(qty)  as region_avg
from  bi_report.dwm_commodity_price_ratio
where out_date>='%s' and out_date<='%s'
  and qty>0
group by brand_name,product_code,region_name,catname_one,catname_two,catname_three,COMMODITY_YEARS,COMMODITY_SEASON,CHANNEL,cpz
) a
group by a.brand_name,a.product_code,
         a.catname_one,a.catname_two,a.catname_three,
         a.COMMODITY_YEARS,a.COMMODITY_SEASON,a.CHANNEL,a.cpz
) t1
left join
(
select
       catname_one,catname_two,catname_three,CHANNEL,COMMODITY_YEARS,COMMODITY_SEASON,brand_name, product_code,
       sum(sal)/sum(qty)  as nation_avg
from  bi_report.dwm_commodity_price_ratio
where  region_name <> '电商'
  and  qty>0
  and  out_date>='%s' and out_date<='%s'
group by brand_name,product_code,catname_one,catname_two,catname_three,COMMODITY_YEARS,COMMODITY_SEASON,CHANNEL
) t2
 on t1.brand_name       = t2.brand_name and t1.product_code     = t2.product_code
and t1.catname_one      = t2.catname_one and t1.catname_two      = t2.catname_two and t1.catname_three    = t2.catname_three
and t1.COMMODITY_YEARS  = t2.COMMODITY_YEARS and t1.COMMODITY_SEASON = t2.COMMODITY_SEASON and t1.CHANNEL          = t2.CHANNEL
left join
(
select
brand_name,
product_code,
round(max(nvl(case when platform='淘宝'  then avg_price end  ,0)  ) )  as   tb_price,
round(max(nvl(case when platform='京东'  then avg_price end  ,0)  ) )  as   jd_price,
round(max(nvl(case when platform='唯品'  then avg_price end  ,0)  ) )  as   wph_price
from (
select
t4.commodity_supplier_code       as product_code,
t4.commodity_brand_name          as brand_name,
case when t1.order_source_no like 'TB%%'      then '淘宝'
     when t1.order_source_no like 'WBPT-JD%%' then '京东'
     when t1.order_source_no like 'WBPT-WPH%%' then '唯品'
 end as platform,
sum(t1.SALE_TOTAL_AMOUNT) / sum(t1.SALE_COMMODITY_NUM)       as avg_price
from bi_report.dwm_commodity_analysis_yh t1
left join bi_report.commodity_base_info t4
  on  t1.COMMODITY_NO=t4.COMMODITY_NO
where t4.commodity_catname_one in ('女鞋','男鞋','户外休闲','包')
  and t4.commodity_brand_name  in ('BEVIVO','百丽','百丽箱包','他她','天美意','百思图','森达','伐拓',
                            '思加图','妙丽','真美诗','卡特','拔佳','暇步士')
  and t1.REPORT_DATE>='%s' and t1.REPORT_DATE<='%s'
  and t1.SALE_COMMODITY_NUM>0
group by t4.commodity_supplier_code,t4.commodity_brand_name,
case when t1.order_source_no like 'TB%%'      then '淘宝'
     when t1.order_source_no like 'WBPT-JD%%' then '京东'
     when t1.order_source_no like 'WBPT-WPH%%' then '唯品'
 end
 ) w
where platform is not NULl
group by brand_name,product_code

) t3
 on t1.product_code=t3.product_code
and t1.brand_name  = t3.brand_name
left join bi_report.commodity_base_info t4
  on t1.product_code = t4.commodity_supplier_code
where t2.nation_avg < t1.online
  and t2.nation_avg<>0
""" % (Monday, Sunday, Monday, Sunday, Monday, Sunday)

    afterdata = """
      select
        t1.brand_name      as brand_name,
        t1.style_no        as style_no,
        t1.product_code    as product_code,
        t1.catname_one     as catname_one,
        t1.catname_two     as catname_two,
        t1.catname_three   as catname_three,
        t1.COMMODITY_YEARS           as YEARS,
        t1.COMMODITY_SEASON          as SEASON,
        round(t1.nation,0)          as nation_yes,
        round(t2.nation,0)          as nation_after,
        t1.cpz
        from
        (
        select
       t1.catname_one   as catname_one,
       t1.catname_two   as catname_two,
       t1.catname_three as catname_three,
       t1.CHANNEL       as CHANNEL,
       t1.COMMODITY_YEARS as COMMODITY_YEARS,
       t1.COMMODITY_SEASON as COMMODITY_SEASON,
       t1.brand_name       as brand_name,
       t1.product_code     as product_code,
       t4.commodity_style_no as style_no,
       t1.cpz,
       sum(t1.sal)/sum(t1.qty)  as nation
        from  bi_report.dwm_commodity_price_ratio t1
   left join bi_report.commodity_base_info t4
          on t1.product_code = t4.commodity_supplier_code
        where t1.out_date>='%s'
          and t1.out_date<='%s'
          and t1.region_name <> '电商'
          and t1.qty>0
        group by t1.catname_one, t1.catname_two,t1.catname_three,t1.CHANNEL, t1.COMMODITY_YEARS,
       t1.COMMODITY_SEASON,t1.brand_name,t1.product_code,t1.cpz,t4.commodity_style_no
        ) t1
        inner join
        (
       select
       t1.catname_one   as catname_one,
       t1.catname_two   as catname_two,
       t1.catname_three as catname_three,
       t1.CHANNEL       as CHANNEL,
       t1.COMMODITY_YEARS as COMMODITY_YEARS,
       t1.COMMODITY_SEASON as COMMODITY_SEASON,
       t1.brand_name       as brand_name,
       t1.product_code     as product_code,
       t4.commodity_style_no as style_no,
       t1.cpz,
       sum(t1.sal)/sum(t1.qty)  as nation
        from  bi_report.dwm_commodity_price_ratio t1
   left join bi_report.commodity_base_info t4
          on t1.product_code = t4.commodity_supplier_code
        where t1.out_date>='%s'
          and t1.out_date<='%s'
          and t1.region_name <> '电商'
          and t1.qty>0
        group by t1.catname_one, t1.catname_two,t1.catname_three,t1.CHANNEL, t1.COMMODITY_YEARS,
       t1.COMMODITY_SEASON,t1.brand_name,t1.product_code,t1.cpz,t4.commodity_style_no
        ) t2
        on  t1.product_code=t2.product_code
        and t1.brand_name  = t2.brand_name
        where (t2.nation-t1.nation) >10
          and t1.nation<>0
          and t2.nation<>0

          ;
    """ % (Monday, Sunday, Monday_after, Sunday_after)
    cur.execute(yesdata)
    df_yes = cur.fetchall()
    df_yes = pd.DataFrame(df_yes, columns=['品牌', '商品款号','商品编码','一级分类','二级分类', '三级分类', '销售渠道','年份','季节','东北','华北',
                      '华东', '华南', '华中','鲁豫', '西北', '西南', '牌价', '淘宝均价','京东均价','唯品会均价','线上均价','线下均价','畅平滞'])
    print df_yes
    cur.execute(afterdata)
    df_after = cur.fetchall()
    df_after = pd.DataFrame(df_after,columns = ['品牌','商品款号', '商品编码','一级分类','二级分类', '三级分类', '年份','季节', '上周线下均价', '上上周线下均价','畅平滞'])
    return df_after, df_yes


def write_excel(data_yes, data_after):
    # 设置边框
    data = data_yes
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
    sheet = wbk.add_sheet('线上价格高于线下', cell_overwrite_ok=True)
    for i in range(len(data.columns)):
        sheet.write(0, i, data.columns[i], style)
    c = 1
    for d in data.loc[data.index].values:
        for index in range(data.columns.size):
            sheet.write(c, index, d[index], style)
        c += 1
    # 第二页数据
    sheet_one = wbk.add_sheet('线下价格差异', cell_overwrite_ok=True)
    for i in range(len(data_after.columns)):
        sheet_one.write(0, i, data_after.columns[i], style)
    c = 1
    for d in data_after.loc[data_after.index].values:
        for index in range(data_after.columns.size):
            sheet_one.write(c, index, d[index], style)
        c += 1
    # 设置字体居中
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    alignment.vert = xlwt.Alignment.VERT_CENTER
    # style = xlwt.XFStyle()
    style.alignment = alignment
    wbk.save(r'/Users/lin/Desktop/线上线下价格校对.xls')

def SendMail(subject, Monday, Sunday, Monday_after, Sunday_after):
    # today = datetime.date.today()
    server = {'name': 'smtp.exmail.qq.com', 'user': 'daily_report@belle.com.cn', 'passwd': 'Yougou@2019'}
    fro = 'ylin<daily_report@belle.com.cn>'
    to = ['lin.yang@belle.com.cn']
    # to = ['zhou.xy@belle.com.cn', 'zhu.xl@belle.com.cn', 'han.gs@belle.com.cn', 'yan.jieer@belle.com.cn',
    #        'tan.xiu@belle.com.cn', 'zhu.yh@belle.com.cn', 'michael.hu@belle.com.cn', 'fu.sx@belle.com.cn', 'zhu.rl@belle.com.cn',
    #        'guan.wei@belle.com.cn', 'zhang.yp@belle.com.cn', 'xu.yy@belle.com.cn',
    #        'wang.jm@belle.com.cn', 'wang.zh.sz@belle.com.cn', 'li.lz@belle.com.cn', 'zhang.bt.sz@belle.com.cn',
    #        'xu.yx@belle.com.cn', 'chen.fl@belle.com.cn', 'he.xf@belle.com.cn', 'li.xz.sz@belle.com.cn',
    #        'zeng.t1.sz@belle.com.cn', 'du.l@belle.com.cn', 'huang.cr@belle.com.cn',
    #        'chen.lin@belle.com.cn', 'niu.r@belle.com.cn', 'zhan.dp@belle.com.cn', 'qin.wm@belle.com.cn',
    #        'he.t.sz@belle.com.cn', 'tang.p@belle.com.cn', 'huang.p@belle.com.cn', 'wang.ll1.sz@belle.com.cn',
    #        'wang.jm@belle.com.cn', 'lu.x.sz@belle.com.cn', 'li.zp@belle.com.cn',
    #        'han.jb@belle.com.cn', 'zhong.yl@belle.com.cn', 'luo.l.sz@belle.com.cn','lin.yang@belle.com.cn']

    from email.header import Header
    msg = MIMEMultipart()
    msg['From'] = fro
    msg['Subject'] = Header('线上线下价格校对' + str(today), 'utf-8')
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    content = 'Dear All：' \
              '     \n本邮件记录%s至%s线上价格与线下的产品信息，望知悉.' \
              '     \n第一Sheet页记录%s至%s线上成交均价高于线下成交均价的商品信息' \
              '     \n第二Sheet页记录%s至%s线下成交均价较%s至%s线下成交均价降幅大于10元的商品信息' % ( Monday, Sunday, Monday, Sunday,Monday, Sunday, Monday_after, Sunday_after)
    cont = MIMEText(content, 'plain', 'utf-8')
    msg.attach(cont)

    xlsxpart = MIMEApplication(open('/Users/lin/Desktop/线上线下价格校对.xls', 'rb').read())
    xlsxpart.add_header('Content-Disposition', 'attachment', filename='线上线下价格的数据.xls')
    msg.attach(xlsxpart)

    import smtplib
    smtp = smtplib.SMTP(server['name'])
    smtp.login(server['user'], server['passwd'])
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()

if __name__ == '__main__':
    day = datetime.now().weekday()
    print '0 means is Monday,Today is %s' % day
    if day == 0:
        print 'This is Monday, it is time to runnung the demo'
        today = dy.date.today()
        Monday = today + dy.timedelta(days=-7)
        Sunday = today + dy.timedelta(days=-1)
        Monday_after = today + dy.timedelta(days=-14)
        Sunday_after = today + dy.timedelta(days=-8)
        print 'The last monday is %s, last sunday is %s' % (Monday, Sunday)
        print 'The last second monday is %s, last second sunday is %s' % (Monday_after, Sunday_after)
        # 1.载入数据
        print "---------- 1.load data ------------"
        data_after, data_yes = Hive_data(Monday, Sunday, Monday_after, Sunday_after)
        # 2.写入附件
        print "---------- 2.writer excel ---------"
        write_excel(data_yes, data_after)
        # 3.发送邮件
        print "---------- 3.send mail ------------"
        # SendMail('线上线下价格校对', Monday, Sunday, Monday_after, Sunday_after)
    else:
        print 'Time is not, please sleep'
        pass
