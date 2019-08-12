#coding=utf-8
import numpy as np
import csv
import pandas as pd


class SQF_Method():
    def __init__(self):
        pass

    def Get_Weight(self,li):
        li=(li-li.min())/(li.max()-li.min())
        #最大最小标准化
        m, n = li.shape
        #m,n为矩阵行和列数
        k = 1 / np.log(m)
        yij = li.sum(axis=0)  # axis=0列相加 axis=1行相加
        pij = li / yij
        test = pij * np.log(pij)
        test = np.nan_to_num(test)
        #将nan空值转换为0
        ej = -k * (test.sum(axis=0))
        # 计算每种指标的信息熵
        wi = (1 - ej) / np.sum(1 - ej)
        #计算每种指标的权重
        for i in range(0,len(wi)):
            wi[i] = round(wi[i],4)
        return wi.tolist()

