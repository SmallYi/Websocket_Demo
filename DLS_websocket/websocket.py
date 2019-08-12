#-*-coding:utf-8-*-
import tornado.web  
import tornado.websocket  
import tornado.httpserver  
import tornado.ioloop
import threading  
import time
import json
import commands
import thread
import os
import configure_info as configureInfo
from tornado.options import define, options
define("port", default=3368, help="run on the given port", type=int)


class FeatureExtraction_ProStatus(object):
    ''' 处理类 '''
    dealflag=False
    ftE_register=None

    def dealnow(self):
        return FeatureExtraction_ProStatus.dealflag

    def register(self,callbacker,ty):
        FeatureExtraction_ProStatus.ftE_register = callbacker
        FeatureExtraction_ProStatus.dealflag=True
        try:
          if ty=='filelist':
             thread.start_new_thread(self.GetFileList,("GetFileList_Thread",))
        except:
             errdct={'type':'FeatureExtraction','data':-1,'description':'Error:unable to start thread'}
             self.makelines(errdct)
             self.unregister(FeatureExtraction_ProStatus.ftE_register)
           
    def GetFileList(self,threadname):
        filelist=[]
        filelist_dir=configureInfo.filelist_dir
        for files in os.listdir(filelist_dir):
           file_path=os.path.join(filelist_dir,files)
           if os.path.isfile(file_path):
             filelist.append(files)
        senddata={'data':None,'type':'filelist','description':None}
        senddata['data']=filelist
        self.makelines(senddata)

    def unregister(self,callbacker):
        '''close realtime connection'''
        if FeatureExtraction_ProStatus.ftE_register==callbacker:            
             FeatureExtraction_ProStatus.ftE_register=None
             FeatureExtraction_ProStatus.dealflag=False

    def makelines(self, dct):
        ''' 处理接受的内容 '''
        self.trigger(dct)

    def trigger(self, msg):
        ''' 向被记录客户端发送最新内容 '''
        if FeatureExtraction_ProStatus.ftE_register:
             print(msg)
             FeatureExtraction_ProStatus.ftE_register.write_message(json.dumps(msg))

class RealtimeData_ProStatus(object):
    ''' 处理类 '''
    dealflag=False
    rtD_register=None

    def dealnow(self):
        return RealtimeData_ProStatus.dealflag

    def register(self,callbacker,ty):
        RealtimeData_ProStatus.rtD_register = callbacker
        RealtimeData_ProStatus.dealflag=True
        print("start")

    def unregister(self,callbacker):
        '''close realtime connection'''
        if RealtimeData_ProStatus.rtD_register==callbacker:            
             RealtimeData_ProStatus.rtD_register=None
             RealtimeData_ProStatus.dealflag=False

    def makelines(self, dct):
        ''' 处理接受的内容 '''
        self.trigger(dct)

    def trigger(self, msg):
        ''' 向被记录客户端发送最新内容 '''
        if RealtimeData_ProStatus.rtD_register:
             print(msg)
             RealtimeData_ProStatus.rtD_register.write_message(json.dumps(msg))

