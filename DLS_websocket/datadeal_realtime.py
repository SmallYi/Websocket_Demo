import get_Modelparameter as getmpara
import Encoder
import cx_Oracle
import configure_info as configureInfo
import time
import results_save_send as rss

tablename=configureInfo.tablename
sbaseline=configureInfo.signal_baseline
wbaseline=configureInfo.whole_baseline
Code_dict1={} #code
fname={}
smpara={} #signal model parameter
wmpara={} #whole model parameter

#return dirt:key--fieldname value--column number
def get_filedname_from_oracle(tablename):
	conn = cx_Oracle.connect(configureInfo.con_info)
	cur = conn.cursor()
	sql="SELECT column_name,column_id FROM user_tab_columns WHERE Table_Name = '"+tablename+"'"
        print(sql)
	cur.execute(sql)
	rows=cur.fetchall()
	col={}
	for row in rows:
		col[row[0]]=row[1]
	cur.close()
	conn.close()
	return col
	
#extract fields_study and code,field_time change to hour
def data_processing(row,mpara):
 i=0
 msg=""
 key=""
 rlen=len(mpara['fields_study'])
 for i in range(rlen):
	 f=mpara['fields_study'][i]
	 if not fname.has_key(f):
		 print ("realtime detecting: "+tablename+" has no "+f)
		 return None
         key=row[fname[f]-1]
         if f==mpara['field_time']:
              t=time.strptime(key,'%Y-%m-%d %H:%M:%S')
              key=t.tm_hour
	 code=Encoder.value_to_code(f,str(key),Code_dict1)
	 i+=1
	 msg=msg+str(code)
	 if i<rlen:
		 msg=msg+","
 return msg

#dict to string
def dict_to_string(dict1):
 str1=""
 for key,value in dict1.items():
   str1=str1+key+":"+value+" "
 return str1

#detecting result :change code to value,save to oracle,return string
def result_save(msg,predval,abflag,mpara):
  dict1=Encoder.code_to_value(mpara['fields_study'],msg)
  print(dict1)
  #rss.save_to_oracle(mpara['result_tablename'],dict1,predval,abflag)
  Valstr=dict_to_string(dict1)
  return Valstr
  

def test():
	conn = cx_Oracle.connect(configureInfo.con_info)
	cur = conn.cursor()
	sql="SELECT * FROM  "+tablename+" where AGENT_ID='WD-WCASZ0627345'"
	cur.execute(sql)
	rows=cur.fetchone()
        if not rows:
         return None
        i=0
        msg=""
        rlen=len(rows)
	for row in rows:
		msg=msg+str(row)
		i+=1
		if i<rlen:
                 msg=msg+","
        cur.close()
        conn.close()
	return msg

s_predval=-1
w_predval=-1	
s_abflag=-1
w_abflag=-1
s_baseline_val=""		
	
if __name__=='__main__':
 fname=get_filedname_from_oracle(tablename)
 print(fname)
 flag=0   #flag==-1:ERROR flag=0:whole and signal flag=1:no whole model
 if not fname:
	 flag=-1
	 print("realtime detecting :"+tablename+" not exists")
 wmpara=getmpara.get_modelparameter_from_oracle(wbaseline,'all','whole')
 print(wmpara)
 if not wmpara:
         flag=1
	 print("realtime detecting:whole model not exists")
 if not fname.has_key(sbaseline) or not fname.has_key(wbaseline):
	 flag=-1
	 print("realtime decting:threr is no baseline field in detecting table")
 Code_dict1=Encoder.import_coding()
 dectdata=test() #from kafka
 print(dectdata)
 if dectdata:
  row=dectdata.split(",")
  wValstr=sValdict=""
  if flag==0:  
     wdata=data_processing(row,wmpara)          #get whole detecting data
     wValdict=result_save(wdata,w_predval,w_abflag,wmpara)
     print(wdata)
  s_baseline_val=row[fname[sbaseline]-1]
  smpara=getmpara.get_modelparameter_from_oracle(sbaseline,s_baseline_val,'signal')
  if smpara:
    sdata=data_processing(row,smpara)
    sValstr=result_save(sdata,s_predval,s_abflag,smpara)
    print(sdata)
  if not wValstr or not sValstr:
    rss.send_to_webclient(sValstr,s_predval,s_abflag,s_baseline_val,wValstr,w_predval,w_abflag)
 
          
    
           
