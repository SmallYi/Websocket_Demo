import tornado.websocket
import tornado.web
import tornado.httpserver
import tornado.ioloop
import json
import time
import redis
import threading
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor



redisconn = redis.Redis(host="127.0.0.1", port=6379)


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    executor = ThreadPoolExecutor(500)

    def check_origin(self, origin):
        return True

    def open(self):
        self.status_close = False
        pass

    i= 0
    @run_on_executor
    def on_message(self, message):
        self.write_message(
          "b"
        )
        print(1)
        return
        print(self.i,len(message))
        self.i+=1
        obj = json.loads(message)
        action = obj["action"]


        getattr(self, "event_%s" % action)(obj)



    def event_init(self, obj):
        # 1，分享抽奖
        # 2，名称抽奖
        # 3，评论抽奖
        # 4，礼物抽奖
        self.write_message(
            {"users": "", "count": "", "action": "newuser"}
        )
        return



        userid = obj["secretkey"]

        # get_live_message.apply_async(args=(userid,))
        sub = redisconn.pubsub()
        topics = ['message:%s:list:comment' % userid]
        sub.subscribe(topics)
        t = time.time()
        messages = []
        users = set()

        self.write_message(
            json.dumps(
                {
                    "action": "init",
                    "status": 1,
                    "msg": "初始化成功"
                }
            ))

        for i in range(0,pool._processes):
            pool.apply_async(
                www, args=(
                    self,
                ),
            )
        pool.close()
        pool.join()




        while not self.status_close:

            data = sub.get_message(True, 1)
            if data:
                obj = json.loads(data["data"].decode())

                users.add(
                    obj["userinfo"]["userid"]
                )
                messages.append(
                    obj
                )

            if self.status_close:
                break
            if len(messages) >= 50 or time.time() - t > 0.5:
                t = time.time()
                if self.status_close:
                    break

                try:
                    self.write_message(
                        {"users": messages, "count": len(users), "action": "newuser"}
                    )
                except Exception as e:
                    print(e)
                messages = []

        print("结束")


    def on_close(self):
        self.status_close = True


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/ws', WebSocketHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


from multiprocessing.dummy import Pool
import threading
lock = threading.Lock()
pool = Pool(10)
def www(sock):
    while True:
        lock.acquire()
        sock.write_message(
            json.dumps(
                {
                    "action": "cscs",
                    "status": 1,
                    "msg": "多线程测试"
                }
            ))
        lock.release()




if __name__ == '__main__':
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8081)
    tornado.ioloop.IOLoop.instance().start()
