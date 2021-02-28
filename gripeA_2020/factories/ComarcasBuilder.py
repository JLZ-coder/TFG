from pymongo import MongoClient
from .Builder import Builder
import os, sys

class ComarcasBuilder(Builder):
    def __init__(self):
        super().__init__("comarcas")

    def create(self, start, end, parameters):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        comarcas_db = db.comarcas

        listaComarcas = comarcas_db.find({})

        # - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
        #     + Si hay un nodo, se miran todos los demas nodos asociados a este y lo guardamos si alguno de los nodos asociados esta en España

        comarcas_dict = dict()

        for comarca in listaComarca:
            comarcas_dict[comarca['comarca_sg']] = comarca

        return comarcas_dict