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
        filename=row[0]+'.csv'
        print(filename)
        #filename="kddtrain.csv"
        ip,port='192.168.138.201',8888
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        i=0
        try:
            sock.connect((ip,port))
            time_now=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            print("start time:",time_now)
            #while True:
            with open("./datafiles/"+filename,'r') as rfile:
                reader=csv.reader(rfile)
                for row in reader:
                    data=modelname+"\t"+",".join(row[0:-1])
                    #data=",".join(row[0:-1])
                    sock.send(str(len(data))+"\t"+data)
                    i=i+1
                    if i >= 60000:
                        break
                    time.sleep(0.01)
                rfile.close()
                end_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                print("end time:",end_time)
                print("count:",i)

        finally:
            sock.close()
    
