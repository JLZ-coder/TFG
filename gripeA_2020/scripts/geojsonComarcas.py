import json
import os
import pymongo
from pymongo import MongoClient

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
comarca = db.comarcas

#Extraccion de datos
geojson = {}
cursor = comarca.find({})

print(cursor)
#Carpeta destino

