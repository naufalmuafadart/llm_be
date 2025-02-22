from exception.CustomError import CustomError

class UnauthorizedError(CustomError):
    def __init__(self, message = 'Unauthorized'):
        self.message = message
        self.code = 401
        super().__init__(message, 401)
