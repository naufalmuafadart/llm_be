from application.domain.repository.UserRepository import UserRepository
from pymongo import MongoClient
from exception.NotFoundError import NotFoundError
from application.domain.entity.user.RegisteredUserEntity import RegisteredUserEntity
from application.infrastructure.database.mongo_db import MongoDBClient

class MongoUserRepository(UserRepository):
    def get_by_email(self, email):
        client = MongoDBClient()
        db = client.get_database()
        users_collection = db['users']

        # Find the user document by email
        user = users_collection.find_one({"email": email})
        _id = user.get('_id')
        password = user.get('password')

        if not user:
            raise NotFoundError('Email not found')
        
        return RegisteredUserEntity(
            _id,
            email,
            password
        )
