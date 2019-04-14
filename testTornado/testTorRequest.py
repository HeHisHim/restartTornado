"""
RequestHandler.request对象存储了关于请求的相关信息, 具体属性如下
1. method  HTTP的请求方式, 如GET / POST
2. host  被请求的主机名
3. uri  请求的完整资源标示, 包括路径和查询字符串
4. path  请求的路径部分
5. query  请求的查询字符串部分
6. version  使用的HTTP版本
7. headers  请求的协议头, 是类字典型的对象(继承collections.abc.MutableMapping来实现). 支持关键字索引的方式获取特定协议头信息, 如(request.headers["Content-Type"])
8. body  请求体数据
9. remote_ip  客户端的IP地址
10. file  用户上传的文件, 为字典类型, 如下:
    {
        "form_filename1": [<tornado.httputil.HTTPFile>, <tornado.httputil.HTTPFile>],
        "form_filename2": [<tornado.httputil.HTTPFile>,],
        ...
    }
"""

"""
获取request的json数据
request.headers["Content-Type"].startswith("application/json"):
1. 对request.headers的Content-Type判断是否有application/json, 如果有则代表有json数据, 数据保存再request.body里面
2. 使用内置的json库对request.body内容解析(json.loads(self.request.body))
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
        rep = "method: {}</br>".format(self.request.method)
        rep += "host: {}</br>".format(self.request.host)
        rep += "uri: {}</br>".format(self.request.uri)
        rep += "path: {}</br>".format(self.request.path)
        rep += "query: {}</br>".format(self.request.query)
        rep += "version: {}</br>".format(self.request.version)
        rep += "headers: {}</br>".format(self.request.headers)
        rep += "body: {}</br>".format(self.request.body)
        rep += "remote_ip: {}</br>".format(self.request.remote_ip)
        self.write(rep)
    def post(self): # 使用postman Body(raw - JSON)测试
        rep = "headers: {}</br>".format(self.request.headers)
        if self.request.headers["Content-Type"].startswith("application/json"): # 判断是否有json文件
            rep = "body: {}</br>".format(self.request.body) # json数据存在body里面
            json_data = json.loads(self.request.body)
            realBody = "realBody: {}</br>".format(json_data.get("bbc")) # 解析出的数据可以像字典一样使用
            rep += realBody
        self.write(rep)
        

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler)
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()