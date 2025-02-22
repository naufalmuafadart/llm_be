from pymongo import MongoClient
import os
from dotenv import load_dotenv

class MongoDBClient:
    _instance = None

    def __new__(cls, uri=""):
        if not cls._instance:
            load_dotenv()
            user_name = os.getenv('MONGO_USER_NAME')
            password = os.getenv('MONGO_PASSWORD')
            url = os.getenv('MONGO_URL')
            database_name = os.getenv('MONGO_DB')
            uri = f"mongodb+srv://{user_name}:{password}@{url}"

            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(uri)
            cls._instance.db = cls._instance.client[database_name]
        return cls._instance

    def get_database(self):
        return self.db
