"""
XSRF 跨站请求伪造
在Application构造函数中设置xsrf_cookies = True, 因为xsrf_cookies涉及到安全Cookie, 所以还需要同时配置cookie_secret开启密钥
当这个参数被设置时, Tornado将拒绝请求中不包含正确_xsrf值的POST, PUT和DELETE请求
并报错 403 Forbidden('_xsrf' argument missing from POST)
"""

"""
在模板中使用XSRF保护, 只需在模板中添加
{% module xsrf_form_html() %} -- xsrf_token.html

这样在会在模板代码中嵌入一句
<input type="hidden" name="_xsrf" value="2|746f1f8b|cf87bcd4923e5418549766b034d992cf|1554800413"/>
并在cookie中新增了一个_xsrf键值对
"""

"""
RequestHandler.xsrf_token
@property
def xsrf_token(self) -> bytes
该方法本质上是调用了self.set_cookie("_xsrf", self._xsrf_token, **cookie_kwargs)
在cookie中写上_xsrf的值
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import os
import uuid, base64
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError

define("port", default = 8000, type = int, help = "run server on the given port.")

class Application(tornado.web.Application):
    def __init__(self):
        handles = [
            (r"/", IndexHandler),
            (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html")}),
        ]
        settings = dict(
            debug = True,
            static_path = os.path.join(current_path, "static"),
            template_path = os.path.join(current_path, "template"),
            cookie_secret = "p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=",  # 配置密钥
            xsrf_cookies = True,
        )
        tornado.web.Application.__init__(self, handlers = handles, **settings)

# 继承tornado.web.StaticFileHandler, 进入静态页面的时候就设置xsrf_token
class StaticFileHandler(tornado.web.StaticFileHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.StaticFileHandler.__init__(self, *args, **kwargs)
        self.xsrf_token

class IndexHandler(RequestHandler):
    def get(self):
        # self.xsrf_token # 收到get请求就设置token
        self.render("xsrf_token.html")

    def post(self):
        self.write("OK")

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()

    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
