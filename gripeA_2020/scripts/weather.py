import json
import requests
import re
import pandas as pd
import dbf
#from aemet import *
import pymongo
from pymongo import MongoClient
from datetime import datetime

api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YWxlbmNpYWJhcmNlbG9uYUBnbWFpbC5jb20iLCJqdGkiOiJiYzY4MzM1Mi1kZjg3LTRlZTctYjQ4MS1hMDMyODQzZGMwMWIiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYxMDM4OTY0OCwidXNlcklkIjoiYmM2ODMzNTItZGY4Ny00ZWU3LWI0ODEtYTAzMjg0M2RjMDFiIiwicm9sZSI6IiJ9.BanUHViE2mFsnjne_ilriezZqkDRYYT3Vf4SkKOcE04'

#tabla = json.load(open("estaciones.txt",  encoding='utf-8'))
#aemet_client = Aemet(api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YUB1Y20uZXMiLCJqdGkiOiJiZDc2MzgzMS1hMWU4LTQ4MTktOTE2Yy1lYzQ5MjE2OTJiYjAiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwNjQ3NTk4NiwidXNlcklkIjoiYmQ3NjM4MzEtYTFlOC00ODE5LTkxNmMtZWM0OTIxNjkyYmIwIiwicm9sZSI6IiJ9.0Z3PqEjKyMFhUztyu2LAPV7zYPEaeh2RXndZQdryTrE', verbose=True)
#aemet_client.descargar_resumen_mensual_climatologico("aemet.txt", 2018, 12)

tabla = json.load(open("historico1.json",  encoding='utf-8'))



        
#Leemos el fichero que relaciona las estaciones con las comarcas
file = "aemet/CG_estaciones.xlsx"
df = pd.read_excel(file)

#Insertamos la relacion de estaciones con comarcas en mongoDB
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
estacion = db.estaciones
records = df.to_dict(orient='records')


estacion.delete_many({})
estacion.insert_many(records)
 

# dbf.export(table, filename='CG', format='csv', header=False, encoding='ascii')
# #diccionario que tendra como clave "id de comarca" y valor la informacion de las estaciones
# #Insercion de los datos en la base de datos


#Extraemos los indicativos de todas las estaciones
cursor = estacion.find({},{'indicativo':True, '_id':False}).distinct('indicativo')

indicativos = list(cursor)
headers = {
    'cache-control': "no-cache"
}

df = dict()
#url para valores mensuales
#url_mensualAnual = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/2020/aniofin/2020/estacion/0252D/?api_key={}".format(api_key)
j=1
#Solo rango de 5 años 
for i in range(2019,2021):
    #Valores para la URL
    fechaini = "{}-01-01T00:00:00UTC".format(i)
    fechafin = "{}-12-31T00:00:00UTC".format(i)

    for idEstacion in indicativos: #Recorremos la lista 
         
        #Url para valores diarios YYYY-MM-DDTHH:MM:SSUTC
        url_valoresDiaros = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{}/fechafin/{}/estacion/{}/?api_key={}".format(fechaini, fechafin,idEstacion,api_key)
        #Extraemos la url donde esta la informacion de la consulta a la API
        response = requests.request("GET", url_valoresDiaros, headers=headers)
        json_response = response.json()

        if response.status_code == 200 and json_response['estado'] == 200:
            #Extraemos la informacion de la API
            response = requests.request("GET", json_response['datos'], headers=headers)
            try:
                json_response = response.json()

                #Extraemos la url donde esta la informacion de la consulta a la API
                response = requests.request("GET", url_valoresDiaros, headers=headers)
            
                json_response = response.json()

                #Extraemos la informacion de la API
                response = requests.request("GET", json_response['datos'], headers=headers)

                json_response = response.json()
            except:
                print(response)

            #Tmin, fecha
            aux = {}
            for api in json_response:

                if 'tmin' in api:
                    t = ""
                    for l, caracter in enumerate(api['tmin']): #Cambiar formato de la temperatura
                        if caracter == ',':
                            t += '.'
                        else:
                            t += caracter 

                    #fecha_dt = datetime.strptime(api['fecha'], '%Y-%m-%d')
                    #aux[fecha_dt] = float(t)
                    aux[api['fecha']] = float(t)

            #Comarca -> indicativo, historico con las temperaturas minimas 
            cursor = estacion.find({'indicativo': idEstacion},{'indicativo':True,'comarca_sg': True, '_id':False} )
            for it in cursor:
     
                if it['comarca_sg'] not in df:
                    df[it['comarca_sg']] = {'comarca_sg': it['comarca_sg'], 'idEstacion': it['indicativo'], 'historico': dict(aux)}
                else: 
                    df[it['comarca_sg']].append({'comarca_sg': it['comarca_sg'], 'idEstacion': it['indicativo'], 'historico':dict(aux)})
    
text_file = open("historico1.json", "w")
n = text_file.write(json.dumps(df))
text_file.close()
j+=1
    



#records = df.to_dict(orient='records')

historico = db.historico
#historico.delete_many({})
historico.insert_many(df)           
    




