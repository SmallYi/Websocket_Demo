#encoding:utf-8
import cx_Oracle
import sys
import select
import Encoder
import csv
sys.path.append('..')
import configure_info as configureInfo
import results_save_send as sendweb
from kafkaClass import Kafka_producer

class Format_db:
  def __init__(self,modelpara_dict):
    self.modelpara_dict=modelpara_dict

  def get_tables(self):
    conn = cx_Oracle.connect(configureInfo.con_info)
    cur = conn.cursor()
    sql="select table_name from user_tables where table_name like '"+modelpara_dict['Name']+"'"
    cur.execute(sql) 
    rows=cur.fetchall()
    tables=[]
    for row in rows:
       tables.append(row[1])
    cur.close
    conn.close()
    return tables

  def Unit_hour(self):
    tables=get_tables()
    db_select=Format_db_select(tables,self.modelpara_dict)
    db_select.data_select()
    
class Format_csv:
   def __init__(self,modelpara_dict):
     self.modelpara_dict=modelpara_dict
     self.rowlength=0
   
   def code_Judge(self,row_one,lable_num):
     code_field=[0]       # label is at code_field[0]
     for i in range(len(row_one)):
        try:
           float(row_one[i])
        except: 
           if i>lable_num:
               code_field.append(i)
           elif i<lable_num:
               code_field.append(i+1)    
     return code_field
   
   def row_ValueToCode(self,row,row_length,code_field,lable_num,dict1,mname):
       row_code=[0]
       for i in range(row_length):
          if i==lable_num:
            row_code[0]=row[i]
          else:
            row_code.append(row[i])
       for j in range(row_length):
          if row_code[j] and j in code_field:
              row_code[j]=str(Encoder.value_to_code(j,row_code[j],dict1,mname))        
       return row_code

   def Unit_single(self):
       dict1={}
       dict1=Encoder.import_coding(self.modelpara_dict['Model_name'])
       mname=self.modelpara_dict['Model_name']
       rfile="./datafiles/"+self.modelpara_dict['Name']+'.'+self.modelpara_dict['Format']
       print(rfile)
       with open(rfile,'r') as rfile:
        with open("./datafiles/codefiles/"+mname+'_code.csv','w') as wfile:
          data_reader=csv.reader(rfile)
          data_writer=csv.writer(wfile)
          first=True
          row_length=0
          lable_num=int(self.modelpara_dict['Lable_field'])-1    #start from 0,but user's input starts from 1
          code_field=[]
          for row in data_reader:
            if first:
              code_field=self.code_Judge(row,lable_num)  # just judge first line to decide codefiled
              print("codelist",code_field)
              self.rowlength=len(row)
              first=False
            row_code=self.row_ValueToCode(row,self.rowlength,code_field,lable_num,dict1,mname)
            data_writer.writerow(row_code)
            #kafkaproducer.senddata(",".join(row_code))
       self.save_lable_db()     
   
   
   def save_lable_db(self):
      modelname=self.modelpara_dict['Model_name']
      conn = cx_Oracle.connect(configureInfo.con_info)
      cur = conn.cursor()
      sql="select MAX(code) from SIGNALFIELD_CODE where FIELD_name='0' AND model_name='"+modelname+"'"
      cur.execute(sql)
      row=cur.fetchone()
      lable_num=row[0]+1
      sql="update guard_parameter set LABLE_NUM="+str(lable_num)+",COLUMN_NUM="+str(self.rowlength)+" where model_name='"+modelname+"'"
      cur.execute(sql)
      conn.commit()
      cur.close()
      conn.close()
               
def getModelParameter_fromOracle(modelname):
  conn = cx_Oracle.connect(configureInfo.con_info)
  cur = conn.cursor()
  sql="select Description,Format,Name,Unit,Label_field,Date_field,model_name from guard_parameter where model_name='"+modelname+"'"
  cur.execute(sql) 
  row=cur.fetchone()
  modelparameter={}
  if row:
    modelparameter['Format']=row[1]
    modelparameter['Name']=row[2]
    modelparameter['Unit']=row[3]
    #modelparameter['Training_fields']=row[4]
    modelparameter['Lable_field']=row[4]
    modelparameter['Date_field']=row[5]
    modelparameter['Model_name']=row[6]
  cur.close()
  conn.close()
  return modelparameter

if __name__=='__main__':
  modelname=sys.argv[1]
  modelpara_dict=getModelParameter_fromOracle(modelname)
  print(modelpara_dict)
  if not modelpara_dict:
     clientdct={'type':'progress','data':-1,'description':'There is no parameter of this model in database'}
     sendweb.postresult_newmodel_to_server(clientdct)
     exit(-1)
  if(modelpara_dict['Format']=='db'):
      d=Format_db(modelpara_dict)
      d.Unit_hour()  
  elif(modelpara_dict['Format']=='csv'):
      c=Format_csv(modelpara_dict)
      c.Unit_single()
      clientdct={'type':'progress','data':30,'description':'Code finish'}
      print(clientdct)
      sendweb.postresult_newmodel_to_server(clientdct)                       
  else:
       clientdct={'type':'progress','data':-1,'description':'This system does not support '+modelpara_dict['Format']}
       sendweb.postresult_newmodel_to_server(clientdct)
       exit(-1)


