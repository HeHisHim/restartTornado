"""
tornado.web.Application是Tornado的核心应用类
是与服务器对接的接口, 里面保存了路由信息表
其初始化接收的第一个参数就是一个路由信息映射元组的列表
其listen(端口)方法用来创建一个http服务器实例, 并绑定到给定端口
上面app.listen(8000)只是绑定8000端口, 并未开启监听
"""

"""
tornado.ioloop
tornado的核心IO循环模块, 封装了linux的epoll和BSD的kqueue, 这些是tornado高性能的基石
IOLoop.current()返回当前线程的IOLoop实例
IOLoop.current().start()启动IOLoop实例的IO循环, 同时打开服务器监听8000端口
"""

"""
一个简单的Tornado Web程序启动流程
1. 创建web应用实例对象, 第一个初始化参数为路由映射列表, 即r"/", r修饰表示不转义后面的字符
2. 定义实现路由映射列表中的handler类即IndexHandler
3. 创建服务器实例, 绑定服务器端口即app.listen(8000)
4. 启动当前线程的IOLoop
"""
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

