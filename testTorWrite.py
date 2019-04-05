"""
关于tornado的输出write(chunk)
将chunk数据写到输出缓冲区, 可以在同一个处理方法中多次使用write
"""

"""
使用write写json数据
如果将字典数据用json.dumps序列化显示数据, 会采用Content-Type: text/html
如果直接显示字典数据, write会自动帮转换为json字符串, 采用Content-Type: application/json
"""

"""
手动编写header的key / value
使用set_header(self, name: str, value: _HeaderTypes)可以改写header数据
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
        student = {"name": "zhangsan", "age": 18, "gender": 1}
        self.write(json.dumps(student)) # Content-Type: text/html; charset=UTF-8
        # self.write(student) # Content-Type: application/json; charset=UTF-8


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler)
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()