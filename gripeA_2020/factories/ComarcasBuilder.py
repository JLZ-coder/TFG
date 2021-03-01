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

        comarcas_dict = dict()

        for comarca in listaComarca:
            comarcas_dict[comarca['comarca_sg']] = comarca

        return comarcas_dict