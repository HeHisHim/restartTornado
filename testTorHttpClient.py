"""
tornado.httpclient.AsyncHTTPClient
Tornado提供了一个异步Web请求客户端AsyncHTTPClient来进行异步Web请求
"""

"""
def fetch(
    self,
    request: Union[str, "HTTPRequest"],
    raise_error: bool = True,
    **kwargs: Any
) -> Awaitable["HTTPResponse"]
用于执行一个Web请求request, 并异步返回一个tornado.httpclient.HTTPResponse响应
request可以是一个url, 也可以是一个tornado.httpclient.HTTPRequest对象, 如果是url, fetch会自己构造一个HTTPRequest对象
"""

"""
HTTPRequest
HTTP请求类, HTTPRequest的构造函数可以接收众多构造参数, 最常用的如下:
1. url(string): 要访问的url, 此参数必传, 除此之外均为可选参数
2. method(string): HTTP访问方式, 如"GET"或"POST", 默认方法为"GET"
3. headers(HTTPHeaders or dict): 附加的HTTP协议头
4. body: HTTP请求的请求体
"""

"""
HTTPResponse
HTTP响应类, 其常用属性如下:
1. code: HTTP状态码, 如200或404
2. reason: 状态码描述信息
3. body: 响应体字符串
4. error: 异常(可有可无)
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import os
import pymysql
import asyncio
import time
import uuid, base64
from tornado.options import options, define
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, MissingArgumentError, StaticFileHandler

url = "http://ip.taobao.com/service/getIpInfo.php?ip=" # 输入ip, 返回ip所在区域, json格式数据

ipList = ["11.70.184.41", "121.70.193.41", "160.70.184.4", "211.20.184.41", "190.70.184.41", "90.70.184.184"]
# 美国 中国 德国 台湾 哥伦比亚 法国
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
            login_url = "/login", # 当用户验证失败时, 将用户重定向到该url上
            cookie_secret = "p8ekSGn5STe7MpVopQjQgUoE1fjuMUtDjTLPWrgVKKg=",  # 配置密钥
            xsrf_cookies = True,
        )
        tornado.web.Application.__init__(self, handlers = handles, **settings)

class IndexHandler(RequestHandler):
    async def get(self):
        start = time.time()
        self.client = AsyncHTTPClient()
        # 封装成task对象, 并发执行
        tasks = [
            asyncio.ensure_future(self.get_ip_info(ipList[1], 1)),
            asyncio.ensure_future(self.get_ip_info(ipList[5], 5)),
            asyncio.ensure_future(self.get_ip_info(ipList[3], 3)),
            asyncio.ensure_future(self.get_ip_info(ipList[0], 0)),
            asyncio.ensure_future(self.get_ip_info(ipList[4], 4)),
            asyncio.ensure_future(self.get_ip_info(ipList[2], 2)),
        ]

        # 等待全员状态为finished的时候, 输出结果
        # dones, _ = await asyncio.wait(tasks)
        # for done in dones:
        #     self.write_response(done.result())

        # 当有一个task状态为finished, 就输出结果
        for done in asyncio.as_completed(tasks):
            result = await done
            print(type(result))
            self.write_response(result)
        print(time.time() - start)

    def write_response(self, data):
        self.write(data)
        self.write("<br/>")
        print("now flush: ", data)
        self.flush()

    # 异步获取ip地址数据
    async def get_ip_info(self, ip, index):
        # await asyncio.sleep(index * 1) # 可开启这句测试是否并发执行, 注释下面的代码
        response = None
        code = -1
        while 200 != code: # 当状态码不为200, 则一直循环直到请求成功
            try:
                response = await self.client.fetch(url + ip)
                code = response.code
            except Exception as e:
                print(e)
                return "Error"
        try:
            if response:
                data = json.loads(response.body)
                return data["data"]["country"]
            return "Error"
        except Exception as e:
            print(e)

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()

    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
