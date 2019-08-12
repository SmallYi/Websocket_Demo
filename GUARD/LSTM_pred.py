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
from keras.utils import np_utils
from elephas.spark_model import SparkModel
from elephas.utils.rdd_utils import from_labeled_point,to_labeled_point
from elephas import optimizers as elephas_optimizers
from keras.optimizers import SGD
from elephas.mllib.adapter import to_vector, from_vector

from pyspark import SparkContext, SparkConf

# Create Spark context
conf = SparkConf().setAppName('LSTM_Spark_MLP')
sc = SparkContext(conf=conf)

def deal_x(x):
  x=np.array(x)
  x_data=x[1:]
  x_data=np.expand_dims(x_data,axis=2)
  return x_data

test_data=sc.textFile("output/data/z2.csv").map(lambda ln: deal_x([float(x) for x in ln.split(',')]))


model = load_model('model.h5')
adagrad = elephas_optimizers.Adagrad()
spark_model = SparkModel(sc,
                         model,
                         optimizer=adagrad,
                         frequency='epoch',
                         mode='synchronous',
                         num_workers=3)

# Test Spark model
spark_model.predict_classes(test_data,"output/data/prediction")






     



 
