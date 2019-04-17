import logging
import json
import string
import random
import re
import asyncio
import tornado.ioloop

import utils.common
from tornado.web import RequestHandler
from utils.response_code import RET
from utils.session import Session

class ProfileHandler(RequestHandler):
    def get_current_user(self):
        if self.get_secure_cookie("session_id"):
            session_id = self.get_secure_cookie("session_id").decode("utf8")
            try:
                self.user_data = self.application.redis.get("sess_%s" % session_id)
            except Exception as e:
                logging.error(e)
                return False
            if self.user_data:
                self.user_data = json.loads(self.user_data)
                return True
            else:
                return False
        return False
    """个人信息"""
    @utils.common.require_logined # 验证登录
    def get(self):
        user_phone = self.user_data.get("mobile")
        datas = self.get_user_data_FromMySQL(user_phone)

        if not datas:
            return self.write(dict(errno = RET.SESSIONERR, errmsg = "用户不存在"))
        
        return self.write(dict(errno = RET.OK, data = {"name": datas[0], "mobile": user_phone, "avatar": datas[1]} ,errmsg = "用户验证通过"))
    
    def get_user_data_FromMySQL(self, mobile):
        datas = None
        SQL = "select up_name, up_avatar from ih_user_profile where up_mobile = %s;"
        with self.application.puredb.cursor() as cursor:
            try:
                cursor.execute(SQL, mobile)
                datas = cursor.fetchone()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql查询出错"))
        return datas