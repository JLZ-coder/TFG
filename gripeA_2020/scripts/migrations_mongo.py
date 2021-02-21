import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import pygeohash as geohash
import openpyxl 
import datetime
# Metemos las migraciones en mongo si son de las especies que queremos

#Ficheros necesarios
#file = "mov_acuaticas ult 10 años.xlsx"
file = "data/Datos especies1.xlsx"
file1 = "data/Especies.xlsx"

df = pd.read_excel(file, 'Movimientos')

df_especies = pd.read_excel(file1)

#Ahora borramos todos los que tengan 'localidad confidencial'
'''df = df[df.Localidad != 'Localidad confidencial']
df = df[df.LocalidadR != 'Localidad confidencial']
df1 = df_especies['codigo anilla'].tolist()
df = df[df.Especie.isin(df1)]


#Ahora borramos las columnas que nos sobran:
df.drop(['Cod_Localidad', 'Cod_LocalidadR', 'EspecieR', 'Verificacion',
         'InfoAnillaR', 'AnillaR', 'AmpliacionAnillaR', 'CentroR', 'SexoR', 'EdadR'], axis='columns', inplace=True)

#Ahora vamos a dar formato a las coordenadas:

df['CuadranteLongitudR'] = df['CuadranteLongitudR'].map({'W':'-', 'E':'+'})
df['CuadranteLongitud'] = df['CuadranteLongitud'].map({'W':'-', 'E':'+'})
df['CuadranteLatitud'] = df['CuadranteLatitud'].map({'S':'-', 'N':'+'})
df['CuadranteLatitudR'] = df['CuadranteLatitudR'].map({'S':'-', 'N':'+'})
'''
#df['Lat'] = df['CuadranteLatitud'].map(str) + df['LatitudGrados'].map(str) + '.' + df['LatitudMinutos'].map(str)
#df['Long'] = df ['CuadranteLongitud'].map(str) + df['LongitudGrados'].map(str) + '.' + df['LongitudMinutos'].map(str)

df = df.rename(columns={'Lat_A': 'Lat', 'long_a': 'Long', 'LAT_R': 'LatR', 'LON_R': 'LongR', 'FechaAnill':'FechaAnillamiento'})
df ['geohash'] = df.apply(lambda x: geohash.encode(float(x.Lat), float(x.Long)), axis=1)
df ['geohashR'] = df.apply(lambda x: geohash.encode(float(x.LatR), float(x.LongR)), axis=1)

#df['LatR'] = df['CuadranteLatitudR'].map(str) + df['LatitudGradosR'].map(str) + '.' + df['LatitudMinutosR'].map(str)
#df['LongR'] = df ['CuadranteLongitudR'].map(str) + df['LongitudGradosR'].map(str) + '.' + df['LongitudMinutosR'].map(str)

df = df[df.geohash != df.geohashR]
#date = datetime.datetime.fromtimestamp(df['FechaAnillamiento'][0]*100)


#df['FechaAnillamiento'] = df['FechaAnillamiento'].multiply(1000)
#df['FechaAnillamiento'] = pd.to_datetime(df['FechaAnillamiento'], unit='ms')
#df['FechaRecuperacion'] = pd.to_datetime(df['FechaAnillamiento'], format= "%d/%m/%y")

#df.drop(['LatitudGrados', 'LatitudMinutos', 'LongitudGrados', 'LongitudMinutos', 'CuadranteLatitud', 'CuadranteLongitud'], axis='columns', inplace=True)
#df.drop(['LatitudGradosR', 'LatitudMinutosR', 'LongitudGradosR', 'LongitudMinutosR', 'CuadranteLatitudR', 'CuadranteLongitudR'], axis='columns', inplace=True)
#df.drop(['Unnamed: 31'], axis='columns', inplace=True)

#df['index'] = df.index

#print (df)


client= MongoClient('mongodb://localhost:27017/')
db = client.lv
migrations = db.migrations
records = df.to_dict(orient='records')  # Here's our added param..
# Borra todo
migrations.delete_many({})
#records = json.loads(df.T.to_bson()).values()
migrations.insert_many(records)

