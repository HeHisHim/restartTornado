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

对于json和xml无法通过上述方法获取
"""

"""
关于default的默认值_ARG_DEFAULT
"""