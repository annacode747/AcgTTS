class ResponseData:
    massage = ''
    code = 200
    data = {}

    def __init__(self, massage='OK', code=200):
        self.massage = massage
        self.code = code
        self.data = None

    def renderSuccess(self, data=None, massage=None):
        return {
            'code': self.code,
            'data': data,
            'massage': massage if massage is not None else self.massage
        }

    def renderError(self, massage=None):
        return {
            'code': self.code,
            'data': self.data,
            'massage': massage if massage is not None else self.massage
        }