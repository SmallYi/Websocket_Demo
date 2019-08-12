import socket
import time
import sys
import csv
import cx_Oracle
sys.path.append('..')
import configure_info as configureInfo
from FAHP import FAHP_Method
from FAHP import Evaluation
import numpy as np
import pandas as pd
import csv
import json
import urllib
import urllib2
import random
csv_file = "./datafiles/evafiles/"

global weight

class Eva_Server():
    def send_data(self,s_data):
        sava_s_data = ','.join(s_data)
        temp_result = []
        n = len(s_data)
        for i in range(0,n):
            s_data[i] = float(s_data[i])
        global weight
        E = Evaluation()
        senddata={'data':{'weight':None,'eva_result':None,'s_data':None},'type':'eva_realtime','description':None}
        url = configureInfo.evaluaterealturl
        degree = E.Membership_matrix(matrix_level,s_data)
        eva_result = E.fuzzy_evaluate_result(weight,degree)

        for i in range(0,len(eva_result)):
            temp_result.append(str(eva_result[i]))
        sava_eva_result = ','.join(temp_result)
        result_save(sava_s_data,sava_eva_result,'Matrix_level.csv','A')

        senddata['data']['weight']=weight
	senddata['data']['eva_result']=eva_result
	senddata['data']['s_data']=s_data
	print('senddata:',senddata)
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

def result_save(s_data,eva_result,matrix_level,judge_matrix):
    output = ['normal.','nmap.','smurf.']
    i = random.randint(0,2)
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur=conn.cursor()
    time_now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

    sql="insert into EVA_PARAMETER"+" (output,s_data,result,matrix_level,judge_matrix,insert_time) values('"+output[i]+"','"+s_data+"','"+eva_result+"','"+matrix_level+"','"+judge_matrix+"',to_date('"+time_now+"','yyyy-mm-dd hh24:mi:ss'))"
    print(sql)
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    #print(2)



if __name__=='__main__':

    modelname=sys.argv[1]
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur = conn.cursor()
    sql="select name from GUARD_PARAMETER where model_name = '"+modelname+"'"
    cur.execute(sql) 
    row=cur.fetchone()
    cur.close()
    conn.close()
    if row:
        global weight
        weight = []
        F = FAHP_Method()
        E = Evaluation()
        Eva = Eva_Server()
        A = []
        matrix_level = pd.read_csv(csv_file + "Matrix_level.csv").values
        for i in range(0,4):
            filename = csv_file + 'A' + str(i) + '.csv'
            tempA = pd.read_csv(filename).values
            A.append(tempA)
        weight = F.get_global_weight(A)
        while True:
            try:
                with open("./datafiles/evafiles/c.csv",'r') as rfile:
                    reader=csv.reader(rfile)
                    for row in reader:
                        #data=modelname+"\t"+",".join(row[0:-1])
                        #print("row:",row)
                        if row[0] == 'i0':
                            pass
                        else:
                            #print("row:",row)
                            #data=",".join(row)
                            #print(type(data))
                            Eva.send_data(row)
                            time.sleep(1)
                    rfile.close()
            finally:
                pass

