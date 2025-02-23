from application.domain.repository.AuthRepository import AuthRepository
from application.infrastructure.database.mongo_db import MongoDBClient
from exception.NotFoundError import NotFoundError

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
    
    def validate_token_exist(self, token, user_id):
        client = MongoDBClient()
        db = client.get_database()
        collection = db["auths"]

        count = collection.count_documents({
            'user_id': user_id,
            'token': token
        })

        if count == 0:
            raise NotFoundError('Auth token not found' + str(user_id))
