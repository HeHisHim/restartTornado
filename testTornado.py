import tornado.web
import tornado.ioloop

class IndexHandler(tornado.web.RequestHandler):
    """主页请求类"""
    def get(self):
        """get请求处理"""
        self.write("Hello Abc")
    
    def post(self):
        # 返回 405: Method Not Allowed
        pass

if __name__ == "__main__":
    app = tornado.web.Application([(r"/",   IndexHandler)])
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()


"""
tornado.web.Application是Tornado的核心应用类
是与服务器对接的接口, 里面保存了路由信息表
其初始化接收的第一个参数就是一个路由信息映射元组的列表
其listen(端口)方法用来创建一个http服务器实例, 并绑定到给定端口
上面app.listen(8000)只是绑定8000端口, 并未开启监听
"""