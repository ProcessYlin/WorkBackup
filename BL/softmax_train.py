# coding:UTF-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_data(inputfile):
    '''
    input: inputfile(string)  训练样本的位置
    output: feature_data(mat)  特征
            lable_data(mat)    标签
            k(int)            类别的个数
    '''
    f = open(inputfile)  # 打开文件
    feature_data = []
    lable_data = []
    for line in f.readlines():
        feature_tmp = []
        feature_tmp.append(1)
        lines = line.strip().split(",")
        for i in xrange(len(lines) - 1):
            feature_tmp.append(float(lines[i]))
        lable_data.append(int(lines[-1]))
        feature_data.append(feature_tmp)
    f.close()
    return np.mat(feature_data), \
           np.mat(lable_data).T, len(set(lable_data))


def gradientascent(feature_data, lable_data, k, maxcycle, alpha):
    '''
    :param feature_data:  特征
    :param lable_data:    标签
    :param k:             类别的个数
    :param maxcycle:      最大的迭代次数
    :param alpha:         学习率
    :return: weights(mat) 权重
    '''
    m, n = np.shape(feature_data)
    # print m, n
    weights = np.mat(np.ones((n, k)))
    # print weights
    i = 0
    while i <= maxcycle:
        err = np.exp(feature_data * weights)
        if i % 100 == 0:
            print "t-------iter: ", i, \
                ", cost : ", cost(err, lable_data)
        rowsum = -err.sum(axis=1)
        rowsum = rowsum.repeat(k, axis=1)
        err = err / rowsum
        for x in range(m):
            err[x, lable_data[x, 0]] += 1
        weights = weights + (alpha / m) * feature_data.T * err
        i += 1
    return weights


def cost(err, lable_data):
    '''
    :param err:   exp的值
    :param lable_data: 标签的值
    :return: sum_cost / m(float): 损失函数的值
    '''
    # print 'point'
    m = np.shape(err)[0]
    # print m
    sum_cost = 0.0
    for i in xrange(m):
        if err[i, lable_data[i, 0]] / np.sum(err[i, :]) > 0:
            sum_cost -= np.log(err[i, lable_data[i, 0]] / np.sum(err[i, :]))
        else:
            sum_cost -= 0
    return sum_cost / m

def save_model(file_name, weights ):
    '''

    :param file_name: 保存的文件名
    :param weights: 模型
    '''
    f_w = open(file_name,"w")
    m , n =np.shape(weights)
    for i in xrange(m):
        w_tmp = []
        for j in xrange(n):
            w_tmp.append(str(weights[i, j]))
        f_w.write("\t".join(w_tmp) + "\n")
    f_w.close()

if __name__ == "__main__":
     # 导入数
    # 训练数据模型
    inputfile = '/Users/lin/Desktop/train_20170919.csv'
    #print load_data(inputfile)
    feature, label, k = load_data(inputfile)
    weights = gradientascent(feature, label, k, 5000, 0.2)
    # print  gradientascent(feature, label, k, 5000, 0.2)
    # 保存最终的模型
    save_model("weights_20170919", weights)
