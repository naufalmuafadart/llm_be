from application.domain.repository.AuthRepository import AuthRepository
from application.infrastructure.database.mongo_db import MongoDBClient
import pymongo

class MongoAuthRepository(AuthRepository):
    def insert(self, token, user_id, expired_at):
        client = MongoDBClient()
        db = client.get_database()
        mycol = db["auths"]

        mydict = {
            "token": token,
            "user_id": user_id,
            "expired_at": expired_at
        }

        x = mycol.insert_one(mydict)
