from utils.response_code import RET
import functools

def require_logined(fun):
    @functools.wraps(fun)
    def wrapper(request_handler, *args, **kwargs):
        # 根据get_current_user判断 是否已经登录(判断session数据)
        if not request_handler.get_current_user():
            request_handler.write(dict(errno = RET.SESSIONERR, errmsg = "用户未登录"))
        else:
            fun(request_handler, *args, **kwargs)
    return wrapper