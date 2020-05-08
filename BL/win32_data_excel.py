# -*- coding: utf-8 -*-
# @Time    : 2019/11/10 1:24 PM
# @Author  : ylin
# @Email   :
# @File    : pd_toexcel.py
# @Software: PyCharm
from openpyxl import Workbook
from openpyxl import load_workbook
from inspect import isfunction
from openpyxl.styles import Color, PatternFill, Font, Border, Side
from openpyxl.styles.colors import Color
from openpyxl.cell.cell import WriteOnlyCell
import json
import datetime
import numpy as np
import win32com.client as win32
from win32com.client import DispatchEx
import win32process
import win32api
import win32con

def writeExcel_area(file_path):
    data = np.array([
        [0                 ,1158         ,0                 ,202         ,0                 ,1            ,0             ,0   ,0    ,0],
        [0                 ,933         ,0                 ,169         ,0                 ,1            ,0             ,0   ,0    ,0],
        [0                 ,831         ,0                 ,130         ,0                 ,1            ,0             ,0   ,0    ,0],
        [0                 ,933         ,0                 ,163         ,0                 ,1            ,0             ,141 ,0    ,0],
        [0                 ,1171         ,0                 ,188         ,0                 ,1            ,0             ,166 ,0    ,0],
        [0                 ,896         ,0                 ,156         ,0                 ,1            ,0             ,229 ,0    ,0],
        [0                 ,837         ,0                 ,130         ,0                 ,1            ,0             ,265 ,0    ,0],
        [0                 ,924         ,0                 ,156         ,0                 ,0.97        ,0             ,311 ,0    ,0],
        [0                 ,1187         ,0                 ,189         ,0                 ,0.85        ,0             ,340 ,500  ,0],
        [880         ,880         ,150         ,150         ,0.67   ,0             ,404         ,322 ,468  ,0],
        [830         ,830         ,128         ,128         ,0.69   ,0             ,415         ,332 ,5000 ,0],
        [920         ,0                 ,155         ,0                 ,0.68   ,0             ,443         ,0   ,5000 ,0],
        [1170         ,0                 ,190         ,0                 ,0.737  ,0             ,565         ,0   ,0    ,0],
        [940         ,0                 ,175         ,0                 ,0      ,0             ,511         ,0   ,0    ,0],
        [930         ,0                 ,130         ,0                 ,0      ,0             ,530         ,0   ,0    ,0]
        ])
    # print(data.shape)
    [h, l] = data.shape
    # 预算年1、2月成交均价数据
    # print(data_fre.shape)
    area_list = ['华南','华南','东北','华东','华中','鲁豫','西南','西北','总公司','电商']
    xl_app = DispatchEx('Excel.Application')
    xl_app.Visible = True
    wb = xl_app.Workbooks.open(file_path)
    for num in range(len(wb.Sheets)):
        if any(area in wb.Sheets(num+1).Name for area in area_list) and  ('分级' not in wb.Sheets(num+1).Name):
            sheet = xl_app.Worksheets(wb.Sheets(num+1).Name)
            print(wb.Sheets(num+1).Name)
            # sheet.Cells(6,6).Value = 5555
            for i in range(h):
                for j in range(l):
                    # row_num 数据从指定行数开始追加，默认从1
                    sheet.Cells(i+6, j+63).Value = data[i][j]
                    print(data[i][j])
    wb.Save()
    wb.Close()
    xl_app.Quit()
    # 杀死残留的excel进程
    close_excel_by_force(xlApp)
    del xlApp

def close_excel_by_force(excel):
    # Get the window's process id's
    hwnd = excel.Hwnd
    t, p = win32process.GetWindowThreadProcessId(hwnd)
    # Ask window nicely to close  
    try:
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, p)
        if handle:
            win32api.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)
    except:
        pass


def main():
    # 设置该脚本可使用最大内存8G
    writeExcel_area(file_name)

if __name__ == '__main__':
    startime = datetime.datetime.now()
    file_name = r"C:\Users\yshh737\Desktop\商品预算模版-百丽品牌_百丽-总部品牌部（小范围）_191230_203747 (1).xlsx"
    main()
    endtime = datetime.datetime.now()
    print(endtime-startime)






    