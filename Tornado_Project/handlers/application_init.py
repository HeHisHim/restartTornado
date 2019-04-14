import tormysql
import tornado.web
import urls
import config
import redis

class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, handlers = urls.handlers, **config.settings)
        self.db = tormysql.ConnectionPool(**config.mysql_options)
        self.redis = redis.Redis(**config.redis_options)