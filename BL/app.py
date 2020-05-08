# encoding=utf-8
from flask import Flask
from flask import request, abort, Response
from win32com.client import DispatchEx
import os, stat
import json
import pythoncom
import logging
import socket
import requests
import psutil
import time
import datetime
import uuid

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='app.log',
                    filemode='a')

app = Flask(__name__)

test_active_exl = 'c:/code/test_data.xlsx'

def send_qywx_post(msg, file_name, **kwargs):
    try:
        post_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=37e6401c-f72c-421f-b604-09de26edee40'
        my_header = {'Content-Type': 'application/json'}
    
        # 获取本机电脑名
        myname = socket.gethostname()
        # 获取本机ip
        myaddr_ip = socket.gethostbyname(myname)
        post_msg = '【windows报警】 \n IP: %s 发生异常，请及时查看。\n 错误信息： %s  \n请求路径： %s ' % (myaddr_ip, json.dumps(msg), file_name)
        request_data = {'msgtype':'text', 'text':{'content': post_msg}}
        requests.post(url=post_url, json=request_data, headers=my_header)
    except Exception as e:
        print(e,"!!!!!!!!!!!!1")


def open_path_files(path, add_ip):
    logging.info('Prepare to deal path : %s' % path)
    if add_ip == '10.250.43.154':
        path = path.replace("/data/app/income/excel", "z:\\excel").replace("/", "\\")
    elif add_ip == '10.250.11.96':
        path = path.replace("/data/app/income/excel", "y:\\excel").replace("/", "\\")
    elif not os.path.exists(path):
        logging.error('path not exist !!!')
        return {'code': 400, 'msg': 'path not exist !!!'}
    else:
        return {'code': 400, 'msg': 'path not exist !!!'}
    for path_file in os.listdir(path):
        chmod_file = os.path.join(path, path_file)
        os.chmod(chmod_file, stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
        logging.info( '===%s=== chmod done' % chmod_file)
        f_name, f_ext = os.path.splitext(path_file)
        if f_ext == '.xlsx' and '~$' not in f_name:
            open_file = os.path.join(path, path_file)
            ret_info = win_method(open_file)
            if ret_info.get('code') != 200:
                logging.error("open path: %s  failed !!!  %s " % (path, ret_info))
                return ret_info
    logging.info('path : %s well done !!!' % path)
    return {'code': 200, 'msg': 'work done'}


@app.route('/upload', methods=['POST', 'GET'])
def upload_string():
    #上传部分
    logging.info('=====================coming==========================')
    file = request.files['file']
    logging.info('=====================The file is %s==========================' % file)
    path = "c:\\test\\" # 临时目录
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    unique = uuid.uuid1()
    try:
        filename = "temp-%s-%s.xlsx" % (nowTime, unique)
        fullfilename = path + filename
        file.save(fullfilename)
        logging.info('#########The file : %s have created done !!!###################' % filename)
        ##todo-- 文件清洗
        win_method(fullfilename)
        logging.info('Excel quited !!!  file: %s ok !!!' % filename)
        # 流式读取
        def send_file():
            store_path = fullfilename
            with open(store_path, 'rb') as targetfile:            
                while 1:                     
                    data = targetfile.read(20 * 1024 * 1024)  # 每次读取20M
                    if not data:
                        break
                    yield data
        response = Response(send_file(), content_type='application/octet-stream')
        response.headers["Content-disposition"] = 'attachment; filename=%s' % filename  # 如果不加上这行代码，导致下图的问题
        return response
    except Exception as e:
        logging.info({'code': 400, 'msg': '%s error !!! OR %s is invalid !!!' % (e, file_name)})
        return {'code': 400, 'msg': '%s error !!! OR %s is invalid !!!' % (e, file_name)}
        
        
def win_method(file_name):
    logging.info('Prepare open file: %s' % file_name)
    pythoncom.CoInitialize()
    try:
        xl_app = DispatchEx('Excel.Application')
        logging.info('Excel opened')
        xl_app.Visible = True
        xl_book = xl_app.Workbooks.open(file_name)
        logging.info('%s ########## opened' % file_name)
        xl_book.Save()
        logging.info('%s saved' % file_name)
        xl_book.Close()
        xl_app.quit()
        logging.info('Excel quited !!!  file: %s ok !!!' % file_name)
        return {'code': 200, 'msg': '%s ok' % file_name}
    except Exception as e:
        logging.info({'code': 400, 'msg': '%s error !!! OR %s is invalid !!!' % (e, file_name)})
        return {'code': 400, 'msg': '%s error !!! OR %s is invalid !!!' % (e, file_name)}


@app.route('/visible', methods=['POST', 'GET'])
def excel_visible():
    mem_usage = psutil.virtual_memory().percent
    if int(mem_usage) > 95:
        abort(400, u'内存使用率：负载高于95！')
    logging.info('内存使用率：负载高于95 #############')
    file_name = ''
    add_ip = request.remote_addr
    #print(add_ip)
    if request.method == "GET":
        file_name = request.args.get('file_name', '')
    if request.method == "POST":
        file_name = request.form.get('file_name', '') or request.json.get('file_name')
    if not file_name:
        abort(404, u'没有文件路径！')
    logging.info('=====================%s==========================' % file_name)
    try:
        msg = open_path_files(file_name, add_ip)
        if msg.get('code') != 200:
            logging.info('no code 200 begin send msg #############')
            send_qywx_post(msg, file_name)
            logging.info('no code 200 begin send msg ########send done#####')
            abort(400, msg)
        else:
            return json.dumps(msg)
    except Exception as e:
        abort(400, *e.args)


@app.route('/mon_exl_active', methods=['GET'])
def mon_exl_active():
    res = win_method(test_active_exl)
    if res.get('code') != 200:
        send_qywx_post(res, 'monitor_excel_active 方法 !!!')
        abort(400, res)
    else:
        return json.dumps(res)


@app.route('/get_host_status', methods=['GET'])
def get_host_status():
    running_exl = []
    mem_usage = psutil.virtual_memory().percent
    cpu_usage = psutil.cpu_percent(interval=1)
    pids = psutil.pids()
    for pid in pids:
        p = psutil.Process(pid)
        if 'EXCEL' in p.name() or 'excel' in p.name():
            run_time = time.time() - p.create_time()
            if run_time >= 600:
                running_exl.append('pid:%s  %s   runing: %s seconds' % (pid, p.name(), run_time))
    if int(mem_usage) > 95 or int(cpu_usage) > 99 or len(running_exl) > 0:
        msg = 'Memory_use_rate is %s \n CPU_use_rate is %s  \n Out_time_excel_qty is %s ' % (mem_usage, cpu_usage, len(running_exl))
        # resp_msg = {'code':400, 'msg': msg}
        send_qywx_post(msg, 'get_host_status 消息！！！ ')
        #print(msg)
        return json.dumps({'code': 400, 'msg': msg}, ensure_ascii=False)
    return json.dumps({'code': 200, 'msg': 'host 正常'})

#每天清除临时文件
@app.route('/file_clear', methods=['POST','GET'])
def file_day_clear():
    path = "c:\\test" # 临时目录
    nowTime = datetime.datetime.now().strftime('%Y-%m-%d')
    try:
        for file_name in os.listdir(path):
            use_file = os.path.join(path, file_name)
            if file_name[5:15] < nowTime:
                os.remove(use_file)
            else:
                return {'code': 200, 'msg': 'file not exist !!!'}
    except Exception as e:
        logging.info({'code': 400, 'msg': '%s error !!! OR %s is invalid !!!' % (e, file_name)})
        return {'code': 400, 'msg': '%s error !!! OR %s is invalid !!!' % (e, file_name)}
       

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
