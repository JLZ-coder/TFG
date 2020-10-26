import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import geohash

#Leemos los dos archivos 

file = "Comarcas_ganaderas.xlsx"
df = pd.read_excel(file)

file = "Centroides comarcas ganaderas.xlsx"
dfCentroide = pd.read_excel(file)

#Añadimos al dataframe que ira dentro de nuestra base de datos las coordenadas de los centroides
df['XCoord'] = dfCentroide['XCoord']
df['YCoord'] = dfCentroide['YCoord']

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
comarca = db.comarcas
records = df.to_dict(orient='records')  

comarca.insert_many(records)
print(df)