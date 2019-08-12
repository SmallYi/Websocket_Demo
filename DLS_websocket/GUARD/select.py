import cx_Oracle
import sys
sys.path.append("..")
import configure_info as configureInfo
import Encoder
import random
import datetime

class Format_db_select:
 def __init__(self,tables,modelpara_dict):
    self.tables=tables
    self.model_name=modelpara_dict['model_name']

 def hour_data_select(self):
  dict1={}
  dict1=Encoder.import_coding(self.model_name)
  conn = cx_Oracle.connect(configureInfo.con_info)
  cur = conn.cursor()
  count_cloumn=[0]*60
  first=True
  osusername_set=()
  for tname in tables:
   i=0
   sql="select distinct os_username from "+tname
   print(sql)
   cur.execute(sql)
   osusernames=cur.fetchall()
   for osusername in osusernames:
       if osusername[0] not in osusername_set:
          osusername_set=osusername_set+(osusername[0],)
       sql="select count(distinct app_name),to_char(act_time,'hh24'),to_char(act_time,'mi') from "+tname+" where os_username='"+osusername[0]+"' group by to_char(act_time,'hh24'),to_char(act_time,'mi')"
       cur.execute(sql) 
       rows=cur.fetchall()
       for row in rows:
         j=int(row[2])
         if first:
           count_cloumn[j]=row[0]
         else:
           if count_cloumn[j]<row[0]:
             count_cloumn[j]=row[0]
       first=False
  print(count_cloumn)
  print(osusername_set)
  sum1=0
  for a in count_cloumn:
    sum1=sum1+a
  print(sum1)
  app=[None]*24
  noaction_code=Encoder.value_to_code('APP_NAME','noaction',dict1,self.model_name)
  with open(self.model_name+'.csv','wb') as pfile:
   with open(self.model_name+'_dect.csv','wb') as qfile:
    days=int(len(tables)*0.8)
    print("days=",days)
    d=0
    for d in range(len(tables)):
      tname=tables[d]
      i=0
      for i in range(len(osusername_set)):
         osusername=osusername_set[i]
         k=0
         for k in range(24):
             '''app[k]=[None]*60'''
             app[k]=[None]*61
             f=0
             for f in range(61):
               app[k][f]=[]
             app[k][60]=[0,]            
         sql="select app_name,to_char(act_time,'hh24'),to_char(act_time,'mi'),min(log_id) from "+tname+" where os_username='"+osusername+"' group by to_char(act_time,'hh24'),to_char(act_time,'mi'),app_name"
         cur.execute(sql) 
         rows=cur.fetchall()
         if rows:
           for row in rows:
             app[int(row[1])][int(row[2])].append(str(Encoder.value_to_code('APP_NAME',row[0],dict1,self.model_name)))
             #app[int(row[1])][int(row[2])].append(row[0])
             if int(row[3])==1:
                print(1)
                app[int(row[1])][60][0]=1
           h=0
           for h in range(24):
             m=flag=0
             for m in range(60):
               if not len(app[h][m])==0:
                  flag=1
                  break
             if flag==0:
                continue
             hour=noaction_code+h
             line=str(Encoder.value_to_code('OS_USERNAME',osusername,dict1,self.model_name))+','+str(hour)+","
             if d<days:
               pfile.write(line)
             else:
               qfile.write(line)  
             m=0
             for m in range(60):
                lmax=count_cloumn[m]
                y=len(app[h][m])
                for q in range(y,lmax):
                  app[h][m].append(str(noaction_code))                  
                line=','.join(app[h][m])+','
                if m==59:
                   line=','.join(app[h][m])+'\n'
                if d<days:
                  pfile.write(line)
                else:
                  qfile.write(line)
  cur.close()
  conn.close()

 def single_data_select(self):
    

