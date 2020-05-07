#!/bin/sh

# 数据每日增量跟新

#echo '等待7点再开始数据同步，如果手工执行，请注释等待2小时代码'
#sleep 2h


DATE_1d=`date -d "-1 day" +%Y-%m-%d`
DATE=`date -d "-1 day" +%Y%m%d`
DATE_F=`date -d "$DATE -10 days" +%Y-%m-%d`
date_30=`date -d "-30 days" +%Y-%m-%d`
DIR="../.."
CONF_DIR="../../conf"
mkdir -p $DIR/log/`date +%Y%m%d`



function oracle2hive_dwm_commodity_analysis_yh {
mysql -h10.15.1.14 -ubelle_user -p2RXFgsLK -e"
update belle.table_check set is_updated=0,updatetime=current_timestamp() where table_name='ods_dwm_commodity_analysis_yh';"

hadoop fs -rm -r /user/fxwang/BI_REPORT.DWM_COMMODITY_ANALYSIS_YH

        sqoop import \
        --hive-import \
        --connect jdbc:$JDBC \
        --username $USERNAME \
        --password $PASSWORD \
        --table BI_REPORT.DWM_COMMODITY_ANALYSIS_YH \
        --hive-database data_belle \
        --hive-table import_dwm_commodity_analysis_yh \
        --hive-partition-key "import_date" \
        --hive-drop-import-delims \
        --where "report_date >= '$date_30'" \
        --hive-partition-value "$DATE" \
        --hive-overwrite \
        --input-null-string "\\\\N" \
        --input-null-non-string "\\\\N" \
        --split-by commodity_no \
        -m 10

        if [ $? -eq 0 ];then
            create_sql="show create table data.test_table;"
            CREATE_SQL=`hive -e "$create_sql"`
            CREATE_COLS=$(echo $CREATE_SQL|awk -F')' '{print$1}'|awk -F'(' '{print$2}'|sed 's/,/,\n/g'|grep -v 'import_date'|grep -v report_date)
            echo $CREATE_COLS
            logger "BI_REPORT.DWM_COMMODITY_ANALYSIS_YH sqoop has done!"
            echo -e "**********BI_REPORT.DWM_COMMODITY_ANALYSIS_YH sqoop has done!************"
            # merge数据
            sql="set hive.exec.dynamic.partition=true;
             set hive.exec.dynamic.partition.mode=nonstrict;
             set hive.exec.max.dynamic.partitions=100000;
             set hive.exec.max.dynamic.partitions.pernode=100000;
             set hive.support.quoted.identifiers=none;
             set hive.support.concurrency=false;

             insert overwrite table data.test_table partition(report_date)
             select
             \`(report_date|import_date)?+.+\`,report_date from 
             data_belle.import_dwm_commodity_analysis_yh
             where import_date='$DATE' "
            hive -e "$sql"
            if [ $? -eq 0 ];then
               logger "BI_REPORT.DWM_COMMODITY_ANALYSIS_YH merge has done!"
               echo -e "**********BI_REPORT.DWM_COMMODITY_ANALYSIS_YH merge has done!**********"
               mysql -h10.15.1.14 -ubelle_user -p2RXFgsLK -e"update belle.table_check set is_updated=1,updatetime=current_timestamp() where table_name='ods_dwm_commodity_analysis_yh';"
            else
               logger "BI_REPORT.DWM_COMMODITY_ANALYSIS_YH merge error!"
               echo -e "**********BI_REPORT.DWM_COMMODITY_ANALYSIS_YH merge error!************"
               exit 1
            fi
        else
            logger "BI_REPORT.DWM_COMMODITY_ANALYSIS_YH sqoop error!"
            echo -e "*********BI_REPORT.DWM_COMMODITY_ANALYSIS_YH sqoop error!**********"
            echo -e "WARNING:DATE:`date '+%Y-%m-%d %H:%M:%S'`,TABLE:BI_REPORT.DWM_COMMODITY_ANALYSIS_YH sqoop failed.开始第二次sqoop" | mail -s "Warning of the BI_REPORT.DWM_COMMODITY_ANALYSIS_YH" fxwang@hillinsight.com
            sleep 10m
            oracle2hive_dwm_commodity_analysis_yh
        #exit 1
        fi

}

init

oracle2hive_dwm_commodity_analysis_yh




