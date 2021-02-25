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
        temps_db = db.historico
        estacion_db = db.estaciones

        valor = list(historico.find({'idEstacion': "0002I"}, {'_id':False, 'historico(semanal)':True}))

        print(valor[0]['historico(semanal)']['2017'][0])
        tempMin = temps_db.find()

       
        return tempMin