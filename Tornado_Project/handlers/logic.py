import logging
import json
import string
import re
import asyncio
import tornado.ioloop

import utils.common
from tornado.web import RequestHandler
from utils.response_code import RET
from utils.session import Session

class LogicBaseHandler(RequestHandler):
    def prepare(self):
        if self.request.headers.get("Content-Type") and \
                self.request.headers.get("Content-Type").startswith("application/json"):
            self.JsonArgs = json.loads(self.request.body)
            if not self.JsonArgs:
                self.JsonArgs = dict()

    def get_current_user(self):
        self.session = Session(self)
        return self.session.data