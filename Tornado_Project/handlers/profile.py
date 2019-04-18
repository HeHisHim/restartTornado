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
        self.user_data = dict()
        return utils.common.get_current_user(self)
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

class NameHandler(RequestHandler):
    def get_current_user(self):
        self.user_data = dict()
        return utils.common.get_current_user(self)

    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()

    @utils.common.require_logined # 验证登录
    def post(self):
        """
        name: xxx
        修改session的数据
        更新session刷新redis
        操作mysql update名字
        """
        name = self.dataBody.get("name")
        try:
            self.session = Session(self)
            self.session.data["name"] = name
            self.session.save()
        except Exception as e:
            logging.error(e)

        data = self.update_user_name(name, self.user_data.get("mobile"))
        if not data:
            return self.write(dict(errno = RET.DBERR, errmsg = "更换错误"))

        return self.write(dict(errno = RET.OK, errmsg = "更新成功"))

    def update_user_name(self, name, phone):
        datas = None
        SQL = "update ih_user_profile set up_name = %s where up_mobile = %s;"
        with self.application.puredb.cursor() as cursor:
            try:
                datas = cursor.execute(SQL, (name, phone))
                self.application.puredb.commit()
            except Exception as e:
                logging.error(e)
                self.application.puredb.rollback()
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        return datas

class AuthHandler(RequestHandler):
    def prepare(self):
        if self.request.headers.get("Content-Type") and self.request.headers.get("Content-Type").startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()

    def get_current_user(self):
        self.user_data = dict()
        return utils.common.get_current_user(self)

    @utils.common.require_logined # 验证登录
    def get(self):
        user_phone = self.user_data.get("mobile")
        user_datas = self.get_real_data(user_phone)
        if user_datas:
            return self.write(dict(errno = RET.OK, errmsg = "OK", data = {"real_name": user_datas[0], "id_card": user_datas[1]}))

    @utils.common.require_logined # 验证登录
    def post(self):
        user_phone = self.user_data.get("mobile")
        real_name = self.dataBody.get("real_name")
        id_card = self.dataBody.get("id_card")
        if not all((real_name, id_card)):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "参数错误"))

        data = self.set_real_data(user_phone, real_name, id_card)
        if not data:
            return self.write(dict(errno = RET.DBERR, errmsg = "更换错误"))

        return self.write(dict(errno = RET.OK, errmsg = "更新成功"))

    def get_real_data(self, mobile):
        datas = None
        SQL = "select up_real_name, up_id_card from ih_user_profile where up_mobile = %s;"
        with self.application.puredb.cursor() as cursor:
            try:
                cursor.execute(SQL, mobile)
                datas = cursor.fetchone()
            except Exception as e:
                logging.error(e)
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        return datas

    def set_real_data(self, mobile, real_name, id_card):
        datas = None
        SQL = "update ih_user_profile set up_real_name = %s, up_id_card = %s where up_mobile = %s;"
        with self.application.puredb.cursor() as cursor:
            try:
                datas = cursor.execute(SQL, (real_name, id_card, mobile))
                self.application.puredb.commit()
            except Exception as e:
                logging.error(e)
                self.application.puredb.rollback()
                return self.write(dict(errno = RET.DBERR, errmsg = "mysql出错"))
        return datas