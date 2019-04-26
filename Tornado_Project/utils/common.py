from utils.response_code import RET
import functools
import logging
import json

def require_logined(fun):
    @functools.wraps(fun)
    def wrapper(request_handler, *args, **kwargs):
        # 根据get_current_user判断 是否已经登录(判断session数据)
        if not request_handler.get_current_user():
            request_handler.write(dict(errno = RET.SESSIONERR, errmsg = "用户未登录"))
        else:
            fun(request_handler, *args, **kwargs)
    return wrapper

def get_current_user(handler):
    if handler.get_secure_cookie("session_id"):
        handler.session_id = handler.get_secure_cookie("session_id").decode("utf8")
        try:
            handler.user_data = handler.application.redis.get("sess_%s" % handler.session_id)
        except Exception as e:
            logging.error(e)
            return False
        if handler.user_data:
            handler.user_data = json.loads(handler.user_data.decode("utf8"))
            return True
        else:
            return False
    return False