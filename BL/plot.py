# coding:UTF-8

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 导入数据
data = pd.read_table('/Users/lin/desktop/sub_pp.txt', sep='\t')
#print data
x = data.iloc[:, 0]
# print x
# 特征向量一
y = data.iloc[:, 1]
#print y
# 特征向量二
#label = data.iloc[:, 2]
# 标识
plt.scatter(x, y, label='M5')
# 画图
# plt.scatter(x[label == 0], y[label == 0], label='C0')
# plt.scatter(x[label == 1], y[label == 1], label='C1')
# plt.scatter(x[label == 2], y[label == 2], label='C2')
# plt.scatter(x[label == 3], y[label == 3], label='C3')
# plt.scatter(x[label==4], y[label==4], label='C4')
plt.xlabel('level')
plt.ylabel('distance')
plt.legend()
plt.show()
