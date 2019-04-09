import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import tormysql
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

        self.db = pymysql.connect("127.0.0.1", "root", "1231230", "itcast")
        self.cursor = self.db.cursor()

class IndexHandler(RequestHandler):
    def get(self):
        rep = self.application.cursor.execute("select ui_name from it_user_info where ui_user_id = 1")
        data = self.application.cursor.fetchone()
        print(data)
        self.write(data[0])

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
