#!/usr/bin/python
# -*- coding:utf-8 -*-

import datetime
import traceback
import sys
sys.path.append("/home/hive/py/libs")
from utils.MailUtils import SendMail
from database.Database import OracleDB
from time import sleep

def getFinshStatus(tableName,databaseName,hostName,databseType,jobName):
    try:
        oracleDB = OracleDB()
        code = 1
        while code>0:
            #查询sql
	    print "开始查询"
	    print "%s %s %s %s" % (tableName,databaseName,hostName,databseType)
            sql = '''
                    select  is_updated
                      from monitor_table_check 
                     where to_char(updatetime,'yyyy/mm/dd' )= to_char(trunc(sysdate),'yyyy/mm/dd') 
                       and upper(table_name) = upper('%s')
                       and upper(database_name) = upper('%s')
                       and upper(hostname) = upper('%s')
                       and upper(database_type) = upper('%s')
                ''' % (tableName,databaseName,hostName,databseType)
            req1 = oracleDB.select(sql)
            print req1
            if req1[0][0] == 1:
                print "数据准备好了"
                code = 0

            else:
                print "数据没有准备好，5分钟后再看"
                sleep(300)


    except:
        SendMail("%s [%s] except" % (tableName, jobName))

if __name__=='__main__':
    if (len(sys.argv) == 6):
        databaseName=sys.argv[1]
        tableName=sys.argv[2]
	    hostName=sys.argv[3]
	    databseType=sys.argv[4]
	    jobName=sys.argv[5]
        print "开始验证数据是否准备好........."
        print databaseName
        print tableName
	    print hostName
	    print databseType
	    print jobName
        starttime = datetime.datetime.now()
        print "[%s] [call procedures] [%s] runing..." % (starttime, "开始查询是否有结果")
        getFinshStatus(tableName,databaseName,hostName,databseType,jobName)
        endtime = datetime.datetime.now()
        print "[%s] [call procedures] [%s] Total time costs  :   %ds" % (endtime,"执行结束",(endtime - starttime).seconds)
    else:
        print "参数不对，请核对参数个数........"
        print "正确参数是5个，分别是数据库名，表名，IP，数据库类型，任务名"


