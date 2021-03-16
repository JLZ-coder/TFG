import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import pygeohash as geohash
import geojsonComarcas

# Mete las comarcas en mongodb

#Leemos los dos archivos
file = "data/Comarcas_ganaderas.xlsx"
df = pd.read_excel(file)

file = "data/Centroides comarcas ganaderas.xlsx"
dfCentroide = pd.read_excel(file)

#Añadimos al dataframe que ira dentro de nuestra base de datos las coordenadas de los centroides
df = pd.merge(left=df,right=dfCentroide, left_on='comarca_sg', right_on='comarca_sg')
df = df.rename(columns={'XCoord': 'Longitud', 'YCoord': 'Latitud'})

#Segunda parte de los datos (Geojson)
#Extraemos los datos
file = "data/comarcasGanaderas.geojson"
leer = json.load(open(file, encoding='utf-8'))

com_sgsa_n = []
CPRO = []
provincia = []
CODAUTO = []
comAutonoma = []
CPROyMUN = []
coordenadas = []
geohashC = []

for comarca in leer['features']:
    com_sgsa_n.append(comarca['properties']['comarca'])
    coordenadas.append(comarca['geometry']['coordinates'])
    CPRO.append(comarca['properties']['CPRO'])
    provincia.append(comarca['properties']['provincia'])
    CODAUTO.append(comarca['properties']['CODAUTO'])
    comAutonoma.append(comarca['properties']['comAutonoma'])
    CPROyMUN.append(comarca['properties']['CPROyMUN'])

i = 0

for i in range(len(df)):
   geohashC.append(geohash.encode(df['Latitud'][i], df['Longitud'][i]))

df['com_sgsa_n'] = com_sgsa_n
df['CPRO'] = CPRO
df['provincia'] = provincia
df['CODAUTO'] = CODAUTO
df['comAutonoma'] = comAutonoma
df['CPROyMUN'] = CPROyMUN
df['coordinates'] = coordenadas
df['geohash'] = geohashC

#funcion para generar el cuadrante de cada comarca
df = geojsonComarcas.coordinatesFunc(df)
#Insercion de los datos en la base de datos
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
comarca = db.comarcas
records = df.to_dict(orient='records')


comarca.delete_many({})
comarca.insert_many(records)
