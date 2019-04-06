"""
路径与渲染
使用模板, 路径设置与静态文件设置一样, 在tornado.web.Application添加template_path告知Tornado从文件系统中寻址
"""

"""
RequestHandler.render() 用于渲染主页模板, 并返回给客户端
"""

"""
static_url()
Tornado模板提供了一个叫做static_url函数来生成静态文件目录下文件的URL

<link href="{{ static_url('css/index.css') }}" rel="stylesheet">
相当于增添 "?v=fe8ccdaf962ce00b725138ef260cbf0c"
<link href="/static/css/index.css?v=fe8ccdaf962ce00b725138ef260cbf0c" rel="stylesheet">

1. static_url函数创建了一个基于文件内容的hash值, 并将其添加到URL末尾(即参数v), 这个hash值确保浏览器总是加载一个文件的最新版本, 而不是浏览器的缓存版本
2. 另一个好处时可以改变应用URL的结构, 而不需要改变模板中的代码. 例如可以通过设置static_url_prefix来更改Tornado默认静态路径前缀/static. 使用static_url更灵活
"""

"""
tornado默认是开启模板自动转义, 防止网站受到恶意攻击

autoescape = None
关闭自动转义, 全局生效, 不建议. 这会导致xss注入攻击

RequestHandler.set_header("X-XSS-Protection", 0)  0: 禁止XSS过滤 1: 启动XSS过滤
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

class IndexHandler(RequestHandler):
    def get(self):
        houses = [{"price": 210}, {"price": 310}, {"price": 300}]
        self.render("index.html", houses = houses, index = 0)

class NewHandler(RequestHandler):
    def get(self):
        self.render("new.html", text = "")

    def post(self):
        text = self.get_argument("text", default = "")
        self.render("new.html", text = text)

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/new", NewHandler),
        (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html"), "default_filename": "index.html"}), # 未指明时默认提供index.html
    ], 
    debug = True,
    autoescape = None, # 关闭全局自动转义
    static_path = os.path.join(current_path, "static"),
    template_path = os.path.join(current_path, "template"),)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()