import json
import requests
import re
import pandas as pd
from aemet import *
import pymongo
from pymongo import MongoClient

#tabla = json.load(open("estaciones.txt",  encoding='utf-8'))
#aemet_client = Aemet(api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YUB1Y20uZXMiLCJqdGkiOiJiZDc2MzgzMS1hMWU4LTQ4MTktOTE2Yy1lYzQ5MjE2OTJiYjAiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwNjQ3NTk4NiwidXNlcklkIjoiYmQ3NjM4MzEtYTFlOC00ODE5LTkxNmMtZWM0OTIxNjkyYmIwIiwicm9sZSI6IiJ9.0Z3PqEjKyMFhUztyu2LAPV7zYPEaeh2RXndZQdryTrE', verbose=True)
#aemet_client.descargar_resumen_mensual_climatologico("aemet.txt", 2018, 12)


#Leemos el fichero que relaciona las estaciones con las comarcas
file = "aemet/Estaciones_CG.xlsx"

df = pd.read_excel(file)
#diccionario que tendra como clave "id de comarca" y valor la informacion de las estaciones
#Insercion de los datos en la base de datos
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
estacion = db.estaciones
records = df.to_dict(orient='records')

estacion.delete_many({})
estacion.insert_many(records)



       
        




