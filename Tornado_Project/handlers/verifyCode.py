from tornado.web import RequestHandler
import logging
import constants
from  utils.captcha.image import ImageCaptcha
import string
import random
characters = string.digits + string.ascii_lowercase

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

        random_str = ''.join([random.choice(characters) for _ in range(4)]) # 随机生成4个字符
        image = ImageCaptcha().generate(random_str)
        try:
            self.application.redis.setex("image_code_%s" % code_id, constants.IMAGE_CODE_EXPIRES_SECONDS, random_str)
        except Exception as e:
            logging.error(e)
            self.write("")
            return
        self.write(image.getvalue())

        
