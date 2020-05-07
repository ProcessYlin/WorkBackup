# coding=UTF-8
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.cross_validation import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import cross_val_predict


columns = ['store',  'sal_qty', 'sal_prm_amt', 'inv_amt', 'lable']
data = pd.read_csv('/Users/lin/Desktop/data.csv', names=columns, sep=',')
# print data.head()
x = data[['store', 'sal_qty', 'sal_prm_amt', 'inv_amt']]
y = data[['lable']]
# print x, y
x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1)
# print x_train, x_test, y_train, y_test
# 导入方程容器
linreg = LinearRegression()
# 训练方程
linreg.fit(x_test, y_test)
print linreg.intercept_
print linreg.coef_

# 模型拟合测试集
y_pred = linreg.predict(x_test)
# 用scikit-learn计算MSE--均方差，RMSE--均方根差--（越小越好）
print "MSE: ", metrics.mean_squared_error(y_test, y_pred)
# print "RMSE: ", np.sqrt(metrics.mean_squared_error(y_test, y_pred))
# 生成预测值
predicted = cross_val_predict(linreg, x, y, cv=5)
print predicted
# 图形展示
fig, ax = plt.subplots()
# 预测值和实际值做散点图，越靠近 y=x，说明误差越小
ax.scatter(y, predicted)
# 刻画 y=x 的直线
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_xlabel('Measured')
ax.set_ylabel('Predicted')
plt.show()
















