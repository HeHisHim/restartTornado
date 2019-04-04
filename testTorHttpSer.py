"""
使用tornado.httpserver实现端口绑定
即手动实现testTornado.py中的app.listen(8000)
因为tornado整合了http服务器和web框架
"""

"""
引入tornado.httpserver即tornado的HTTP服务器实现
因为服务器要服务于创建的web应用, 将接收到的客户端请求通过web应用中的路由映射表引导到对应的handle中
所以构建的http_server对象的时候需要传入web应用对象app
http_server.listen(8000)意为将服务器绑定到8000端口
app.listen(8000)正是对这一过程的简写
"""

"""
使用tornado.httpserver开启多进程服务
使用http_server.bind(port)将服务器绑定到指定端口
http_server.start(num_processes = 1)方法指定开启几个进程
num_processes参数默认为1, 即开启一个进程. 如果num_processes为None或者小于0, 则根据机器硬件CPU核心数创建同等数目的子进程
如果num_processes > 0, 则创建num_processes个子进程
"""

"""
关于tornado的多进程
虽然tornado提供了开启多进程的方式, 但是由于
1. 每个子进程都会从父进程中复制一份IOLoop实例, 如果在创建子进程前改动了IOLoop实例, 则会影响到每一个子进程, 这会干扰到子进程IOLoop的工作
2. 所有进程都是由一个命令一次开启的, 也就无法做到在不停服务的情况下更新代码
3. 所有进程共享同一个端口, 想要分别单独监控每一个进程就很困难
不建议使用这种多进程方式, 而是手动开启多个进程, 并且绑定不同的端口

"""

import tornado.web
import tornado.ioloop
import tornado.httpserver

class IndexHandler(tornado.web.RequestHandler):
    """主路由请求类"""
    def get(self):
        """get请求处理"""
        self.write("Hello Tornado")

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", IndexHandler)
    ])
    # ----------------------------
    # 修改这部分
    # app.listen(8000)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(8000)
    # 通过这样调用启动时是单进程
    # ----------------------------

    """多进程启动"""
    # ----------------------------
    # http_server = tornado.httpserver.HTTPServer(app)
    # http_server.bind(8000)
    # http_server.start(0)
    # ----------------------------
    tornado.ioloop.IOLoop.current().start()