from exception.CustomError import CustomError

class NotFoundError(CustomError):
    def __init__(self, message = 'Resource not found'):
        self.message = message
        self.code = 404
        super().__init__(message, 404)
