import numpy as np 
from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential, load_model
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from keras.layers.convolutional import Conv1D, MaxPooling1D
from sklearn.preprocessing import LabelBinarizer
from sklearn.preprocessing import LabelEncoder
import re
import json
import pandas as pd
import os
import tensorflow as tf
import csv
import sys
import cx_Oracle
sys.path.append('..')
import configure_info as configureInfo
from keras.utils import np_utils
from elephas.spark_model import SparkModel
from elephas.utils.rdd_utils import from_labeled_point,to_labeled_point
from elephas import optimizers as elephas_optimizers
from keras.optimizers import SGD
from elephas.mllib.adapter import to_vector, from_vector

from pyspark import SparkContext, SparkConf
import getpass

# Create Spark context
conf = SparkConf().setAppName('LSTM_Spark_MLP')
sc = SparkContext(conf=conf)

#load_data
def from_rdd_point(rdd, categorical=False, nb_classes=None):
    '''
    Convert a RDD back to a pair of numpy arrays
    '''
    features = np.asarray(rdd.map(lambda lp: lp[1]).collect())
    labels = np.asarray(rdd.map(lambda lp: lp[0]).collect(), dtype='int32')
    if categorical:
        if not nb_classes:
            nb_classes = np.max(labels)+1
        temp = np.zeros((len(labels), nb_classes))
        for i, label in enumerate(labels):
            temp[i, label] = 1.
        labels = temp
        print(np.shape(labels))
    print(np.shape(features))
    return labels,features
def deal(x,Lable_num):
  x=np.array(x)
  x_data=x[1:]
  y_data=x[0]-1
  y_data = np_utils.to_categorical(y_data, Lable_num)
  x_data=np.expand_dims(x_data,axis=2)
  return x_data,y_data

def getModelParameter_fromOracle(modelname):
  conn = cx_Oracle.connect(configureInfo.con_info)
  cur = conn.cursor()
  sql="select LABLE_NUM,COLUMN_NUM,target_dimension from guard_parameter where model_name='"+modelname+"'"
  cur.execute(sql) 
  row=cur.fetchone()
  modelparameter={}
  if row:
    modelparameter['Lable_num']=row[0]
    modelparameter['Column_num']=int(round((row[1]-1)*row[2]))
    print("1111111111111111111"+str(modelparameter['Column_num']))
  cur.close()
  conn.close()
  return modelparameter

if __name__=='__main__':
        modelname=sys.argv[1]
        modelpara_dict=getModelParameter_fromOracle(modelname)
        if not modelpara_dict:
           exit -1
        path="output/GUARD/"+modelname+"/"+modelname+"_study.csv"
	train_data=sc.textFile(path).map(lambda ln: deal([float(x) for x in ln.split(',')],modelpara_dict['Lable_num']))
	
	# LSTM with Dropout and CNN classification
	max_review_length = modelpara_dict['Column_num']  #1824

	model=Sequential()

	model.add(Conv1D(activation="relu", padding="same", filters=64, kernel_size=5,input_shape=(modelpara_dict['Column_num'],1)))

	model.add(MaxPooling1D(pool_size=4))

	model.add(LSTM(100,dropout=0.2, recurrent_dropout=0.2))

	model.add(Dense(modelpara_dict['Lable_num'],activation='softmax'))

	print(model.summary())

	sgd = SGD(lr=0.1)
	model.compile(loss='categorical_crossentropy',optimizer=sgd)
	adagrad = elephas_optimizers.Adagrad()
	spark_model = SparkModel(sc,
		                 model,
		                 optimizer=adagrad,
		                 frequency='epoch',
		                 mode='synchronous',
		                 num_workers=3)

	# Train Spark model
	spark_model.train(train_data, nb_epoch=1, batch_size=32, verbose=2, validation_split=0.1)
        spark_model.master_network.save('model/'+modelname+'/'+modelname+'.h5')
	# Evaluate Spark model by evaluating the underlying model
	#score = spark_model.master_network.evaluate(x_test, y_test, verbose=2)
	#print('Test accuracy:', score[1])






     



 
