# coding:UTF-8
import numpy as np
import random as rd


def load_weights(weights_path):
    '''
    :param weights_path:权重的存储位置
    :return: weights(mat) 讲权重存到矩阵中
             m(int)权重的行数
             n(int)权重的列数
    '''
    f = open(weights_path)
    w = []
    for line in f.readlines():
        w_tmp = []
        lines = line.strip().split('\t')
        for x in lines:
            w_tmp.append(float(x))
        w.append(w_tmp)
    f.close()
    weights = np.mat(w)
    m, n = np.shape(weights)
    return weights, m, n

def load_data_file(inputfile):
    '''
    input: inputfile(string)  训练样本的位置
    output: feature_data(mat)  特征
            lable_data(mat)    标签
            k(int)            类别的个数
    '''
    f = open(inputfile)  # 打开文件
    feature_data = []
    for line in f.readlines():
        feature_tmp = []
        feature_tmp.append(1)
        lines = line.strip().split(",")
        for i in xrange(len(lines)):
            feature_tmp.append(float(lines[i]))
        feature_data.append(feature_tmp)
    f.close()
    return np.mat(feature_data)

def load_data(num, m):
    '''
    :param num: 生成的测试样本的个数
    :param m:   样本的维度
    :return: testdataset(mat) 生成的测试样本
    '''

    testdataset = np.mat(np.ones((num, m)))
    for i in xrange(num):
        # 读取测试文件中的每一列
        # 导入第1列的数据
        testdataset[i, 1] = test_data_file[i, 1]
        # 导入第2列的数据
        testdataset[i, 2] = test_data_file[i, 2]
        # 导入第3列的数据
        testdataset[i, 3] = test_data_file[i, 3]
        # 导入第4列的数据
        testdataset[i, 4] = test_data_file[i, 4]
        # 导入第5列的数据
        testdataset[i, 5] = test_data_file[i, 5]
    return testdataset


def predict(test_data, weights):
    '''
    :param test_data: 测试数据的特征
    :param weights: 模型的权重
    :return: h_argmax(axis=1) 所属类别
    '''
    # 生成的模型是一个3*4的矩阵，每一行测试数据与模型矩阵想乘，取概率值最大的结果
    h = test_data * weights
    # 此处需要加深理解
    return h.argmax(axis=1)


def save_result(file_name, result):
    '''
    :param file_name: 保存最终结果的文件名
    :return: 最终的预测结果
    '''
    f_result = open(file_name, 'w')
    m = np.shape(result)[0]
    for i in xrange(m):
        f_result.write(str(result[i, 0]) + '\n')
    f_result.close()


def save_result_end(file_name, result):
    '''
    :param file_name: 保存最终结果的文件名
    :return: 最终的预测结果
    '''
    f_result = open(file_name, 'w')
    m = np.shape(result)[0]
    for i in xrange(m):
        f_result.write(str(result[i, 0]) + '\n')
    f_result.close()


if __name__ == "__main__":
    # 导入训练模型
    print "---------load model----------"
    w, m, n = load_weights("/Users/lin/Desktop/百丽标签预测/多分类算法/weights_20170919")
    print 'maxtr is : %d' % m
    # 导入测试数据
    print "---------load data-----------"
     # 导入数
    inputfile = '/Users/lin/Desktop/test_20170919.csv'
    test_data_file =  load_data_file(inputfile)
    print test_data_file
    # print test_data[1, 1]
    # 导入测试数据
    test_data = load_data(5000, m)
    print test_data
    #print test_data
    # 用模型进行预测
    result = predict(test_data, w)
    #print result
    # 保存预测结果
    # save_result("result",  result)
    # 保存输出文件
    with open("./baili_20170920_result.txt", "w") as file:
        for r in range(len(test_data)):
            file.write("\t".join(map(str, [test_data_file[r][0], result[r][0]])) + "\n")
            print test_data_file[r][0]