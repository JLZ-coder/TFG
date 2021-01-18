from pymongo import MongoClient
from .Builder import Builder
from dao.daoBrotes import daoBrotes

class OutbreakBuilder(Builder):
    def __init__(self):
        super().__init__("outbreak")

    def create(self):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks

        cursor = brotes_db.find({})

        datos = {}

        for outbreak in cursor:
            oieid = outbreak["oieid"]

            datos[oieid] = outbreak

        return datos