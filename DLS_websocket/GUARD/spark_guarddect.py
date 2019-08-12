#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
 Counts words in UTF8 encoded, '\n' delimited text received from the network every second.
 Usage: network_wordcount.py <hostname> <port>
   <hostname> and <port> describe the TCP server that Spark Streaming would connect to receive data.

 To run this on your local machine, you need to first run a Netcat server
    `$ nc -lk 9999`
 and then run the example
    `$ bin/spark-submit examples/src/main/python/streaming/network_wordcount.py localhost 9999`
"""
from __future__ import print_function

import sys
import time
import json
import urllib
import urllib2
import csv
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import cx_Oracle
import Encoder
import os
sys.path.append('..')
import configure_info as configureInfo
import numpy as np
from keras.models import Sequential, load_model, model_from_yaml
from elephas.spark_model import SparkModel
from elephas import optimizers as elephas_optimizers
from keras.optimizers import SGD
from itertools import tee
first=True
column_num=0
codefield=[]
parameters=None
def code_Judge(row_one):
     code_field=[]       # label is at code_field[0]
     for i in range(len(row_one)):
        try:
           float(row_one[i])
        except: 
           code_field.append(i)    
     return code_field

def deal(line,modelname,dict1,weight_list):
    #print('deal5555555555',line)
    if line:
       line_list=line.split("\t",1)
       if line_list and len(line_list)==2:
          if line_list[0]==modelname and line_list[1]:
              return code(line_list[1],modelname,dict1,weight_list)
 
def code(data,mname,dict1,weight_list):
    global first,column_num,codefield
    data=data.encode('utf-8')
    data_list=data.split(",")
    #print('88888888888weight_list',weight_list)
    dmi_list=[] 
    if first:
       column_num=len(data_list)
       codefield=code_Judge(data_list)
       first=False
       print("codefield:",codefield)
    for i in range(column_num):
      if i+1 in weight_list: 
         if i in codefield:
            dmi_list.append(str(Encoder.value_to_code(i+1,data_list[i],dict1,mname)))
         else:
            dmi_list.append(data_list[i])
    data_list2=np.expand_dims(dmi_list,axis=2)
    #print('77777777777777777777777777data_list',data_list2)
    return data,data_list2

def prediction(rdd,yaml,dict2,modelname):
    global parameters
    #print('6666666666666666666',rdd.collect())
    code_iterator, value_iterator = tee(rdd, 2)
    print('code_iterator',code_iterator,'value_iterator',value_iterator,'\n')
    data_code = np.asarray([y for x, y in code_iterator])
    data_value = np.asarray([x for x, y in value_iterator])
    model = model_from_yaml(yaml)
    model.set_weights(parameters)
    pred_code=model.predict_classes(data_code)
    return result_send_save(pred_code,data_value, modelname)
 
def result_send_save(pred_code,data_value,modelname):
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur=conn.cursor()
    url = configureInfo.guardrealturl
    senddata={'data':{'item':None,'output':None,'time':None,'number':None,'modelname':modelname},'type':'guard_realtime','description':None}
    for i in range(len(pred_code)):    
	    pred_value=Encoder.code_to_value(0,pred_code[i]+1,dict2)            
	    print("prediction:",pred_value)
	    time_now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
	    sql="insert into "+result_table+" (data,output,insert_time) values('"+data_value[i]+"','"+pred_value+"',to_date('"+time_now+"','yyyy-mm-dd hh24:mi:ss'))"
	    print(sql)
            try:
                cur=conn.cursor()
                cur.execute(sql)
            except Exception as e:
                print(e)   
	    senddata['data']['item']=data_value[i]
	    senddata['data']['output']=pred_value
	    senddata['data']['time']=time_now
	    print(senddata)
	    data = urllib.urlencode({'dict':json.dumps(senddata)}).encode(encoding='UTF8') 
	    req = urllib2.Request(url)
            times=0
            while True:
               try:             
	          response = urllib2.urlopen(req,data,3)
               except:
                  times=times+1
                  print('Websocket connect test:'+str(times))
                  if times<20:
                     continue
                  else:
                     break
               else:
                  break
    try:
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(e)
    return pred_value

def stopByMarkFile(ssc):
    path="stop.txt"
    url = configureInfo.changemodelurl
    if os.path.exists(path):
       print("after 5 seconds stopping spark streaming!")
       time.sleep(5)
       ssc.stop()
       os.remove(path)
       data = urllib.urlencode({'dict':json.dumps('stop')}).encode(encoding='UTF8') 
       req = urllib2.Request(url, data)
       response = urllib2.urlopen(req)
    else:
       print("No stop signal detected!")

   
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: spark_guarddect.py <modelname>", file=sys.stderr)
        exit(-1)
    modelname=sys.argv[1]
    sql="select result_table,feature_extraction from guard_parameter where model_name='"+modelname+"'"
    conn=cx_Oracle.connect(configureInfo.con_info)
    cur=conn.cursor()
    cur.execute(sql)
    row=cur.fetchone()
    cur.close()
    conn.close()
    if row:
            print(row)
            pfile=open('model/model_now.txt','w')
            pfile.write(modelname)
            pfile.close()
            result_table=row[0]
            sql='''
                    CREATE TABLE %s
                    (
                            DATA VARCHAR2(1204 BYTE) PRIMARY KEY,
                            OUTPUT VARCHAR2(64 BYTE),
                            INSERT_TIME DATE
                    )
                ''' % result_table
            try:
                    conn=cx_Oracle.connect(configureInfo.con_info)
                    cur=conn.cursor()
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    print('555555555555555CREATE TABLE %s success.' % result_table)
            except Exception as e:
                    print(e)
	    dict1={}
	    dict1=Encoder.import_coding(modelname)
	    dict2={}
	    dict2=Encoder.import_key(modelname)
            if row[1]:
                    weight_list=[]
                    for k,v in eval(row[1]):
                            weight_list.append(k)
                    #print(weight_list)
		    sc = SparkContext(appName="PythonStreamingNetworkWordCount")
		    ssc = StreamingContext(sc, 1)
		    model = load_model('model/'+modelname+'/'+modelname+'.h5')
		    yaml = model.to_yaml()
		    parameters = model.get_weights()
		    #parameters = sc.broadcast(init)
		    brokers="master:2181,slave1:2181,slave2:2181"
		    topic='HelloKafka'
		    lines=KafkaUtils.createStream(ssc,brokers, "spark-streaming-consumer", {topic: 1})
		    liner = lines.map(lambda x: x[1])
		    liner.foreachRDD(lambda rdd:stopByMarkFile(ssc))
		    data=liner.map(lambda line:deal(line,modelname,dict1,weight_list))
		    pred=data.mapPartitions(lambda rdd:prediction(rdd,yaml,dict2,modelname))
		    #pred.foreachRDD(lambda rdd:rdd.saveAsTextFile("output/output"))
		    pred.pprint()
		    ssc.start()
		    ssc.awaitTermination()
            else:
                    print("This model:"+modelname+"  has not finish pca part")
    else:
            print("There is no this table:"+modelname)
