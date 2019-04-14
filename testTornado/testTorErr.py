"""
send_error(self, status_code: int = 500, **kwargs: Any) -> None
抛出HTTP错误状态码status_code, 默认为500. kwargs为可变命名参数
使用send_error抛出错误后tornado会调用write_error()方法进行处理, 并返回给浏览器处理后的错误页面
该方法类似于raise抛出异常
"""

"""
write_error(self, status_code: int, **kwargs: Any) -> None
用来处理send_error抛出的错误信息并返回给浏览器错误信息页面
可以重写此方法来定制自己的错误显示页面
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError, url

define("port", default = 8000, type = int, help = "run server on the given port.")

class InderHandler(RequestHandler):
    def write_error(self, status_code, **kwargs):
        self.write("错误error</br>")

    def get(self):
        rep = "method: {}</br>".format(self.request.method)
        self.write(rep)
        # <html><title>404: Not Found</title><body>404: Not Found</body></html>
        # 抛出404错误内部调用了self.finish(), 再调用self.write()的时候会报错 -- Cannot write() after finish()
        self.send_error(404)
        # self.write("error_message")

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler),
    ], debug = True)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()