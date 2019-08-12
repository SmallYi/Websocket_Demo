import cx_Oracle
import random
import urllib
import urllib2
import time
import json
import configure_info as configureInfo
conn = cx_Oracle.connect(configureInfo.con_info)
cur = conn.cursor()
sql='select * from LSTM_537TT03OT_SINGLE'
cur.execute(sql)
rows=cur.fetchall()
senddata={'data':{'act_time':None,
                  'abnormal':None,  
                  'prediction':None,
                  'item':None,
                  'abnormal_rate':None},
          'type':'noguard_realtime',
          'description':{'agent_id':None,
                        'model_type':'all'}
         }
url = configureInfo.noguardrealturl
total=0
ab_num=0
agent_id=['537TT03OT','5VM45975','P02703102649','S2A58BGQ','WDWCASZ0627345']
for row in rows:
   total=total+1
   t=random.randint(0,4)
   senddata['data']['item']=row[0]
   senddata['data']['prediction']=row[1]
   senddata['data']['abnormal']=row[2]
   if senddata['data']['abnormal']==0:
       ab_num=ab_num+1
   senddata['data']['act_time']=str(row[4])
   senddata['data']['abnormal_rate']=ab_num/total
   senddata['description']['agent_id']=agent_id[t]
   data = urllib.urlencode({'dict':json.dumps(senddata)}).encode(encoding='UTF8') 
   req = urllib2.Request(url, data)
   response = urllib2.urlopen(req)
   time.sleep(3)
cur.close()
con.close()
