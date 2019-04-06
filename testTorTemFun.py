"""
自定义函数
在模板中还可以使用自己编写的函数, 只需要将函数名作为模板的参数传递即可, 就像其他变量一样
模板会调用自定义函数, 将返回结果渲染
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import os
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError, StaticFileHandler

define("port", default = 8000, type = int, help = "run server on the given port.")

# 计算总价格
def sum_of_price(prices):
    return sum(prices)

class IndexHandler(RequestHandler):
    def get(self):
        houses = [{"price": [111, 232]}, {"price": [11, 232]}, {"price": [111, 22]}]
        self.render("index.html", houses = houses, fun_sum_of_price = sum_of_price) # 像普通变量一样传参

class NewHandler(RequestHandler):
    def get(self):
        self.render("new.html", text = "")

    def post(self):
        text = self.get_argument("text", default = "")
        self.render("new.html", text = text)

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/new", NewHandler),
        (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html"), "default_filename": "index.html"}), # 未指明时默认提供index.html
    ], 
    debug = True,
    # autoescape = None, # 关闭全局自动转义
    static_path = os.path.join(current_path, "static"),
    template_path = os.path.join(current_path, "template"),)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()