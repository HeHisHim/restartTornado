"""
def set_cookie(
    self,
    name: str,  -- cookie名
    value: Union[str, bytes],  -- cooked值
    domain: str = None,  -- 提交cookie时匹配的域名
    expires: Union[float, Tuple, datetime.datetime] = None,  -- cookie有效期, 可以是时间戳整数
    path: str = "/",  -- 提交cookie时匹配的路径
    expires_days: int = None,  -- cookie的有效天数, 优先级低于expires
    **kwargs: Any
) -> None
"""

"""
def get_cookie(self, name: str, default: str = None) -> Optional[str]
获取名为name的cookie, 默认为 None
"""

"""
def clear_cookie(self, name: str, path: str = "/", domain: str = None)
删除名为name, 并同时匹配domain和path的cookie

执行清理cookie操作后, 并不是立即删除浏览器的cookie, 而是给cookie值置为空, 并改变其有效期使其失效
真正的删除cookie是由浏览器去清理
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
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

class IndexHandler(RequestHandler):
    def get(self):
        if not self.get_cookie("mycookie"):
            self.set_cookie("mycookie", "y")
            # self.set_header("Set-Cookie", "mycookie=y") 相当于用set_header设置
        else:
            self.clear_cookie("mycookie")
        self.write("OK")

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()

    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
