#orcle connectting info
con_info='system/123456@192.168.1.86/orcl'
# old_con_info='system/123456@192.168.138.1/orcl'

#realtime detecting
tablename="DL_TMSAPP_C0A80006_20170220"
signal_baseline="AGENT_ID"
whole_baseline="AGENT_ID"

#master websocket
master_IP='192.168.1.49'
master_port='3368'

#websocket
guardrealturl = 'http://'+master_IP+':'+master_port+'/guardlstm'
noguardrealturl = 'http://'+master_IP+':'+master_port+'/noguardlstm'
newmurl='http://'+master_IP+':'+master_port+'/newmodel'
changemodelurl='http://'+master_IP+':'+master_port+'/changemodel'
evaluaterealturl='http://'+master_IP+':'+master_port+'/evaluate'
#kafa
kafka_info='master:9092,slave1:9092,slave2:9092'

#table
tablename_dect='DL_TMSAPP_C0A80006'

#filelist
filelist_dir='/home/zwh/TensorFlowOnSpark/examples/websocket/GUARD/datafiles'
