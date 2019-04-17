import logging
import json
import string
import random
import re
import asyncio
import tornado.ioloop

from tornado.web import RequestHandler
from utils.response_code import RET
from utils.session import Session

class IndexHandler(RequestHandler):
    def get(self):
        self.write(dict(errno = "123", errmsg = "123"))

class RegisterHandler(RequestHandler):
    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()
    async def post(self):
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
            check_phonecode = self.application.redis.get("sms_code_%s" % mobile)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno = RET.DBERR, errmsg = "redis查询出错"))

        # 手机验证码过期
        if not check_phonecode:
            return self.write(dict(errno = RET.NODATA , errmsg = "验证码过期"))

        if check_phonecode.decode("utf8") != phoneCode:
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
        task = []
        # task = asyncio.ensure_future(self.get_user_phone(mobile))
        task.append(asyncio.ensure_future(self.get_user_phone(mobile)))
        for done in asyncio.as_completed(task):
            data = await done
            # 有数据的话, 代表该手机已经被注册
            if data:
                return self.write(dict(errno = RET.PARAMERR, errmsg = "手机被注册了"))
        # 不能有空格
        if len(passwd.strip()) != len(passwd):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "密码有空格"))

        # 两次密码对比
        if len(passwd) != len(passwd2) or passwd != passwd2:
            return self.write(dict(errno = RET.PARAMERR, errmsg = "两次密码不一样"))

        """
        数据入库
        """
        save_task = []
        save_task.append(asyncio.ensure_future(self.save_user_data(mobile, mobile, passwd)))
        for done in asyncio.as_completed(save_task):
            data = await done
            if not data:
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql插入出错"))

        """
        设置session
        """
        try:
            self.session = Session(self)
            self.session.data["mobile"] = mobile
            self.session.data["name"] = mobile
            self.session.save()
        except Exception as e:
            logging.error(e)
        return self.write(dict(errno=RET.OK, errmsg = "注册成功"))

    async def get_user_phone(self, user_phone):
        datas = None
        SQL = "select up_mobile from ih_user_profile where up_mobile = %s"
        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(SQL, user_phone)
                    datas = cursor.fetchone()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql查询出错"))
        return datas

    async def save_user_data(self, name, mobile, passwd):
        datas = None
        SQL = "Insert into ih_user_profile (up_name, up_mobile, up_passwd) values (%s, %s, %s);"
        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    datas = await cursor.execute(SQL, (name, mobile, passwd))
            except Exception as e:
                logging.error(e)
                conn.rollback()
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql入库出错"))
        return datas

class LoginHandler(RequestHandler):
    def prepare(self):
        if self.request.headers.get("Content-Type") and self.request.headers.get("Content-Type").startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()
    
    async def post(self):
        mobile = self.dataBody.get("mobile")
        passwd = self.dataBody.get("password")

        task = []
        task.append(asyncio.ensure_future(self.check_user_data(mobile)))
        for done in asyncio.as_completed(task):
            user_data = await done
            if not user_data:
                return self.write(dict(errno = RET.USERERR, errmsg = "用户不存在"))
        
        # 密码是否正确
        if passwd != user_data[0]:
            return self.write(dict(errno = RET.PWDERR, errmsg = "密码错误"))

        # 设置session
        try:
            self.session = Session(self)
            self.session.data["mobile"] = mobile
            self.session.data["name"] = user_data[1]
            self.session.save()
        except Exception as e:
            logging.error(e)
        return self.write(dict(errno=RET.OK, errmsg = "登录成功"))


    async def check_user_data(self, mobile):
        datas = None
        SQL = "select up_passwd, up_name from ih_user_profile where up_mobile = %s;"
        async with await self.application.db.Connection() as conn:
            try:
                async with conn.cursor() as cursor:
                    await cursor.execute(SQL, mobile)
                    datas = cursor.fetchone()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql查询出错"))
        return datas

class CheckLoginHandler(RequestHandler):
    """检查登录状态"""
    def get(self):
        if self.get_secure_cookie("session_id"):
            session_id = self.get_secure_cookie("session_id").decode("utf8")
        else:
            return self.write(dict(errno = RET.SESSIONERR, errmsg = "False"))

        try:
            user_data = self.application.redis.get("sess_%s" % session_id)
        except Exception as e:
            logging.error(e)
        
        if user_data:
            user_data = json.loads(user_data)
            self.write(dict(errno = RET.OK, errmsg = "True", data = {"name": user_data.get("name")}))
        else:
            self.write(dict(errno = RET.SESSIONERR, errmsg = "False"))

