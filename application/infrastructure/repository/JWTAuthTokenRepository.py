from application.domain.repository.AuthTokenRepository import AuthTokenRepository
from dotenv import load_dotenv
import os
import datetime
import time
import json
import hmac
import hashlib
import base64
import jwt

class JWTAuthTokenRepository(AuthTokenRepository):
    def create(self, payload: dict, is_access_token) -> str:
        load_dotenv()
        secret = os.getenv('ACCESS_TOKEN_SECRET') if is_access_token else os.getenv('REFRESH_TOKEN_SECRET')
        expires_in = int(os.getenv('ACCESS_TOKEN_EXPIRED_DURATION')) if is_access_token else int(os.getenv('REFRESH_TOKEN_EXPIRED_DURATION'))
        
        # Add expiration time to the payload
        payload["exp"] = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        # Generate the token
        token = jwt.encode(payload, secret, algorithm="HS256")
        return token

    def validate(self, token: str, is_access_token : bool) -> dict:
        load_dotenv()
        secret = os.getenv('ACCESS_TOKEN_SECRET') if is_access_token else os.getenv('REFRESH_TOKEN_SECRET')
        try:
            # Decode and validate the token
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired.")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token.")

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
