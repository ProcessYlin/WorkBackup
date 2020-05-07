CREATE TABLE data_belle.kylin_product_info_data (


product_code       STRING COMMENT '商品编码',
brand_name         STRING COMMENT '品牌',
region_name        STRING COMMENT '地域',
platform           STRING COMMENT '平台',
YPUBLIC_PRICE      double COMMENT '牌价',
current_price      double COMMENT '全国指导价', 
catname_one        STRING COMMENT '一级分类',
catname_two        STRING COMMENT '二级分类',
catname_three      STRING COMMENT '三级分类',
COMMODITY_YEARS    STRING COMMENT '年份',
COMMODITY_SEASON   STRING COMMENT '季节',
CHANNEL            STRING COMMENT '渠道', 
cpz                STRING COMMENT '畅平滞',
qty                double COMMENT '销量',
sal                double COMMENT '销售额'
) 
PARTITIONED BY ( out_date STRING ) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n' 
WITH SERDEPROPERTIES ('serialization.format'=',', 'line.delim'='\n', 'field.delim'=',') STORED AS TEXTFILE 




*********shell脚本
#!/bin/sh
# 数据每日更新

DATE_1d=`date -d "-1 day" +%Y-%m-%d`
DATE=`date -d "-1 day" +%Y%m%d`

#


hive -e "$sql"
