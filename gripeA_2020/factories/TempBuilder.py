from pymongo import MongoClient
from .Builder import Builder
from neo4j import GraphDatabase
import json

class TempBuilder(Builder):
    def __init__(self):
        super().__init__("temp")

    def create(self, start, end, parameters):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        temperatura = db.temperatura

        cursor = temperatura.find({},{'_id':False, 'comarca_sg':True,'historicoFinal':True})

        tempMin = {}

        for i in cursor:
            tempMin[i['comarca_sg']] = i['historicoFinal']
       
        return tempMin