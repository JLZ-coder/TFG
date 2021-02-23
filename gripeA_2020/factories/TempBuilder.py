from pymongo import MongoClient
from .Builder import Builder
from neo4j import GraphDatabase
import json

class TempBuilder(Builder):
    def __init__(self):
        super().__init__("temp")

    def create(self, start, end):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        temps_db = db.historico

        
        tempMin = temps_db.find()

       


        return tempMin