import pymongo
from pymongo import MongoClient

class daoMongo:

    _instance = None

    def __new__(cls):
        if cls._instance is None:

            cls._instance = super(daoMongo, cls).__new__(cls)
            cls._client = MongoClient('mongodb://localhost:27017/')
            cls._collection = cls._client.lv

        return cls._instance

    def close(self):
        self._instance = None
        self._client.close()