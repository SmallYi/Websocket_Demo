#encoding:utf-8
import cx_Oracle
import time
import csv
import sys
sys.path.append('..')
import configure_info as configureInfo

#val[0]--code val[1]--field_name
def import_coding(model_name):
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur = conn.cursor()
    sql="select key,code,field_name from Signalfield_code where model_name='"+model_name+"'"
    cur.execute(sql)
    rows=cur.fetchall()
    dict1={}
    for row in rows:
        key=row[0]+"\t"+row[2]
        val=row[1]
        dict1[key]=val
    cur.close()
    conn.close()
    return dict1

def import_key(model_name):
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur = conn.cursor()
    sql="select key,code,field_name from Signalfield_code where model_name='"+model_name+"'"
    cur.execute(sql)
    rows=cur.fetchall()
    dict1={}
    for row in rows:
        key=str(row[1])+"\t"+row[2]
        val=row[0]
        dict1[key]=val
    cur.close()
    conn.close()
    return dict1	

def Add_coding(dict1,field_name,key,value_code):
	dict1[key+"\t"+field_name]=value_code
	conn = cx_Oracle.connect(configureInfo.con_info)
	cur = conn.cursor()
	sql="insert into Signalfield_code values('"+key+"',"+str(value_code)+",'"+field_name+"')"
	print(sql)
	cur.execute(sql)
	conn.commit()
	cur.close()
	conn.close()
	

def value_to_code(field,key,dict1,model_name):
  if field == 'ACT_TIME':
     key=key.replace(":","")
     return int(key)
  r=1
  rkey=key+"\t"+str(field)
  if dict1.has_key(rkey):
     r=dict1[rkey]
  else:
     conn = cx_Oracle.connect(configureInfo.con_info)
     cur = conn.cursor()
     sql="select max(code) from Signalfield_code where model_name='"+model_name+"' and field_name='"+str(field)+"'" 
     print(sql)
     cur.execute(sql)
     rows=cur.fetchone()  
     if rows[0]==None:
        r=1
     else:
        r=rows[0]+1
     dict1[key+"\t"+str(field)]=r
     sql="insert into Signalfield_code values('"+key+"',"+str(r)+",'"+str(field)+"','"+model_name+"')"
     print(sql)
     cur.execute(sql)
     conn.commit()
     cur.close()
     conn.close()
  return r

def code_to_value(field,code,dict1):
  r=""  
  rcode=str(code)+"\t"+str(field)
  if dict1.has_key(rcode):
      r=r+dict1[rcode]
  else:
      print("The massage does not encode!") 
  return r



	
     
