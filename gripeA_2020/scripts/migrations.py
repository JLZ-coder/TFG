import pandas as pd
import pymongo
from pymongo import MongoClient
import json
import geohash

file = "mov_acuaticas ult 10 años.xlsx"

df = pd.read_excel(file)

#Ahora borramos todos los que tengan 'localidad confidencial'
df = df[df.Localidad != 'Localidad confidencial']
df = df[df.LocalidadR != 'Localidad confidencial']




#Ahora borramos las columnas que nos sobran:
df.drop(['Cod_Localidad', 'Cod_LocalidadR', 'EspecieR', 'Verificacion',
         'InfoAnillaR', 'AmpliacionAnillaR', 'CentroR'], axis='columns', inplace=True)

#Ahora vamos a dar formato a las coordenadas:

df['CuadranteLongitudR'] = df['CuadranteLongitudR'].map({'W':'-', 'E':'+'})
df['CuadranteLongitud'] = df['CuadranteLongitud'].map({'W':'-', 'E':'+'})
df['CuadranteLatitud'] = df['CuadranteLatitud'].map({'S':'-', 'N':'+'})
df['CuadranteLatitudR'] = df['CuadranteLatitudR'].map({'S':'-', 'N':'+'})

df['Lat'] = df['CuadranteLatitud'].map(str) + df['LatitudGrados'].map(str) + '.' + df['LatitudMinutos'].map(str)
df['Long'] = df ['CuadranteLongitud'].map(str) + df['LongitudGrados'].map(str) + '.' + df['LongitudMinutos'].map(str)
df ['geohash'] = df.apply(lambda x: geohash.encode(float(x.Lat), float(x.Long)), axis=1)



df['LatR'] = df['CuadranteLatitudR'].map(str) + df['LatitudGradosR'].map(str) + '.' + df['LatitudMinutosR'].map(str)
df['LongR'] = df ['CuadranteLongitudR'].map(str) + df['LongitudGradosR'].map(str) + '.' + df['LongitudMinutosR'].map(str)
df ['geohashR'] = df.apply(lambda x: geohash.encode(float(x.LatR), float(x.LongR)), axis=1)

df['FechaAnillamiento'] = pd.to_datetime(df['FechaAnillamiento'], format= "%d/%m/%y")
df['FechaRecuperacion'] = pd.to_datetime(df['FechaAnillamiento'], format= "%d/%m/%y")

df.drop(['LatitudGrados', 'LatitudMinutos', 'LongitudGrados', 'LongitudMinutos', 'CuadranteLatitud', 'CuadranteLongitud'], axis='columns', inplace=True)
df.drop(['LatitudGradosR', 'LatitudMinutosR', 'LongitudGradosR', 'LongitudMinutosR', 'CuadranteLatitudR', 'CuadranteLongitudR'], axis='columns', inplace=True)
df.drop(['Unnamed: 31'], axis='columns', inplace=True)


#print (df)


client= MongoClient('mongodb://localhost:27017/')
db = client.lv
migrations = db.migrations
records = df.to_dict(orient='records')  # Here's our added param..

#records = json.loads(df.T.to_bson()).values()
migrations.insert_many(records)
