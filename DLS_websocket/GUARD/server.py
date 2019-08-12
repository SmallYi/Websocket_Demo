import SocketServer
import time
from kafkaClass import Kafka_producer

class Server(SocketServer.BaseRequestHandler):
    def handle(self):
        conn=self.request
        print(conn)
        kafkaproducer=Kafka_producer('master:9092,slave1:9092,slave2:9092','HelloKafka')
        error_flag=0
        data_r=''
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
                print(list1[1][0:row_l])
                kafkaproducer.senddata(list1[1][0:row_l])
                data=list1[1][row_l:]
            if error_flag:
                break
        conn.close()


if __name__=='__main__':
    ip,port='192.168.138.201',8888
    server=SocketServer.ThreadingTCPServer((ip,port),Server)
    server.serve_forever()
    
    
