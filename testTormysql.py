"""
数据库连接初始化
tornado需要在应用启动时创建一个数据库连接实例, 供各个RequestHandler使用
可以在构造Application的时候创建一个数据库实例, 并设置成Application的属性
而RequestHandler可以通过self.application获取其属性, 进而操作数据库实例
"""
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import json
import pymysql
import tormysql
import os
import time
import asyncio
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
        # 创建一个全局的mysql连接供Handler调用 同步调用方式
        # self.db = pymysql.connect("127.0.0.1", "root", "1231230", "itcast")
        ## 异步调用方式
        self.db = tormysql.ConnectionPool(
               max_connections = 20, #max open connections
                idle_seconds = 7200, #conntion idle timeout time, 0 is not timeout
                wait_connection_timeout = 3, #wait connection timeout
                host = "127.0.0.1",
                user = "root",
                passwd = "1231230",
                db = "itcast",
                charset = "utf8"
        )

class IndexHandler(RequestHandler):
    # 改写成异步调用
    async def get(self):
        begin = time.time()
        idList = self.get_arguments("id")
        tasks = []

        if not idList:
            self.render("main.html")
            return

        for id in idList:
            tasks.append(asyncio.ensure_future(self.asyncFetchData(id)))
        
        for done in asyncio.as_completed(tasks):
            data = await done
            if data:
                data = json.dumps(data[0][2])
                self.write(data)
                self.write("<br/>")
                print(data)
                print("now: flush")
                self.flush()
            else:
                self.write("Error<br/>")
                self.flush()
        print("spend time: ", time.time() - begin)

    async def asyncFetchData(self, id):
        datas = None
        sql = "select hi_name, hi_address, hi_price from it_house_info where hi_user_id = %s;"
        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(sql, id)
                    datas = cursor.fetchall()
            except Exception as e:
                print(e)
        return datas

    ## 同步调用
    # def get(self):
    #     begin = time.time()
    #     idList = self.get_arguments("id")
    #     for id in idList:
    #         data = self.fetchData(id)
    #         if data:
    #             data = json.dumps(data[0][2])
    #             self.write(data)
    #             self.write("<br/>")
    #             print(data)
    #             print("now: flush")
    #             self.flush()
    #         else:
    #             self.write("Error<br/>")
    #             self.flush()
    #     print("spend time: ", time.time() - begin)


    # def fetchData(self, id):
    #     data = None
    #     with self.application.db.cursor() as cursor:
    #         sql = "select hi_name, hi_address, hi_price from it_house_info where hi_user_id = %s;"
    #         try:
    #             cursor.execute(sql, id)
    #             data = cursor.fetchall()
    #         except Exception as e:
    #             print(e)
    #         return data

if __name__ == "__main__":
    current_path = os.path.dirname(__file__)
    tornado.options.parse_command_line()
    # 以下改用类来封装
    # app = tornado.web.Application([
    #     (r"/", IndexHandler),
    #     (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "static/html"), "default_filename": "index.html"}), # 未指明时默认提供index.html
    # ], 
    # debug = True,
    # static_path = os.path.join(current_path, "static"),
    # template_path = os.path.join(current_path, "template"),)
    app = Application()

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
