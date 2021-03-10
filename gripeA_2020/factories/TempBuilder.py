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

        estaciones = estacion_db.find({})
        tempMin = {}

        for it in estaciones:
            valor = list(temps_db.find({'idEstacion': it['indicativo']}, {'_id':False, 'historico(semanal)':True}))
            
            if valor == []:#Si la estacion principal no tiene datos se busca la siguiente más cercana
                aux = []
                i = 1
                while aux == []:
                    aux = list(temps_db.find({'idEstacion': it['estacionesAdd'][i]}, {'_id':False, 'historico(semanal)':True}))
                    i +=1

                tempMin[it['comarca_sg']] = aux[0]['historico(semanal)']
            else:
                tempMin[it['comarca_sg']] = valor[0]['historico(semanal)']
       
        return tempMin