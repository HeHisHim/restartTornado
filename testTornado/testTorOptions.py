"""
tornado提供了一个便捷的工具 - tornado.options模块
该模块用于全局参数定义, 存储和转换
"""

"""
tornado.options.define()
该函数用于定义options选项变量的方法, 定义的变量可以在全局的tornado.options.options中获取使用, 传入参数:
1. name: 选项变量名, 需保证全局唯一性, 否则会报"Option 'xxx' already defined in"的错误
2. default: 选项变量的默认值, 如不传默认为None
3. type: 选项变量的类型, 从命令行或配置文件导入参数时, tornado会根据这个类型转换输入的值
4. multiple: 布尔类型, 选项变量的值是否可以为多个. 默认为False, 如果为True, 那么设置选项变量时值与值之间用英文逗号分隔, 而选项变量则是一个list列表(若默认值和输入均未设置, 则为空列表[])
5. help: 选项变量的帮助提示信息, 在命令行启动tornado时通过参数 --help, 可以查看所有的选项变量信息(使用此功能时需要在代码中加入tornado.options.parse_command_line())
"""

"""
tornado.options.options
全局的options对象, 所有定义的选项变量都会作为该对象的属性
"""

"""
tornado.options.parse_command_line()
转换命令行参数, 并将转换后的值对应到全局options对象相关的属性上. 追加命令行参数的方式是 --myoption = myvalue
"""

"""
tornado.options.parse_config_file(path)
从配置文件中导入option, 配置文件中的选项格式如下:
myoption = "myvalue"
myotheroption = "myothenvalue"
新建配置文件config
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options

tornado.options.define("port", default = 8000, type = int, help = "run server on the given port") # 定义服务器监听端口选项
tornado.options.define("testCase", default = None, type = str, multiple = True, help = "testCase") # 无意义, 演示多值情况

class IndexHandler(tornado.web.RequestHandler):
    """主路由请求类"""
    def get(self):
        """get请求处理"""
        self.write("Hello Options")

if __name__ == "__main__":
    # tornado.options.parse_command_line() #使用命令行传参配置
    tornado.options.parse_config_file("./config") # 使用配置文件传参
    print(tornado.options.options.testCase)

    app = tornado.web.Application([
        (r"/", IndexHandler),
    ])

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.current().start()