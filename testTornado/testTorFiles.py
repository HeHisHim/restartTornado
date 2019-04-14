"""
RequestHandler.request.files
file  用户上传的文件, 为字典类型, 如下:
{
    "form_filename1": [<tornado.httputil.HTTPFile>, <tornado.httputil.HTTPFile>],
    "form_filename2": [<tornado.httputil.HTTPFile>,],
    ...
}
self.request.files["form_filename1"]返回的是list类型, 可以通过self.request.files["form_filename1"][0]来获取客户端上传的第一个文件
文件有三个属性可以获取数据
1. filename: 文件的实际名字, 与form_filename1不同, form_filename1是表单的名字
2. body: 文件的数据实体
3. content_type: 文件类型
可以通过self.request.files["form_filename1"][0]["filename"]
self.request.files["form_filename1"][0]["body"]
self.request.files["form_filename1"][0]["content_type"]来获取对应的数据
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
    def post(self): # 使用postman Body(form_data - File)测试
        # print(self.request.files["image1"][0]["body"])
        imageName = self.request.files["image1"][0]["filename"]
        imagedata = self.request.files["image1"][0]["body"]
        with open("./static/" + imageName, "wb") as pFile:
            pFile.write(imagedata)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler)
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()