"""
WebSocket
websocket是HTML5规范中新提出的客户端-服务器通讯协议, 协议本身使用新的ws://URL格式
websocket是独立的, 创建在TCP上的协议(即传输层). 和HTTP唯一关联是使用HTTP协议的101状态码进行协议切换, 使用TCP端口是80, 可以用于绕过大多数防火墙的限制
websocket使得客户端和服务器之间的数据交换变得更加简单, 允许服务端直接向客户端推送数据而不需要客户端进行请求, 两者之间可以创建持久性的连接, 并允许数据进行双向传送
"""

"""
Tornado的websocket模块
Tornado提供支持websocket的模块是tornado.websocket, 其中提供了一个WebSocketHandler类来处理通讯, 继承此类来处理websocket

WebSocketHandler.open()
当一个WebSocket连接建立后被调用

WebSocketHandler.on_message(message)
当客户端发送消息message过来时被调用, 该方法必须被重写

WebSocketHandler.on_close()
当WebSocket连接关闭后被调用

WebSocketHandler.write_message(message, binary = False)
向客户读发送消息message, message可以是字符串或字典(字典会转为json字符串)
若binary为False, 则message以utf8编码发送
若binary为True, 则可发送任何字节码

WebSocketHandler.close()
关闭WebSocket连接

WebSocketHandler.check_origin(origin)
判断源origin, 对于符合条件(即返回True)的请求源origin允许其连接, 否则返回403
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import os
import pymysql
import asyncio
import time
import uuid, base64
from tornado.options import options, define
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, MissingArgumentError, StaticFileHandler
from tornado.websocket import WebSocketHandler

define("port", default = 8000, type = int, help = "run server on the given port.")

class Application(tornado.web.Application):
    def __init__(self):
        handles = [
            (r"/", IndexHandler),
            (r"/chat", ChatHandler),
            (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html")}),
        ]
        settings = dict(
            debug = True,
            static_path = os.path.join(current_path, "static"),
            template_path = os.path.join(current_path, "template"),
            login_url = "/login", # 当用户验证失败时, 将用户重定向到该url上
            cookie_secret = "p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=",  # 配置密钥
            xsrf_cookies = True,
        )
        tornado.web.Application.__init__(self, handlers = handles, **settings)

class ChatHandler(WebSocketHandler): # 要使用websocket需继承tornado.websocket.WebSocketHandler
    users = [] # 类属性, 记录所有连接
    def open(self):
        for user in self.users:
            user.write_message("%s上线了" % self.request.remote_ip)
        self.users.append(self)

    def on_message(self, message):
        for user in self.users:
            if not user == self:
                user.write_message("%s say: %s" % (self.request.remote_ip, message))

    def on_close(self):
        self.users.remove(self)
        for user in self.users:
            user.write_message("%s下线了" % self.request.remote_ip)

class IndexHandler(RequestHandler):
    def get(self):
        self.render("webSocketDemo.html")

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()

    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
