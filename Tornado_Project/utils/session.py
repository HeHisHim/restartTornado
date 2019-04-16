import uuid
import logging
import json
import config

class Session:
    def __init__(self, request_handler):
        self.request_handler = request_handler
        self.session_id = self.request_handler.get_secure_cookie("session_id")
        self.data = {}
        # 如果为空, 表示用户第一次登录, 生成一个新的session_id(全局唯一)
        if not self.session_id:
            self.session_id = uuid.uuid4().hex
        else:
            try:
                data = self.request_handler.application.redis.get("sess_%s" % self.session_id)
            except Exception as e:
                logging.error(e)
            if data:
                self.data = json.loads(data.decode("utf8"))

    def save(self):
        json_data = json.dumps(self.data)
        try:
            self.request_handler.application.redis.setex("sess_%s" % self.session_id, config.SESSION_EXPIRES_SECONDS, json_data)
        except Exception as e:
            logging.error(e)
            raise Exception("save session failed")
        else:
            self.request_handler.set_secure_cookie("session_id", self.session_id)

    def clear(self):
        self.request_handler.clear_cookie("session_id")
        try:
            self.request_handler.application.redis.delete("sess_%s" % self.session_id)
        except Exception as e:
            logging.error(e)