"""
正则提取uri
tornado中对于路由映射也支持正则提取uri, 提取出来的参数会作为RequestHandler中对应请求方式的参数
若未定义名字, 则参数按顺序传递, 一般在参数比较少的时候使用
若定义了名字, 则参数按照参数名传递, 提取多值最好用命名方式
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError

define("port", default = 8000, type = int, help = "run server on the given port.")

class InderHandler(RequestHandler):
    def get(self):
        self.write("OK")

class SubjectCityHandler(RequestHandler):
    def get(self, subject, city):
        self.write("Subject: {}</br>City: {}".format(subject, city))

class SubjectDateHandler(RequestHandler):
    def get(self, date, subject):
        self.write("date: {}</br>subject: {}".format(date, subject))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler),
        (r"/sub-city/(.+)/([a-z]+)", SubjectCityHandler), # 未命名方式 http://localhost:8000/sub-city/tornado/shenzhen
        (r"/sub-date/(?P<subject>.+)/(?P<date>\d+)", SubjectDateHandler), # 命名方式 http://localhost:8000/sub-date/tornado/2019
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()