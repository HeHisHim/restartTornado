from tornado.web import RequestHandler
import logging
import constants
from  utils.captcha.image import ImageCaptcha
from utils.response_code import RET
import string
import random
import re
import json
CHARACTERS = string.digits + string.ascii_lowercase

# 验证码Handler
class ImageCodeHandler(RequestHandler):
    def set_default_headers(self):
        self.set_header("Content-Type", "image/png")
    def get(self):
        code_id = self.get_argument("codeid")
        pre_code_id = self.get_argument("pcodeid") # 之前的一个验证码id
        if pre_code_id:
            try:
                self.application.redis.delete("image_code_%s" % pre_code_id)
            except Exception as e:
                logging.error(e)

        random_str = ''.join([random.choice(CHARACTERS) for _ in range(4)]) # 随机生成4个字符
        image = ImageCaptcha().generate(random_str)
        try:
            self.application.redis.setex("image_code_%s" % code_id, constants.IMAGE_CODE_EXPIRES_SECONDS, random_str)
        except Exception as e:
            logging.error(e)
            self.write("")
            return
        self.write(image.getvalue())


class PhoneCodeHandler(RequestHandler):
    def prepare(self):
        if self.request.headers["Content-Type"].startswith("application/json"):
            self.dataBody = json.loads(self.request.body)
            if not self.dataBody:
                self.dataBody = dict()

    def post(self):
        """
        判断验证码
        成功: 发送短信 不成功: 返回错误信息
        """
        mobile = self.dataBody.get("mobile")
        piccode_id = self.dataBody.get("piccode_id")
        piccode = self.dataBody.get("piccode")
        if not all((mobile, piccode, piccode_id)):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "参数不完整"))

        # 正则判断手机号
        if not re.match(r"1\d{10}", mobile):
            return self.write(dict(errno = RET.PARAMERR, errmsg = "手机号错误"))

        try:
            imageTxT = self.application.redis.get("image_code_%s" % piccode_id).decode("utf8")
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno = RET.DBERR, errmsg = "查询出错"))
        
        if not imageTxT:
            return self.write(dict(errno = RET.NODATA , errmsg = "验证码过期"))

        if imageTxT.lower() != piccode.lower():
            return self.write(dict(errno = RET.DATAERR , errmsg = "验证码错误"))

        check_num = "%04d" % random.randint(0, 9999)
        try:
            self.application.redis.setex("sms_code_%s" % mobile, constants.SMS_CODE_EXPIRES_SECONDS, check_num)
        except Exception as e:
            logging.error(e)
            return self.write(dict(errno = RET.DBERR, errmsg = "生成短信验证码出错"))

        return self.write(dict(errno=RET.OK, errmsg = "OK", secret = check_num))
        