class NewModel_ProStatus(object):
    ''' 处理类 '''
    newM_register = None
    dealflag=False

    def dealnow(self):
      return NewModel_ProStatus.dealflag

    def register(self,cmd,callbacker,ty,modelname):
        ''' 记录客户端连接实例 '''
        NewModel_ProStatus.newM_register=callbacker
        NewModel_ProStatus.dealflag=True
        try:
           if cmd=="fpgrowth":
               print("fpgrowth"+ty+modelname)
               #thread.start_new_thread(self.FPstart_newmodel,("FPnewmodel_Thread",ty,modelname))
           elif cmd=="lstm": 
               if ty=='single' or ty=='all':
                  print("lstm"+ty+modelname)        
                  #thread.start_new_thread(self.LSTMstart_newmodel,("LSTMnewmodel_Thread",ty,modelname))
               elif ty=="guard":
                  thread.start_new_thread(self.GUARDstart_newmodel,("GUARDnewmodel_Thread",ty,modelname))        
        except:
             clientdct={'type':'progress','data':-1,'description':'Error:unable to start thread'}
             self.unregister(NewModel_ProStatus.newM_register,clientdct)
           
    def FPstart_newmodel(self,threadName,ty,modelname):
       (status,output)=commands.getstatusoutput('sh FPgrowth_newmodel.sh '+str(ty)+' '+modelname)
       rstr=str(status)
       print(output)
       clientdct={'type':'progress','data':100,'description':'new model done'}
       self.makelines(clientdct)
       self.unregister(NewModel_ProStatus.newM_register)
       
    def LSTMstart_newmodel(self,threadName,ty,modelname):
       (status,output)=commands.getstatusoutput('sh LSTM_newmodel.sh '+ty+' '+modelname)
       rstr=str(status)
       print(output)
       clientdct={'type':'progress','data':100,'description':'new model done'}
       self.makelines(clientdct)
       self.unregister(NewModel_ProStatus.newM_register)

    def GUARDstart_newmodel(self,threadName,ty,modelname):
       (status,output)=commands.getstatusoutput('sh GUARD_newmodel.sh '+ty+' '+modelname)
       rstr=str(status)
       print(output)
       clientdct={'type':'progress','data':100,'description':'new model done'}
       self.makelines(clientdct)
       self.unregister(NewModel_ProStatus.newM_register)

    def unregister(self,callbacker):
        ''' 删除客户端连接实例 '''
        if callbacker==NewModel_ProStatus.newM_register:                  
           NewModel_ProStatus.newM_register=None
           NewModel_ProStatus.dealflag=False  

    def makelines(self, dct):
        ''' 处理接受的内容 '''
        self.trigger(dct)

    def trigger(self, msg):
        ''' 向被记录客户端发送最新内容 '''
        print(msg)
        if NewModel_ProStatus.newM_register:
           NewModel_ProStatus.newM_register.write_message(json.dumps(msg))

class ChangeModel_ProStatus(object):
    dealflag=False
    cgM_register=None
    modelname_now=None

    def dealnow(self):
        return ChangeModel_ProStatus.dealflag

    def register(self,callbacker,ty,modelname):
        ChangeModel_ProStatus.cgM_register = callbacker
        ChangeModel_ProStatus.dealflag=True
        try:
           pfile=open('model/model_now.txt','r+')
           row=pfile.read()
           if row:
               modelname_now=row
           if modelname_now==modelname:
               clientdct={'type':'other','data':-1,'description':modelname+' is now being processed!'}
               self.makelines(clientdct)
               
           else:
                mkdir('stop.txt')
                pfile.truncate()
                
        except:
           clientdct={'type':'other','data':-1,'description':'stop file exists or model_now file not exists!'}
           self.makelines(clientdct)
   
    def unregister(self,callbacker):
        ''' 删除客户端连接实例 '''
        if callbacker==ChangeModel_ProStatus.cgM_register:                  
           ChangeModel_ProStatus.cgM_register=None
           ChangeModel_ProStatus.dealflag=False  

    def makelines(self, dct):
        ''' 处理接受的内容 '''
        self.trigger(dct)

    def trigger(self, msg):
        ''' 向被记录客户端发送最新内容 '''
        print(msg)
        if ChangeModel_ProStatus.cgM_register:
           ChangeModel_ProStatus.cgM_register.write_message(json.dumps(msg))
    
    
class WebSocketHandler(tornado.websocket.WebSocketHandler):   
    ''' 接受websocket链接，保存链接实例 '''
    def check_origin(self, origin):     #针对websocket处理类重写同源检查的方法
        return True

    def open(self):
        clientdct={'type':'other','data':0,'description':'connect success!'}
        self.write_message(json.dumps(clientdct))

    def on_close(self):      
       self.application.rtD.unregister(self)  #删除客户端连接
       self.application.newM.unregister(self)
       self.application.cgM.unregister(self)
       self.close()
       print(str(self)+' close')
    
    def judge_deal(self,cmd):
       flag=False
       if not self.application.newM.dealnow() and not self.application.cgM.dealnow() and not self.application.rtD.dealnow():
            flag=True
       if self.application.rtD.dealnow() and cmd=='change':
            flag=True
       print(self.application.newM.dealnow(),self.application.cgM.dealnow(),self.application.rtD.dealnow())
       return flag

 
    def on_message(self, message):       
       msg=json.loads(message)
       print(msg)
       if msg:
          cmd=msg['algorithm']
          ty=msg['type']
          modelname=msg['model_name']
          if self.judge_deal(cmd):
              if cmd=='start':
                   self.application.rtD.register(self,ty)
              elif cmd=='change':
                   self.application.cgM.register(self,ty,modelname)
              elif cmd=='pca': #feature extraction
                   self.application.ftE.register(self,ty)           
              else:
                   self.application.newM.register(cmd,self,ty,modelname)
          else:
              clientdct={'type':'other','data':0,'description':'Model is being processed!'}
              self.write_message(json.dumps(clientdct))



