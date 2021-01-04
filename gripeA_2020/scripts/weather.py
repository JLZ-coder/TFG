import json
import requests
import re
import pandas as pd
import dbf
#from aemet import *
import pymongo
from pymongo import MongoClient
api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YUB1Y20uZXMiLCJqdGkiOiJiZDc2MzgzMS1hMWU4LTQ4MTktOTE2Yy1lYzQ5MjE2OTJiYjAiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwNjQ3NTk4NiwidXNlcklkIjoiYmQ3NjM4MzEtYTFlOC00ODE5LTkxNmMtZWM0OTIxNjkyYmIwIiwicm9sZSI6IiJ9.0Z3PqEjKyMFhUztyu2LAPV7zYPEaeh2RXndZQdryTrE'

#tabla = json.load(open("estaciones.txt",  encoding='utf-8'))
#aemet_client = Aemet(api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YUB1Y20uZXMiLCJqdGkiOiJiZDc2MzgzMS1hMWU4LTQ4MTktOTE2Yy1lYzQ5MjE2OTJiYjAiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwNjQ3NTk4NiwidXNlcklkIjoiYmQ3NjM4MzEtYTFlOC00ODE5LTkxNmMtZWM0OTIxNjkyYmIwIiwicm9sZSI6IiJ9.0Z3PqEjKyMFhUztyu2LAPV7zYPEaeh2RXndZQdryTrE', verbose=True)
#aemet_client.descargar_resumen_mensual_climatologico("aemet.txt", 2018, 12)


# #Leemos el fichero que relaciona las estaciones con las comarcas
# file = "aemet/CG_Estaciones_Aemet.dbf"
# table = dbf.Table(file)

# table.open(mode=dbf.READ_WRITE)

 

# dbf.export(table, filename='CG', format='csv', header=False, encoding='ascii')
# #diccionario que tendra como clave "id de comarca" y valor la informacion de las estaciones
# #Insercion de los datos en la base de datos

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
estacion = db.estaciones
#records = df.to_dict(orient='records')

# estacion.delete_many({})
# estacion.insert_many(records)

#Extraemos los indicativos de todas las estaciones
cursor = estacion.find({},{'INDICATIVO':True, '_id':False}).distinct('INDICATIVO')

indicativos = list(cursor)
headers = {
    'cache-control': "no-cache"
}

df = {}

url_mensualAnual = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/2020/aniofin/2020/estacion/0252D/?api_key={}".format(api_key)
#Extraemos la url donde esta la informacion de la consulta a la API
response = requests.request("GET", url_mensualAnual, headers=headers)

json_response = response.json()

#Extraemos la informacion de la API
response = requests.request("GET", json_response['datos'], headers=headers)

json_response = response.json()

df[0] = json_response






#Extraemos la url donde esta la informacion de la consulta a la API
response = requests.request("GET", url_mensualAnual, headers=headers)

json_response = response.json()

#Extraemos la informacion de la API
response = requests.request("GET", json_response['datos'], headers=headers)

json_response = response.json()

print(json_response)
        




