import pymongo
from daoMongo import daoMongo

class daoBrotes(daoMongo):

    def __init__(self):
        super()
        self._doc = self._collection.outbreaks

    def find(self, query = {}):
        return self._doc.find(query)

    def insert_one(self, transfer = {}):
        return self._doc.insert_one(transfer)
    def insert_many(self, transfer = {}):
        return self._doc.insert_many(transfer)

    def update_one(self, query = {}, newValue = {}):
        return self._doc.update_one(query, newValue)
    def update_many(self, query = {}, newValue = {}):
        return self._doc.update_many(query, newValue)

    def delete_one(self, query = {}):
        return self._doc.delete_one(query)
    def delete_many(self, query = {}):
        return self._doc.delete_many(query)