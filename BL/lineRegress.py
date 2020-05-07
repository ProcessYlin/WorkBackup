
 1.机器学习线性回归
 #需要的库
 import matplotlib.pyplot as plt
 import pandas as pd
 import numpy  as np
 
 from sklearn import datasets, linear_model
 #流水表中数据没有表头，命名表头
 columns = ['sale_date','shop_no','bp_no','pro_id','gmv','cnt','discount_sale','type']
 #数据导入','分隔,读取数据
 df = pd.read_csv('liushui.txt',names = columns,sep = ',')
 head.df()
 #读取数据维度
 df.shape   #(18482245, 8)--（行，列）
 #准备样本特征
 X = df[['pro_id', 'cnt']]
 X.head()
 #样本输出
 y = df[['gmv']]
 y.head()
 #把X和y的样本组合划分成两部分，一部分是训练集，一部分是测试集
 from sklearn.cross_validation import train_test_split
 X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1)
 #运行scikit-learn的线性模型,scikit-learn的线性回归算法使用的是最小二乘法来实现的
 from sklearn.linear_model import LinearRegression
 linreg = LinearRegression()
 linreg.fit(X_train, y_train)
 #查看估计值
 print linreg.intercept_      #常数项
 print linreg.coef_           #变量前系数
 
 #模型测试,对于线性回归来说，一般用均方差（Mean Squared Error, MSE）或者均方根差(Root Mean Squared Error, RMSE)在测试集上的表现来评价模型的好坏。
 #模型拟合测试集
y_pred = linreg.predict(X_test)
from sklearn import metrics
# 用scikit-learn计算MSE
print "MSE:",metrics.mean_squared_error(y_test, y_pred)
# 用scikit-learn计算RMSE
print "RMSE:",np.sqrt(metrics.mean_squared_error(y_test, y_pred))

#模型做出来之后，我们一般通过筛选变量来测试，查看均方根差最小的，是最合适的
#使用交叉验证来，一般采用10折交叉验证
X = df[['pro_id', 'cnt']]
y = df[['gmv']]
from sklearn.model_selection import cross_val_predict
predicted = cross_val_predict(linreg, X, y, cv=10)
# 用scikit-learn计算MSE
print "MSE:",metrics.mean_squared_error(y, predicted)
# 用scikit-learn计算RMSE
print "RMSE:",np.sqrt(metrics.mean_squared_error(y, predicted))


#画图观察结果
fig, ax = plt.subplots()
ax.scatter(y, predicted)
ax.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=4)
ax.set_xlabel('Measured')
ax.set_ylabel('Predicted')
plt.show()
