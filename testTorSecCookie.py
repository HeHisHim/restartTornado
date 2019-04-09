"""
def set_secure_cookie(
    self,
    name: str,
    value: Union[str, bytes],
    expires_days: int = 30,
    version: int = None,
    **kwargs: Any
) -> None
Cookie是存储在客户端浏览器中的, 很容易被篡改. Tornado提供一种对Cookie进行简易加密签名的方法来防止Cookie被恶意篡改
使用安全Cookie需要为应用配置一个用来给Cookie进行混淆的密钥cookie_secret, 将其传递给Application的构造函数

设置一个带签名和时间戳的cookie, 防止cookie被伪造
"""

"""
使用base64, uuid来生成全局唯一的id, 用来混淆cookie
import uuid, base64
base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=
"""

"""
def get_secure_cookie(
    self,
    name: str,
    value: str = None,
    max_age_days: int = 31,
    min_version: int = None,
) -> Optional[bytes]
如果cookie存在且验证通过, 返回cookie值. 否则返回None
max_age_days不同与expires_days, expires_days是设置浏览器中cookie的有效期, 而max_age_days是过滤安全cookie的时间戳
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import os
import uuid, base64
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError, StaticFileHandler

define("port", default = 8000, type = int, help = "run server on the given port.")

# base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
# p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=

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
            cookie_secret = "p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=" # 配置密钥
        )
        tornado.web.Application.__init__(self, handlers = handles, **settings)

class IndexHandler(RequestHandler):
    def get(self):
        if not self.get_secure_cookie("who"):
            self.set_secure_cookie("who", "cook")
        else:
            val = self.get_secure_cookie("who")
            print(val)
        self.write("OK")

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()

    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
