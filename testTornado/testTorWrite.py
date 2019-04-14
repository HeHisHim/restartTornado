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

"""
add_header(self, name: str, value: _HeaderTypes) -> None
add_header与set_header的区别

set_header会执行覆盖操作
self._headers[name] = self._convert_header_value(value)

add_header会执行添加操作, 不做覆盖
self._headers.add(name, self._convert_header_value(value))
"""

"""
关于set_default_headers
该方法会在进入HTTP处理方法前先被调用来设置headers的默认值, 可重写该方法来预先设置默认的headers
注意: 在HTTP处理方法中使用set_header()会覆盖在set_default_headers里面设置的同名header
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
        print("start set_default_headers")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("mykey", "myvalue") # 自定义headers
        self.add_header("mykey", "youvalue")
        print("stop set_default_headers")

    def get(self):
        print("start GET")
        student = {"name": "zhangsan", "age": 18, "gender": 1}
        self.write(json.dumps(student)) # Content-Type: text/html; charset=UTF-8
        # self.write(student) # Content-Type: application/json; charset=UTF-8
        # self.set_header("mykey", "yourvalue") # 在此处会修改set_default_headers中同名的值
        print("stop GET")
        # start set_default_headers
        # stop set_default_headers
        # start GET
        # stop GET


if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler)
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()