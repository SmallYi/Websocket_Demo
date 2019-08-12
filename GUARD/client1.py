import socket
import time
import sys
import csv
import cx_Oracle
sys.path.append('..')
import configure_info as configureInfo
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
            filename=row[0]
	    ip,port='192.168.138.201',8888
	    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	    try:
	       sock.connect((ip,port))
	       i=0
	       with open("/model/"+mname+"/"+filename,'r') as rfile:
		   reader=csv.reader(rfile)
		   for row in reader:
                       data=modelname+"\t"+",".join(row[0:-1])
		       sock.send(str(len(data))+"\t"+data)
		       time.sleep(5)
	    finally:
		sock.close()
    
