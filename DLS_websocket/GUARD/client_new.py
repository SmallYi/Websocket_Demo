import socket
import time
import sys
import csv
sys.path.append('..')
import configure_info as configureInfo

if __name__=='__main__':
    ip,port='192.168.138.201',8889
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        sock.connect((ip,port))
        while True:
            with open("./datafiles/evafiles/c.csv",'r') as rfile:
                reader=csv.reader(rfile)
                for row in reader:
                    if row[0] == 'i0':
                        pass
                    else:
                        data=",".join(row)
                        sock.send(str(len(data))+"\t"+data)
                        time.sleep(2)
                rfile.close()
    finally:
        sock.close()


    
