from tornado.web import RequestHandler

class IndexHandler(RequestHandler):
    def get(self):
        # print(self.application.db)
        # print(self.application.redis)
        self.write("Hello World")