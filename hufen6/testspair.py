import websocket
import time
import threading
import requests
import json
import logging
from multiprocessing.dummy import Pool


import os
import sys

sys.path.append("/home/ksht/") #windows环境不用管 linux是应用的路径
os.environ['DJANGO_SETTINGS_MODULE'] = 'ksht.settings'  # 项目的settings
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from ksuser.models import User
from hufen.models import HufenHistory
from django.contrib.sessions.models import Session







import random
from django.utils import timezone
global c #产生随机数1-100
global pdo #确定正常概率0-100
global pno #确定取消概率
global pover #操作超时概率
global pre #重新确认概率
heart = dict() # userid:ws
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')


host = "127.0.0.1:8081"
pool = Pool(100)

def on_message(ws, message):
    global c
    global pdo
    global pno
    global pover
    global pre

    time.sleep(1.5)

    message = json.loads(message)

    if "action" in message:
        action = message["action"]
        if action == "prepos":
            heart[ws.userid] = ws
            ws.send(json.dumps({"action": "pair"}))
            print(ws.userid, "发送匹配请求")


        elif action == "CheckAlive":
            print(ws.userid,time.time(),'CheckAlive')
            c = random.randint(1, 100)
            if c <= pdo:

                ws.send(json.dumps({"action": "IsAlive"}))
                print(ws.userid, time.time(),'IsAlive end')
                print("用户%s在线"%(ws.userid))
            elif pdo < c < pno:
                ws.send(json.dumps({"action": "IsAlive"}))
                print(ws.userid, time.time(),'IsAlive end')
                print("用户%s在线" % (ws.userid))
                ws.close()
                print("断开连接")
                return
            elif c > pno:
                ws.close()
                print("断开连接")
                return


        elif action == "needcost":
            print("用户%s在线积分不足" % (ws.userid))
        elif action == "pair":
            print(ws.userid, time.time(), 'pair')
            print(str(ws.userid) + "与" + message["username"] + '匹配成功: 互粉总次数:' + \
                  str(message['totaltime']) + ' 互粉成功率:' + str(100 * message['sucrate']) + '%')
            c = random.randint(1,100)

            if c <= pdo:
                ws.send(json.dumps({"action": "dopair"}))
                print(str(ws.userid) + "确认互粉")
            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "change"}))
                print(str(ws.userid) + "换个老铁")
            elif pno < c <= pover:
                ws.send(json.dumps({"action": "CancelPairSecond"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return
            print(ws.userid, time.time(), 'dopair end')


        elif action == 'dopairfirst':
            print("%s低信誉值用户先关注%s" % (ws.userid, message["userid"]))

            c = random.randint(1,100)
            if c <= pdo:
                ws.send(json.dumps({"action": "ConfirmPairFirst"}))
                print(str(ws.userid) + "去关注TA")
            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "NoConfirmPairFirst","state":"deny"}))
                print(str(ws.userid) + "不关注TA")
            elif pno < c <= pover:
                ws.send(json.dumps({"action": "NoConfirmPairFirst","state": "cancel"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == 'doconfirmfirst':
            print("%s低信誉值用户选择是否已经关注匹配用户" % (ws.userid))
            c = random.randint(1,100)
            if c <= pdo:
                ws.send(json.dumps({"action": "ConfirmFocusFirst"}))
                print(str(ws.userid) + "已经关注")
            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "NoConfirmFocusFirst","state": "deny"}))
                print(str(ws.userid) + "没有关注")
            elif pno < c <= pover:
                ws.send(json.dumps({"action": "NoConfirmFocusFirst","state": "cancel"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == 'checkfocusfirst':
            print("%s高信誉值用户选择是否去快手确认对方%s是否关注" % (ws.userid,message['userid']))
            # c = random.randint(1,2)
            if c <= pdo:
                ws.send(json.dumps({"action": "CheckFocusFirst"}))
                print(str(ws.userid) + "去快手粉丝列表确认")
            elif pdo < c <= pover:
                ws.send(json.dumps({"action": "NoCheckFocusFirst"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == 'doconfirmpre':
            print("%s高信誉值用户选择对方是否已经关注自己" % (ws.userid))
            c = random.randint(1,100)
            if c <= pdo:
                ws.send(json.dumps({"action": "ConfirmFocusPre"}))
                print(str(ws.userid) + "已经关注")

            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "NoConfirmFocusPre","state": "deny"}))
                print(str(ws.userid) + "没有关注")
            elif pno < c <= pre:
                ws.send(json.dumps({"action": "ReCheckFocusFirst"}))
                print(str(ws.userid) + "重新确认")
            elif pre < c <= pover:
                ws.send(json.dumps({"action": "NoConfirmFocusPre","state": "cancel"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == 'doconfirmsecond':
            print("%s高信誉值用户选择是否去快手关注对方%s" % (ws.userid,message['userid']))
            c = random.randint(1,100)
            if c <= pdo:
                ws.send(json.dumps({"action": "ConfirmFocusSecond"}))
                print(str(ws.userid) + "去关注TA")
            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "NoConfirmFocusSecond","state": "deny"}))
                print(str(ws.userid) + "不关注TA")
            elif pno < c <= pover:
                ws.send(json.dumps({"action": "NoConfirmFocusSecond","state": "cancel"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == 'dofocussecond':
            print("%s高信誉值用户选择是否已经关注对方" % (ws.userid))
            c = random.randint(1,100)
            if c <= pdo:
                ws.send(json.dumps({"action": "ConfirmSuccessFirst"}))
                print(str(ws.userid) + "已经关注")
            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "NoConfirmSuccessFirst","state": "deny"}))
                print(str(ws.userid) + "没有关注")
            elif pno < c <= pover:
                ws.send(json.dumps({"action": "NoConfirmSuccessFirst","state": "cancel"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == 'checkfocussecond':
            print("%s低信誉值用户选择是否去快手确认对方%s是否关注" % (ws.userid,message['userid']))
            # c = random.randint(1,2)
            if c <= pdo:
                ws.send(json.dumps({"action": "CheckFocusSecond"}))
                print(str(ws.userid) + "去快手粉丝列表确认")
            elif pdo < c <= pover:
                ws.send(json.dumps({"action": "NoCheckFocusSecond"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return


        elif action == 'doconfirmfin':
            print("%s低信誉值用户选择对方是否已经关注自己" % (ws.userid))
            c = random.randint(1,100)
            if c <= pdo:
                ws.send(json.dumps({"action": "ConfirmSuccessSecond"}))
                print(str(ws.userid) + "已经关注")

            elif pdo < c <= pno:
                ws.send(json.dumps({"action": "NoConfirmSuccessSecond","state": "deny"}))
                print(str(ws.userid) + "没有关注")
            elif pno < c <= pre:
                ws.send(json.dumps({"action": "ReCheckFocusSecond"}))
                print(str(ws.userid) + "重新确认")

            elif pre < c <= pover:
                ws.send(json.dumps({"action": "NoConfirmSuccessSecond","state": "cancel"}))
                print(str(ws.userid) + "右上角关闭")
                ws.close()
                print("断开连接")
                return

        elif action == "dopairsuccess":
            print("%s与%s互粉成功" % (ws.userid,message['userid']))
            ws.close()
            print("断开连接")
            return

        elif action == 'dofocusfirst':
            print("%s低信誉值用户等待对方确认与关注" % (ws.userid))
            state = message["state"]
            if state == 'makeconfirm':
                print(str(ws.userid) + "对方正在确认您是否已经关注TA，请稍等...")
            elif state == 'makefocus':
                print(str(ws.userid) + "对方已确认您关注了TA，请稍等...")
            elif state == 'dofocus':
                print(str(ws.userid) + "对方正在关注您，请稍等...")
            elif state == 'remakeconfirm':
                print(str(ws.userid) + "对方正在重新确认您是否已经关注TA，请稍等...")


        elif action == 'dopairsecond':
            print("%s高信誉值用户等待对方确认与关注" % (ws.userid))
            state = message["state"]
            if state == 'wait':
                print(str(ws.userid) + "对方正在关注您，请稍等...")
            elif state == 'makeconfirm':
                print(str(ws.userid) + "对方正在确认您是否已经关注TA，请稍等...")
            elif state == 'remakeconfirm':
                print(str(ws.userid) + "对方正在重新确认您是否已经关注TA，请稍等...")

        elif action == 'errorpair':
            state = message["state"]
            if state == 'change':
                print(str(ws.userid) + "对方选择了换一个人，互粉结束")
            elif state == 'cancelpair':
                print(str(ws.userid) + "对方取消了本次互粉，互粉结束")
            elif state == 'ErrorDU_0':
                print(str(ws.userid) + "对方取消了去确认您是否关注，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorDU_1_1':
                print(str(ws.userid) + "对方取消去关注您，互粉结束")
            elif state == 'ErrorDU_1_2':
                print(str(ws.userid) + "对方拒绝去关注您，互粉结束")
            elif state == 'ErrorDU_2_1':
                print(str(ws.userid) + "对方取消确认是否已经关注您，互粉结束")
            elif state == 'ErrorDU_2_2':
                print(str(ws.userid) + "对方选择没有关注您，互粉结束")
            elif state == 'ErrorDU_3_1':
                print(str(ws.userid) + "对方确认之后没有选择您是否关注了TA，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorGU_1_1':
                print(str(ws.userid) + "对方确认之后没有选择您是否关注了TA，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorDU_3_2':
                print(str(ws.userid) + "对方确认之后反映您没有关注TA，互粉结束，若您已关注对方请取关" + str(message['otherid']))
            elif state == 'ErrorGU_1_2':
                print(str(ws.userid) + "对方确认之后反映您没有关注TA，互粉结束，若您已关注对方请取关" + str(message['otherid']))
            elif state == 'ErrorGU_0':
                print(str(ws.userid) + "对方取消了去确认您是否关注，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorGU_2_1':
                print(str(ws.userid) + "对方取消去关注您，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorGU_2_2':
                print(str(ws.userid) + "对方拒绝去关注您，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorGU_3_1':
                print(str(ws.userid) + "对方取消确认是否已经关注您，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'ErrorGU_3_2':
                print(str(ws.userid) + "对方选择没有关注您，互粉结束，请取关对方" + str(message['otherid']))
            elif state == 'workovertime':
                print(str(ws.userid) + "互粉操作超时，互粉结束，若您已关注对方请取关对方" + str(message['otherid']))
            elif state == 'waitovertime':
                print(str(ws.userid) + "等待服务器响应超时，互粉结束，若您已关注对方请取关对方" + str(message['otherid']))
            elif state == 'ErrBeforeFocus':
                print(str(ws.userid) + "对方终止了本次互粉，互粉结束")
            elif state == 'ErrAfterFocus':
                print(str(ws.userid) + "对方终止了本次互粉，互粉结束，请取关对方" + str(message['otherid']))
            ws.close()
            print("断开连接")
            return

        elif action == 'rechecktime':
            print("%s互粉仍在进行，请稍等..." % (ws.userid))

        elif action == 'repairtime':
            print("%s匹配仍在进行，请稍等..." % (ws.userid))

        elif action == 'close':
            print("%s您的账号已在其他地方登录，您被强制下线！" % (ws.userid))

    elif 'error' in message:
        error = message['error']
        if error == "nopair":
            print("%s没有找到合适用户，匹配结束"%(ws.userid))

        elif error == "server":
            print("%s服务器异常，本次互粉结束"%(ws.userid))

        elif error == "initerror":
            print("%s初始化错误" % (ws.userid))
        ws.close()
        print("断开连接")
        return

    elif 'heart' in message:
        pass

    else:
        print(ws.userid, message)

def on_error(ws, error):
    global heart
    if ws.userid in heart:
        del heart[ws.userid]
    print(ws.userid,"error",error)

def on_close(ws):
    global heart
    if ws.userid in heart:
        del heart[ws.userid]
    print(ws.userid,"### closed ###")

def on_open(ws):

    sessionid = userid2sessionid(ws.userid)
    print(ws.userid, "init")
    ws.send(json.dumps({"action": "init", "sessionid": sessionid}))

    # print(ws.userid,"init")
    # ws.send(json.dumps({"action": "init", "uid": ws.userid}))







# def userid2cookies(userid):
#     result =  requests.post("http://"+host+"/hall",{"userid":userid},)
#     return result.headers["Set-Cookie"]


def hufen(userid):
    # cookies = userid2cookies(userid)
    # print(websocket.getdefaulttimeout())
    ws = websocket.WebSocketApp("ws://%s/ws" % host,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                # cookie=cookies

                                )

    # ws.send()
    ws.userid = userid


    ws.on_open = on_open
    ws.run_forever()




def userid2sessionid(id):
    result =  requests.post("http://127.0.0.1/hufen/getsessionid", {"id": id})
    return result.json()["sessionid"]

def session2user(sessionid):
    sessionobj = Session.objects.get(session_key=sessionid)
    userobj = User.objects.get(id=sessionobj.get_decoded()["_auth_user_id"])
    return userobj

import requests

class Heart(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.HeartCheck()

    def HeartCheck(self):
        global heart
        while True:
            lis = list(heart.keys())
            for user in lis:
                if heart[user].sock:
                    heart[user].send(json.dumps({"action": "HeartBeat"}))
            lis.clear()
            time.sleep(10)

if __name__ == "__main__":


    # for i in range(0, 2000):
    #     if not User.objects.filter(userid=i).exists():
    #         User.objects.create(userid=i, username=str(i), credit=100, integral=200)
    # print("creat down")
    # exit()
    #
    # result = HufenHistory.objects.all().delete()
    # print("delete down")
    # exit()
    global c
    global pdo
    global pno
    global pover
    # 设置确定率 否定率 取消率 超时率
    pdo = 101 # 确定率90%
    pno = 95 # 否定率5%
    pre = 97 # 重新确认 2%
    pover = 99 # 取消率2% 超时率1%
    websocket.enableTrace(True)
    thread_heart = Heart()
    thread_heart.start()
    results = []
    # 随机
    while True:
        for userid in range(0, 1):
            uid = random.randint(0, 2000)
            results.append(
                pool.apply_async(
                    hufen,
                    (uid,)

                )
            )
        # 固定
        for result in results:
            result.get()
    exit()

    # for userid in range(1,2):
    #     results.append(
    #         pool.apply_async(
    #             hufen,
    #             (userid+1,)
    #         )
    #     )
    # for result in results:
    #     result.get()
    # exit()
    # for userid in range(1,1001):
    #     results.append(
    #         pool.apply_async(
    #             hufen,
    #             (userid+1,)
    #         )
    #     )
    # for result in results:
    #     result.get()
    # for userid in range(1,1001):
    #     results.append(
    #         pool.apply_async(
    #             hufen,
    #             (userid+1,)
    #         )
    #     )
    # for result in results:
    #     result.get()
    # #
    #
    #


#
#

# def testerror():
#
#     a = b / 0
#     return
