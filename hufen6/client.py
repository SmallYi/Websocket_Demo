import websocket
import json
from multiprocessing.dummy import Pool
import time
import threading



pool = Pool(500)
count = 0


def on_message(ws, message):
    # print(message)
    # data = "aa"*99999
    # time.sleep(1)
    ws.send("B")

def on_error(ws, error):
    print(ws.id,error)
def on_close(ws):
    print(ws.id,"### closed ###")
def on_open(ws):
    data = "aa"*99999
    ws.send(json.dumps({"action": "init", "secretkey": "161314571%s"%data}))

def start(id,):
    ws = websocket.WebSocketApp("ws://127.0.0.1:8081/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.id = id
    ws.on_open = on_open
    ws.run_forever()




websocket.enableTrace(False)
for i in range(0,pool._processes):
    pool.apply_async(
        start,args=(i,)
    )

pool.close()
pool.join()

