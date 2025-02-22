from application.domain.repository.HashingRepository import HashingRepository
from exception.CustomError import CustomError
import bcrypt

class BcryptHashingRepository(HashingRepository):
    def hash(self, text):
        password_bytes = text.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return str(hashed_password)[2:][-1]

    def verify(self, plain_text, hashed_text):
        # Check if the password matches the hash
        if (not bcrypt.checkpw(plain_text.encode('utf-8'), bytes(hashed_text, 'utf-8'))):
            raise CustomError('Text not match')
