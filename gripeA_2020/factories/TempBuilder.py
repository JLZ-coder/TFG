from pymongo import MongoClient
from .Builder import Builder
from dao.daoBrotes import daoBrotes
from neo4j import GraphDatabase
import json

class OutbreakBuilder(Builder):
    def __init__(self):
        super().__init__("temp")

    def create(self, start, end):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        temps_db = db.outbreaks

        listaTemps = temps_db.find({"report_date" : {"$gt" : start, "$lte" : end}})

        # - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
        #     + Si hay un nodo, se miran todos los demas nodos asociados a este y lo guardamos si alguno de los nodos asociados esta en España

        tablaGeoComarca = json.load(open("data/tablaGeoComarca4.txt",  encoding='utf-8'))
        comarca_brotes = {}

        for brote in listaBrotes:
            geo_del_brote = brote['geohash'][0:4]

            for relacion in response:
                if relacion[0] in tablaGeoComarca:
                    for comarca in tablaGeoComarca[relacion[0]]:
                        cod = comarca["cod_comarca"]
                        if cod not in comarca_brotes:
                            comarca_brotes[cod] = [{"oieid" : brote["oieid"]}]
                        else:
                            comarca_brotes[cod].append({ "oieid" : brote["oieid"]})


        return comarca_brotes