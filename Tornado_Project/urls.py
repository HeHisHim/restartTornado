import os

from handlers import passPort, verifyCode, profile, house

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
    (r"/api/login", passPort.LoginHandler),
    (r"/api/check_login", passPort.CheckLoginHandler),
    (r"/api/profile", profile.ProfileHandler),
    (r"/api/logout", passPort.LogoutHandler),
    (r"/api/profile/name", profile.NameHandler),
    (r"/api/profile/auth", profile.AuthHandler),
    (r"/api/house/area", house.AreaIngoHandler),
    (r"/api/house/my", house.MyHouseHandler),
    (r"/api/house/info", house.HouseInfoHandler),
    (r"/api/house/list", house.HouseListHandler),
    (r"^/(.*)$", StaticFileHandler, {"path": os.path.join(current_path, "html"), "default_filename": "index.html"}),
]