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
        (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "statics/html"), "default_filename": "index.html"}),
    ], 
    debug = True, 
    static_path = os.path.join(current_path, "statics"))

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()