class ReceiveGuardLSTMHandler(tornado.web.RequestHandler):
    ''' 接受服务器端脚本提交的最新lstm_guard realtime行内容 '''
    label_five=['normal.']
    def post(self, *args, **kwargs):
        data = self.get_argument('dict', '').encode(encoding='UTF8')       
        if data:
           data_dict=json.loads(data)
           label=data_dict['data']['output']
           if len(ReceiveGuardLSTMHandler.label_five)<5 and label not in ReceiveGuardLSTMHandler.label_five:
               ReceiveGuardLSTMHandler.label_five.append(label)
           if label in ReceiveGuardLSTMHandler.label_five:          
               data_dict['data']['number']=ReceiveGuardLSTMHandler.label_five.index(label)
           else:
               data_dict['data']['number']=-1          
           print(data_dict)
           self.application.rtD.makelines(data_dict)



class ReceiveNoGuardLSTMHandler(tornado.web.RequestHandler):
    ''' 接受服务器端脚本提交的最新lstm_noguard realtime行内容 '''
    def post(self, *args, **kwargs):
        data = self.get_argument('dict', '').encode(encoding='UTF8')
        if data:
           data_dict=json.loads(data)
           #print(data_dict)
           self.application.rtD.makelines(data_dict)
 


       
class ReceiveNewModelHandler(tornado.web.RequestHandler):
    ''' 接受服务器端脚本提交的最新newModel行内容 '''
    def post(self, *args, **kwargs):
        data = self.get_argument('dict', '').encode(encoding='UTF8')
        if data:
           print(data)
           self.application.newM.makelines(json.loads(data))



class ChangeModelHandler(tornado.web.RequestHandler):
    ''' 接受服务器端脚本提交的最新changeModel行内容 '''
    def post(self, *args, **kwargs):
        data = self.get_argument('dict', '').encode(encoding='UTF8')
        if data and json.loads(data)=='stop':
           print(data)
           callbacker=ChangeModel_ProStatus.cgM_register
           self.application.cgM.unregister(self,callbacker)
           self.application.rtD.register(self,'guard')
           thread.start_new_thread(self.LSTMstart_realtime_guard,("GUARDrealtime_Thread",ty,modelname)) 

    def LSTMstart_realtime_guard(self,threadName,ty,modelname):
       (status,output)=commands.getstatusoutput('sh GUARD_realtime.sh '+str(ty)+' '+modelname)
       rstr=str(status)
       print(output)
       clientdct={'type':'progress','data':0,'description':'stop'}
       self.application.cgM.makelines(clientdct)
       self.application.cgM.unregister(NewModel_ProStatus.newM_register)
    
           
           
class Application(tornado.web.Application):  
    def __init__(self):
        self.cmd=None
        self.rtD=RealtimeData_ProStatus() 
        self.newM=NewModel_ProStatus()
        self.cgM=ChangeModel_ProStatus()
        self.ftE=FeatureExtraction_ProStatus()
        handlers = [
		(r'/ws', WebSocketHandler),
		(r'/guardlstm', ReceiveGuardLSTMHandler),
                (r'/noguardlstm', ReceiveNoGuardLSTMHandler),
                (r'/newmodel', ReceiveNewModelHandler),
                (r'/changemodel', ChangeModelHandler),
		]  
        settings = { "template_path": "."}  
        tornado.web.Application.__init__(self, handlers, **settings)



if __name__ == '__main__':  
    ws_app = Application()  
    server = tornado.httpserver.HTTPServer(ws_app)  
    server.listen(options.port)  
    tornado.ioloop.IOLoop.instance().start() 
