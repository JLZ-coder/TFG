import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import pygeohash as geohash
import geojsonComarcas
#Leemos los dos archivos

file = "Comarcas_ganaderas.xlsx"
df = pd.read_excel(file)

file = "Centroides comarcas ganaderas.xlsx"
dfCentroide = pd.read_excel(file)

#Añadimos al dataframe que ira dentro de nuestra base de datos las coordenadas de los centroides
df['XCoord'] = dfCentroide['XCoord']
df['YCoord'] = dfCentroide['YCoord']

#Segunda parte de los datos (Geojson)
#Extraemos los datos
file = "comarcasGanaderas.geojson"
leer = json.load(open(file, encoding='utf-8'))

CPRO = []
provincia = []
CODAUTO = []
comAutonoma = []
CPROyMUN = []
coordenadas = []

for comarca in leer['features']:
    coordenadas.append(comarca['geometry']['coordinates'])
    CPRO.append(comarca['properties']['CPRO'])
    provincia.append(comarca['properties']['provincia'])
    CODAUTO.append(comarca['properties']['CODAUTO'])
    comAutonoma.append(comarca['properties']['comAutonoma'])
    CPROyMUN.append(comarca['properties']['CPROyMUN'])


df['CPRO'] = CPRO
df['provincia'] = provincia
df['CODAUTO'] = CODAUTO
df['comAutonoma'] = comAutonoma
df['CPROyMUN'] = CPROyMUN
df['coordinates'] = coordenadas

#funcion para generar el cuadrante de cada comarca
df = geojsonComarcas.coordinatesFunc(df)
#Insercion de los datos en la base de datos
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
comarca = db.comarcas
records = df.to_dict(orient='records')


comarca.delete_many({})
comarca.insert_many(records)
