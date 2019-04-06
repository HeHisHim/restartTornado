"""
static_path
可以通过向tornado.web.Application类的构造函数传递一个名为static_path的参数告诉Tornado从文件系统的一个特定位置提供静态文件
"""

"""
StaticFileHandler
用 127.0.0.1/static/html/index.html 来访问页面不友好, 可以通过tornado.web.StaticFileHandler来自由映射静态文件与其访问路径url
tornado.web.StaticFileHandler是Tornado内置的类, 专门用来提供静态资源文件的handler
path: 用来指明提供静态文件的根路径, 并在此目录中寻找路由中用正则表达式提取的文件名
default_filename: 用来指定访问路由中未指明文件名时, 默认提供的文件
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

class InderHandler(RequestHandler):
    def get(self):
        self.write("OK")

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/api/index", InderHandler),
        (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "statics/html"), "default_filename": "index.html"}), # 未指明时默认提供index.html
    ], 
    debug = True,
    # 使用os.path.join(跨平台)连接当前目录和静态文件目录
    static_path = os.path.join(current_path, "statics"))

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()