class BadRequest(Exception):
    def __init__(self, message):
        super(BadRequest, self).__init__(message)
        self.status_code = 400
        self.message = message
