import logging
import json
import string
import random
import re

from tornado.web import RequestHandler
from utils.response_code import RET

class IndexHandler(RequestHandler):
    def get(self):
        self.write("Hello World")

class RegisterHandler(RequestHandler):
    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()
        print(self.dataBody)
    def post(self):
        mobile = self.dataBody.get("mobile")
        phoneCode = self.dataBody.get("phonecode")
        passwd = self.dataBody.get("password")
        passwd2 = self.dataBody.get("password2")

        if not all((mobile, phoneCode, passwd, passwd2)):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "参数真不完整"))
        
        # 正则判断手机号
        if not re.match(r"1\d{10}", mobile):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "手机号错误"))

        # 获取redis手机验证码
        try:
            check_phonecode = self.application.redis.get("sms_code_%s" % mobile).decode("utf8")
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno = RET.DBERR, errmsg = "查询出错"))

        # 手机验证码过期
        if not check_phonecode:
            return self.write(dict(errno = RET.NODATA , errmsg = "验证码过期"))

        if check_phonecode != phoneCode:
            return self.write(dict(errno = RET.DATAERR , errmsg = "验证码错误"))

        # 验证码取出后delete掉
        try:
            self.application.redis.delete("sms_code_%s" % mobile)
        except Exception as e:
            logging.error(e)

        """
        判断手机有没在mysql里面
        没有才继续往下执行, 否则return
        """

        # 不能有空格
        if len(passwd.strip()) != len(passwd):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "密码有空格"))

        # 两次密码对比
        if len(passwd) != len(passwd2) or passwd != passwd2:
            return self.write(dict(errno = RET.PARAMERR, errmsg = "两次密码不一样"))

        return self.write(dict(errno=RET.OK, errmsg = "注册成功"))