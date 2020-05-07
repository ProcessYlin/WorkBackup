# coding:UTF-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_data(inputfile):
    print inputfile
    with open(inputfile, "rb")  as f:
        feature_data = [map(int, line.strip().split(",")) for line in f]
    return np.mat(feature_data)


if __name__ == "__main__":
    # 导入数
    # 训练数据模型
    inputfile = '/Users/lin/Desktop/data_x.csv'
    # print load_data(inputfile)
    test_data = load_data(inputfile)
    #print test_data

    #print test_data
    #print test_data[[0, -1]]
    # print test_data[1, 2]
    a_count = 0
    b_count = 0

    for line in test_data:
        a, b = line[0, 0], line[0, 1]
        if a == b:
            a_count += 1
        else:
            b_count += 1
    print "a_count", a_count
    print "b_count", b_count

