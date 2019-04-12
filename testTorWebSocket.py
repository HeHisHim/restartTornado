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

class ChatHandler(WebSocketHandler):
    users = []
    def open(self):
        for user in self.users:
            user.write_message("%s上线了" % self.request.remote_ip)
        self.users.append(self)

    def on_message(self, message):
        for user in self.users:
            print("user: ", user)
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
