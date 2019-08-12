import SocketServer
import time
import sys
import csv
import cx_Oracle
sys.path.append('..')
import configure_info as configureInfo
from FAHP import FAHP_Method
from FAHP import Evaluation
from SQF import SQF_Method
import numpy as np
import pandas as pd
import csv
import json
import urllib
import urllib2
import random
csv_file = "./datafiles/evafiles/"
global weight_FAHP
global weight_SQF
algorithm = ['FAHP','SQF']

class Server(SocketServer.BaseRequestHandler):
    def handle(self):
        conn=self.request
        error_flag=0
        data_r=''
        Eva = Eva_Server()
        while True:
            data=data_r+conn.recv(1500)
            if not data:
                print("no data!")
                break
            while True:
                list1=data.split('\t',1)
                if not len(list1)==2:
                    data_r=data
                    break
                try:
                    row_l=int(list1[0])
                except:
                    print("list1",list1)
                    print("list1[0]",list1[0])
                    error_flag=1
                    print("row_length transform error!")
                    break
                if len(list1[1])<row_l:
                    data_r='\t'.join(list1)
                    break
                #print(list1[1][0:row_l])
                s_data = list1[1].split(',')
                Eva.send_data(s_data)
                data=list1[1][row_l:]
            if error_flag:
                break
        conn.close()

class Eva_Server():
    def send_data(self,s_data):
        global algorithm
        sava_s_data = ','.join(s_data)
        temp_result = []
        eva_result = []
        n = len(s_data)
        for i in range(0,n):
            s_data[i] = float(s_data[i])
        global weight_FAHP
        global weight_SQF
        E = Evaluation()
        senddata={'data':{'weight_FAHP':None,'weight_SQF':None,'eva_result_FAHP':None,'eva_result_SQF':None,'s_data':None},\
		'type':'eva_realtime','description':None}
        url = configureInfo.evaluaterealturl
        degree = E.Membership_matrix(matrix_level,s_data)
        eva_result_FAHP = E.fuzzy_evaluate_result(weight_FAHP,degree)
        eva_result_SQF = E.fuzzy_evaluate_result(weight_SQF,degree)
        eva_result.append(eva_result_FAHP)
        eva_result.append(eva_result_SQF)
        for i in range(0,len(eva_result)):
            eva_level = str(eva_result[i].index(max(eva_result[i]))+1)
            temp_result = []
            for j in range(0,len(eva_result[i])):
                temp_result.append(str(eva_result[i][j]))
            sava_eva_result = ','.join(temp_result)
            self.result_save(sava_s_data,sava_eva_result,'Matrix_level.csv','A.csv',eva_level,algorithm[i])



        senddata['data']['weight_FAHP']=weight_FAHP
        senddata['data']['weight_SQF']=weight_SQF
	senddata['data']['eva_result_FAHP']=eva_result_FAHP
    	senddata['data']['eva_result_SQF']=eva_result_SQF
	senddata['data']['s_data']=s_data
	senddata['description']=algorithm
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

    def result_save(self,s_data,eva_result,matrix_level,judge_matrix,eva_level,algorithm):
        #output = ['normal.','nmap.','smurf.']
        #i = random.randint(0,2)
        conn = cx_Oracle.connect(configureInfo.con_info)
        cur=conn.cursor()
        time_now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        sql="insert into EVA_PARAMETER"+" (eva_level,eva_unit,s_data,result,matrix_level,judge_matrix,insert_time) values('"+eva_level+"','"+algorithm+"','"+s_data+"','"+eva_result+"','"+matrix_level+"','"+judge_matrix+"',to_date('"+time_now+"','yyyy-mm-dd hh24:mi:ss'))"
        print(sql)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        #print(2)


if __name__=='__main__':
    global weight_FAHP
    global weight_SQF
    weight_FAHP = []
    F = FAHP_Method()
    E = Evaluation()
    A = []
    matrix_level = pd.read_csv(csv_file + "Matrix_level.csv").values
    for i in range(0,4):
        filename = csv_file + 'A' + str(i) + '.csv'
        tempA = pd.read_csv(filename).values
        A.append(tempA)
    weight_FAHP = F.get_global_weight(A)
    S = SQF_Method()
    data = pd.read_csv(csv_file + 'c.csv').values
    weight_SQF = S.Get_Weight(data)
    ip,port='192.168.138.201',8889
    server=SocketServer.ThreadingTCPServer((ip,port),Server)
    server.serve_forever()
    
    
