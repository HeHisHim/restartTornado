from handlers import passPort, verifyCode

handlers = [
    (r"/", passPort.IndexHandler),
    (r"/api/imagecode", verifyCode.ImageCodeHandler),
]