import os

from handlers import passPort, verifyCode

import tornado.web

current_path = os.path.dirname(__file__)

class StaticFileHandler(tornado.web.StaticFileHandler):
    def __init__(self, *args, **kwargs):
        tornado.web.StaticFileHandler.__init__(self, *args, **kwargs)
        self.xsrf_token

handlers = [
    # (r"/", passPort.IndexHandler),
    (r"/api/imagecode", verifyCode.ImageCodeHandler),
    (r"/api/smscode", verifyCode.PhoneCodeHandler),
    (r"/api/register", passPort.RegisterHandler),
    (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "html"), "default_filename": "index.html"}),
]