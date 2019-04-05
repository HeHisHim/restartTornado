"""
利用HTTP协议向服务器传参有以下途径
1. 查询字符串(query string), 形如?key1=value1&key2=value2
2. 请求体(body)中发送的数据, 如表单数据, json和xml
3. 提取url的特定部分, 如/blogs/2020/20/20, 可以在服务器端的路由中使用正则表达式截取
4. 在HTTP报头(Header)中增加自定义字段, 如X-XSRFToken=myvalue
"""

"""
tornado使用以下方法来获取请求的信息
1. 获取查询字符串参数
get_query_argument(name, default = _ARG_DEFAULT, strip = True)
从请求的查询字符串中返回指定参数name的值, 如果出现多个同名参数, 则返回最后一个值
default设置为未传入name时的默认值, 如default也未设置, 则会抛出tornado.web.MissingArgumentError异常
strip表示是否过滤参数左右两边的空白字符, 默认为过滤

get_query_arguments(name, strip = True)
从请求的查询字符串中返回指定参数name的值, 返回的是list列表(即使对应name参数只有一个值). 若没有name参数, 则返回空列表[]

2. 获取请求体参数
get_body_argument(name, default = _ARG_DEFAULT, strip = True)
从请求体中返回指定参数name的值, 如果出现多个同名参数, 则返回最后一个值

get_body_arguments(name, strip = True)
从请求体中返回指定参数name的值, 返回的是list列表(即使对应name参数只有一个值). 若没有name参数, 则返回空列表[]

3. 上述方法的整合
get_argument(name, default = _ARG_DEFAULT, strip = True)
从请求体和查询字符串中返回指定参数name的值, 如果出现多个同名参数, 则返回最后一个值

get_arguments(name, strip = True)
从请求体和查询字符串中返回指定参数name的值, 返回的是list列表(即使对应name参数只有一个值). 若没有name参数, 则返回空列表[]

使用get_argument / get_arguments, 如果get / post都有同样的参数名称, 会按顺序先取出get的参数再取出post的参数
因为get是放在请求头里面的, 按照http解析顺序会先取get里面的参数. 而post是放在请求体里面的, 所以是后取
所以上述条件中, get_argument获取的参数是body里面最后一个参数

对于json和xml无法通过上述方法获取
"""

"""
关于default的默认值_ARG_DEFAULT
是一个全局类, 专门用来判断是否设置了与_ARG_DEFAULT不一样的对象, 类里面不做任何处理
class _ArgDefaultMarker:
    pass
"""

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.options import options, define
from tornado.web import RequestHandler, MissingArgumentError

define("port", default = 8000, type = int, help = "run server on the given port.")

class InderHandler(RequestHandler):
    def get(self):
        # query_arg = self.get_query_argument("query", default = 1)
        # query_args = self.get_query_arguments("query")
        query_arg = self.get_argument("query", default = 10)
        query_args = self.get_arguments("query")
        rep = "query_arg: {}</br>query_args: {}</br>".format(query_arg, query_args)
        self.write(rep)
    def post(self): # 使用postman Body(x-www-form-urlencoded)测试
        # body_arg = self.get_body_argument("body", default = 10)
        # body_args = self.get_body_arguments("body")
        body_arg = self.get_argument("body", default = 13)
        body_args = self.get_arguments("body")
        rep = "body_arg: {}</br>body_args: {}</br>".format(body_arg, body_args)
        self.write(rep)

if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", InderHandler)
    ], debug = True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
