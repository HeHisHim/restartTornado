"""
数据库连接初始化
tornado需要在应用启动时创建一个数据库连接实例, 供各个RequestHandler使用
可以在构造Application的时候创建一个数据库实例, 并设置成Application的属性
而RequestHandler可以通过self.application获取其属性, 进而操作数据库实例
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import pymysql
import os
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError, StaticFileHandler

define("port", default = 8000, type = int, help = "run server on the given port.")

class Application(tornado.web.Application):
    def __init__(self):
        handles = [
            (r"/", IndexHandler),
            (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html"), "default_filename": "index.html"}), # 未指明时默认提供index.html
        ]
        settings = dict(
            debug = True,
            static_path = os.path.join(current_path, "static"),
            template_path = os.path.join(current_path, "template"),
        )
        tornado.web.Application.__init__(self, handlers = handles, **settings)
        # 创建一个全局的mysql连接供Handler调用
        self.db = pymysql.connect("127.0.0.1", "root", "1231230", "itcast")

class IndexHandler(RequestHandler):
    def get(self):
        self.fetchData()

    def fetchData(self):
        with self.application.db.cursor() as cursor:
            data = cursor.execute("update it_house_info set hi_user_id = %s where hi_house_id = %s", args = [9, 30])
            self.write(str(data))
            self.application.db.commit()

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()
    # 以下改用类来封装
    # app = tornado.web.Application([
    #     (r"/", IndexHandler),
    #     (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html"), "default_filename": "index.html"}), # 未指明时默认提供index.html
    # ], 
    # debug = True,
    # static_path = os.path.join(current_path, "static"),
    # template_path = os.path.join(current_path, "template"),)
    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
