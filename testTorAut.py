"""
用户验证
用户验证是指在收到用户请求后进行处理前先判断用户的认证状态(如登录状态), 若通过验证则正常处理, 否则强制用户跳转至认证页面(如登录页面)
"""

"""
@tornado.web.authenticated
若要使用Tornado认证功能, 需要对登录用户标记具体的处理函数. 可以使用@tornado.web.authenticated装饰目标函数
当使用这个装饰器包裹一个处理方法时, Tornado将确保这个方法的主体只有在用户被认证的时候才会被调用
"""

"""
get_current_user()方法
装饰器@tornado.web.authenticated的判断执行依赖于请求处理类中的self.current_user属性
如果current_user值为假(None, False, 0, ""等), 任何GET或者HEAD请求都将把访客重定向到应用设置中login_url指定的URL中
而非法用户的POST将返回一个带有403(状态的HTTP响应)

在获取self.current_user属性的时候, tornado会调用get_current_user()方法来返回current_user的值
也就是说, 验证用户的逻辑应该写在get_current_user()方法中. 若该方法返回真则表示通过验证, 否则验证失败
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

class Application(tornado.web.Application):
    def __init__(self):
        handles = [
            (r"/", IndexHandler),
            (r"/login", LoginHandler),
            (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html")}),
        ]
        settings = dict(
            debug = True,
            static_path = os.path.join(current_path, "static"),
            template_path = os.path.join(current_path, "template"),
            login_url = "/login", # 当用户验证失败时, 将用户重定向到该url上
            cookie_secret = "p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=",  # 配置密钥
            xsrf_cookies = True,
        )
        tornado.web.Application.__init__(self, handlers = handles, **settings)

class LoginHandler(RequestHandler):
    def get(self):
        next_url = self.get_argument("next", "")
        if next_url:
            print("myNext: ", next_url)
            self.redirect(next_url + "?f=login")
        else:
            self.write("Login Login")

    def post(self):
        pass

class IndexHandler(RequestHandler):
    def get_current_user(self): # 验证逻辑
        val = self.get_argument("f", None)
        if val:
            print("ok, I got it")
            return True
        return False

    @tornado.web.authenticated # 必须通过验证才能调用GET
    def get(self):
        self.xsrf_token
        self.write("Index OK")

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()

    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
