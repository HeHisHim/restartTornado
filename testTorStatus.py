"""
set_status(self, status_code: int, reason: str = None) -> None
为响应设置状态码, 可以自定义
status_code: int类型状态码, 若reason为None, 则状态码必须HTTP标准状态码之一
reason: string类型描述, 自定义状态码时必须填写, 否则报错. 若status_code为标准状态码, 则自动填充
"""

"""
redirect(self, url: str, permanent: bool = False, status: int = None) -> None
告知浏览器跳转到目标url
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
    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("mykey", "myvalue") # 自定义headers

    def get(self):
        student = {"name": "zhangsan", "age": 18, "gender": 1}
        self.set_status(199) # 手动填写404, 但能正常响应, 只是状态码为404
        self.write(json.dumps(student))

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler)
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()