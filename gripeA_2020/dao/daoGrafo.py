import neo4j
from neo4j import GraphDatabase
from daoNeo4j import 

class daoGrafo(daoNeo4j):

    def __init__(self):
        super()

    def find(self, match, where, ret):
        return self._session()

    def insert(self, create):
        return self._doc.insert_one(transfer)

    def update(self, query = {}, newValue = {}):
        return self._doc.update_one(query, newValue)

    def delete(self, query = {}):
        return self._doc.delete_one(query)