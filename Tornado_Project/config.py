import os

log_level = "debug"
log_file = os.path.join(os.path.dirname(__file__), "logs/log.txt")
# Session有效时长(秒)
SESSION_EXPIRES_SECONDS = 86400

settings = dict(
    debug = True,
    static_path = os.path.join(os.path.dirname(__file__), "static"),
    template_path = os.path.join(os.path.dirname(__file__), "template"),
    cookie_secret = "",
    xsrf_cookies = True,
    login_url = "/login", 
)

mysql_options = dict(
    max_connections = 20, #max open connections
    idle_seconds = 7200, #conntion idle timeout time, 0 is not timeout
    wait_connection_timeout = 3, #wait connection timeout
    host = "",
    user = "",
    passwd = "",
    db = "",
    charset = ""
)

redis_options = dict(
    host = "", 
    port = 0, 
    db = 0, 
    password = ""
) 