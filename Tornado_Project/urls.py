import os

from handlers import passPort, verifyCode

from tornado.web import StaticFileHandler

current_path = os.path.dirname(__file__)

handlers = [
    # (r"/", passPort.IndexHandler),
    (r"/api/imagecode", verifyCode.ImageCodeHandler),
    (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "html"), "default_filename": "index.html"}),
]