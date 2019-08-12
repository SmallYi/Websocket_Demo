#-*-coding:utf-8-*-
#import urllib.parse  
#import urllib.request
import json
import urllib
import urllib2
import cx_Oracle
import time
import configure_info as configureInfo

def save_to_oracle(tablename,resultdict,predval,abflag):
 conn = cx_Oracle.connect(configureInfo.con_info)
 cur = conn.cursor()
 sql="insert into "+tablename+" values(data='"
 i=0
 data=""
 for key,value in resultdict.items():
   data=data+value+" "
 sql=sql+data+"',prediction_value="+str(predval)+",abnormal_flag="+str(abflag)+",insert_time=value(to_date('"+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"','yyyy-mm-dd hh24:mi:ss'))"+")"
 print(sql)
 cur.execute(sql)
 conn.commit()
 cur.close()
 conn.close()

#dict to string
def dict_to_string(dict1):
 str1=""
 for key,value in dict1.items():
   str1=str1+key+":"+value+"\n"
 return str1


#向服务器发送最新行realtime内容
def postresult_realtime_to_server(senddata):
 url = configureInfo.realturl
 if senddata==None:
  return	   
 data = urllib.urlencode({'dict':json.dumps(senddata)}).encode(encoding='UTF8') 
 req = urllib2.Request(url, data)
 response = urllib2.urlopen(req)
 #data = urllib.parse.urlencode({'dict':json.dumps(senddata)}).encode(encoding='UTF8') 
 #req = urllib.request.Request(url, data)
 #es_data = urllib.request.urlopen(req)

#向服务器发送最新行newmodel内容
def postresult_newmodel_to_server(senddata):
 url = configureInfo.newmurl
 if senddata==None:
  return	   
 data = urllib.urlencode({'dict':json.dumps(senddata)}).encode(encoding='UTF8') 
 req = urllib2.Request(url, data)
 response = urllib2.urlopen(req)


def send_realtime_to_webclient(s_resultstr,s_predval,s_abflag,s_bval,w_resultstr,w_predval,w_abflag):
 sendmsg={}
 model_para={}
 sendmsg['spred']=s_predval
 sendmsg['sflag']=s_abflag
 sendmsg['wpred']=w_predval
 sendmsg['wflag']=w_abflag
 model_para['baseline_value']=s_bval
 model_para['data']=s_resultstr
 minfo=dict_to_string(model_para)
 sendmsg['smodelinfo']=minfo
 model_para.clear()
 model_para['baseline_value']="all"
 model_para['data']=w_resultstr
 minfo=dict_to_string(model_para)
 sendmsg['wmodelinfo']=minfo
 postresult_to_server(sendmsg)
 print(sendmsg)
 
