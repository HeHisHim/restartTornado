import tornado.web
import tornado.ioloop
import tornado.options
import tornado.httpserver
from tornado.web import RequestHandler
from tornado.options import define, options
import config
import urls
import tormysql
from handlers.application_init import Application
define("port", type = int, default = 8000, help = "run server on the given port")

def main():
    options.logging = config.log_level
    options.log_file_prefix = config.log_file
    tornado.options.parse_command_line()
    app = Application()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()