import pandas as pd
import pymongo
import pygeohash as geohash

#Extraemos datos de migraciones y comarcas de nuestra bases de datos

client = MongoClient('mongodb://localhost:27017/')
db = client.lv
comarcas = db.comarcas
migraciones = db.migrations


