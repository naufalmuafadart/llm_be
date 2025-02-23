from application.domain.repository.AuthTokenRepository import AuthTokenRepository
from exception.UnauthorizedError import UnauthorizedError
from application.domain.entity.auth_token.AuthTokenPayloadEntity import AuthTokenPayloadEntity
from dotenv import load_dotenv
import os
import datetime
import jwt

class JWTAuthTokenRepository(AuthTokenRepository):
    def create(self, payload, is_access_token) -> str:
        load_dotenv()
        secret = os.getenv('ACCESS_TOKEN_SECRET') if is_access_token else os.getenv('REFRESH_TOKEN_SECRET')
        expires_in = int(os.getenv('ACCESS_TOKEN_EXPIRED_DURATION')) if is_access_token else int(os.getenv('REFRESH_TOKEN_EXPIRED_DURATION'))
        
        # Add expiration time to the payload
        payload.exp = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        # Generate the token
        token = jwt.encode(
            {
                'id': str(payload.id),
                'exp': payload.exp
            },
            secret,
            algorithm="HS256"
        )
        return token

    def validate(self, token: str, is_access_token : bool) -> dict:
        load_dotenv()
        secret = os.getenv('ACCESS_TOKEN_SECRET') if is_access_token else os.getenv('REFRESH_TOKEN_SECRET')
        try:
            # Decode and validate the token
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return AuthTokenPayloadEntity(
                payload['id'],
                payload['exp']
            )
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedError("Invalid token")

    def get_expired_at(self, token, is_access_token):
        load_dotenv()
        secret = os.getenv('ACCESS_TOKEN_SECRET') if is_access_token else os.getenv('REFRESH_TOKEN_SECRET')
        try:
            # Decode and validate the token
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload['exp']
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired.")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token.")
