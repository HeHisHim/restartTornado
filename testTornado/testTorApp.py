"""
tornado.web.Application的构造函数除了第一个是接收路由映射列表外, 还会接收很多关于tornado web应用的配置参数

debug
设置tornado是否工作在调试模式下, 默认为False即工作在生产模式.
当设置debug = True后, tornado会工作在调试 / 开发模式, 在此模式下tornado提供以下特性
1. 自动重启: tornado会监控源码文件, 当有改动保存后就重启程序, 这可以减少手动重启次数. 但是如果保存的更改有错误, tornado会报错然后退出. 从而需要自己手动重启
2. 取消缓存编译模板: 可以单独通过compiled_template_cache = False来设置
3. 取消缓存静态文件hash值: 可以单独通过static_hash_cache = False来设置
4. 提供追踪信息: 当RequestHandler或者其子类抛出一个异常而未被捕获后, 会生成一个包含追踪信息的页面, 可以单独

使用debug参数
import tornado.web
app = tornado.web.Application([], debug = True)
"""

"""
路由中的name字段是特殊字段
name字段不能再使用元组, 而应使用tornado.web.url来构建
name是给该路由起一个名字, 可以通过调用RequestHandler.reserse_url(name)来获取该名字对应的url
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.web import RequestHandler, url

tornado.options.define("port", default = 8000, type = int, help = "run server on the given port") # 定义服务器监听端口选项

class IndexHandler(RequestHandler):
    def get(self):
        python_url = self.reverse_url("python_url")
        # print("python_url: ", python_url) # /python
        self.write("<a href = {}>Tornado</a>".format(python_url))

class ItCastHandler(RequestHandler):
    def initialize(self, subject):
        self.subject = subject

    # def initialize(self, **kwargs): # 可以使用kwargs来获取数据
    #     self.subject = kwargs["subject"]

    def get(self):
        self.write(self.subject)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", IndexHandler), 
        (r"/cpp", ItCastHandler, {"subject": "c++"}), # 路由中的字典会传入对应的RequestHandler的initialize()方法中
        url(r"/python", ItCastHandler, {"subject": "python"}, name = "python_url"),
    ], debug = True)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()