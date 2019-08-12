# -*-coding:utf-8-*-
# 数据集使用KDD99，我们从所有数据集中的正常数据集
import pandas as pd
from sklearn.preprocessing import StandardScaler
from numpy import *
import numpy as np
import csv
import os
import math
import xgboost as xgb
import sys
sys.path.append('..')
import configure_info as configureInfo
import results_save_send as sendweb
import cx_Oracle
from xgboost import XGBClassifier

# 数据预处理
path_KDD_test = '/home/apple/Documents/MacToLinux/KDDcup_study.csv'

# 算法部分
params = {
    'max_depth': 10,
    'subsample': 1,
    'verbose_eval': True,
    'seed': 12,
    'objective':'binary:logistic'
}

def zeroMean(dataMat):
    meanVal = np.mean(dataMat,axis=0) # average lie
    newData = dataMat-meanVal
    return newData,meanVal

def max_min_normalization(arr):
    arr = arr.tolist()
    list = []
    for x in arr:
        x = float(x - np.min(arr)) / (np.max(arr) - np.min(arr))
        list.append(x)
    return list

def fileOpenWrite(stu, path):
    with open(path, mode='a', encoding='utf-8', newline='') as out:
        csv_write = csv.writer(out, dialect='excel')
        csv_write.writerow(stu)


def calc(data):
    n=len(data) # 10000个数
    niu=0.0 # niu表示平均值,即期望.
    niu2=0.0 # niu2表示平方的平均值
    niu3=0.0 # niu3表示三次方的平均值
    for a in data:
        niu += a
        niu2 += a**2
        niu3 += a**3
    niu /= n
    niu2 /= n
    niu3 /= n
    sigma = math.sqrt(niu2 - niu*niu)
    return [niu,sigma,niu3]

def calc_stat(data):
    [niu, sigma, niu3]=calc(data)
    n=len(data)
    niu4=0.0 # niu4计算峰度计算公式的分子
    for a in data:
        a -= niu
        niu4 += a**4
    niu4 /= n
    skew =(niu3 -3*niu*sigma**2-niu**3)/(sigma**3) # 偏度计算公式
    kurt=niu4/(sigma**4) # 峰度计算公式:下方为方差的平方即为标准差的四次方
    return [niu, sigma,skew,kurt]

def test_pca(data, N):
    print("PCA Processing")
    newData, meanVal = zeroMean(data)
    print("newdata222222222222222"+str(np.shape(data)))
    covMat = np.cov(newData, rowvar=0)
    Diag = np.diag(covMat)
    tot = sum(Diag)
    var_exp = [(Diag[i]) / tot for i in range(len(Diag))]
    eigValIndice = np.argsort(Diag)
    print("diagdata222222222222222"+str(len(Diag)))
    n = int(round(len(Diag)*N))
    n_eigValIndice = eigValIndice[-1:-(n+1):-1]
    New_List = []
    for i in range(n):
        New_List.append((n_eigValIndice[i]+1, var_exp[n_eigValIndice[i]]))
    return New_List


def test_Xgboost(x, y1):
    print("Xgboost processing")
    y = max_min_normalization(y1)
    xgtrain = xgb.DMatrix(x, label=y)
    bst = xgb.train(params, xgtrain, num_boost_round=10)
    fmap = 'weight'
    importance = bst.get_score(fmap='', importance_type=fmap)
    print(fmap,importance)
    print('\n')
    # print(bst.get_dump(with_stats=False))
    fmap = 'gain'
    importance = bst.get_score(fmap='', importance_type=fmap)
    print(fmap,importance)
    print('\n')
    # print(bst.get_dump(with_stats=True))
    fmap = 'cover'
    importance = bst.get_score(fmap='', importance_type=fmap)
    print(fmap,importance)
    print('\n')
    # print(bst.get_dump(with_stats=True))

def XGB(x,y,N):
    print("XGBoost importance of feature score")
    model = XGBClassifier()
    model.fit(x, y)
    # feature importance
    featureImportant = model.feature_importances_
    # print(featureImportant)
    list_feature = featureImportant.tolist()
    xgb_Dictionary = {}
    for i in range(len(featureImportant)):
        xgb_Dictionary[i+1] = list_feature[i]
    # print(xgb_Dictionary)
    Tuple_xgbSorted = sorted(xgb_Dictionary.items(), key = lambda item:item[1], reverse = True)
    length_xgbSelected = int(round(len(featureImportant) * N))
    Result_xgbSelected = []
    for j in range(length_xgbSelected):
        Result_xgbSelected.append(Tuple_xgbSorted[j])
    return Result_xgbSelected
    # print(type(featureImportant)) #<type 'numpy.ndarray'>
    # print(len(featureImportant))
    

#峰度：概率密度在均值处峰值高低的特征，假设满足高斯分布
def kurtosis(data):
    print("kurtosis processing")
    dic_kurtosis = {}
    for i in range(40):
        [niu, sigma, skew, kurt] = calc_stat(data[:, i])
        dic_kurtosis[i+1] = kurt
    return dic_kurtosis


def fetch_to_file(mname,filename,weights):
    wl=[]
    for k,v in weights:
       wl.append(k)
    with open(filename,'r') as rfile:
        with open("./datafiles/studyfiles/"+mname+'_study.csv','w') as wfile:
          data_reader=csv.reader(rfile)
          data_writer=csv.writer(wfile)
          for row in data_reader:
             r_list=[]
             r_list.append(row[0])
             for i in range(len(row)):
                if i in wl:
                   r_list.append(row[i])
             data_writer.writerow(r_list)

                    
if __name__ == '__main__':
    print("Main processing")
    mname=sys.argv[1]
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur = conn.cursor()
    sql="select target_dimension,dimension_algorithm from guard_parameter where model_name='"+mname+"'"
    cur.execute(sql)
    row=cur.fetchone()    
    cur.close()
    conn.close()
    if row:
      N = row[0]
      print(N)
      algorithm=row[1]
      path_normal="./datafiles/codefiles/"+mname+'_code.csv'
      if os.path.exists(path_normal):
        if os.path.getsize(path_normal):
            df = pd.read_csv(path_normal)
            print("dfdata222222222222222"+str(np.shape(df)))
            X_data = df.iloc[:, 1:].values  #not include label_column
            print('333333333333333',X_data[0],type(X_data[0]))

            #X_data.astype(float) # change type

            result=[]
            if algorithm=='pca':             
              result = test_pca(X_data, N)
            elif algorithm=='XGBoost':
              Y1 = df.iloc[0:df.shape[0], 0].values  # Y是标签
              result = XGB(X_data, Y1, N)
            print(result)  
            conn = cx_Oracle.connect(configureInfo.con_info)
   	    cur = conn.cursor()
            sql="update guard_parameter set feature_extraction='"+str(result)+"' where model_name='"+mname+"'"
            cur.execute(sql) 
            conn.commit() 
            cur.close()
            conn.close()
            fetch_to_file(mname,path_normal,result)
            clientdct={'type':'progress','data':50,'description':'PCA finish'}
            sendweb.postresult_newmodel_to_server(clientdct) 
            clientdct={'type':'weights','data':result,'description':'PCA finish'}            
            sendweb.postresult_newmodel_to_server(clientdct)  
        else:
            print('File is null!')
      else:
          print('Exists no this file')
    else:
       print('There is no model:'+mname)

   

