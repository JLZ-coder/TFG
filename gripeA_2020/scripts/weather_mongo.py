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
#Insercion de los datos en la base de datos
file = "data/DistanciasCG_estaciones_200km.xlsx"
df = pd.read_excel(file)
df = df.groupby('Codigo_comarca')
#df = df.reset_index()

for key, item in df:
    p = df.get_group(key)
    #Eliminamos repetidos manteniendo el orden
    d = dict()
    for i in p['Estacion_cod']:
        if i not in d:
            d.setdefault(i,i) 

    p = list(d.keys())

    estacion.update({'comarca_sg':key},{"$set": {"estacionesAdd":p}})


cursor = estacion.find({})
df = pd.DataFrame(list(cursor))
df.to_excel('data/estaciones.xlsx', index=False)
#Extraemos los indicativos de todas las estaciones
cursor = estacion.find({},{'indicativo':True, '_id':False}).distinct('indicativo')

indicativos = list(cursor)
headers = {
    'cache-control': "no-cache"
}

df = list()
#url para valores mensuales
#url_mensualAnual = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/2020/aniofin/2020/estacion/0252D/?api_key={}".format(api_key)
j=1
#Solo rango de 5 años 

#Valores para la URL
#fechaini = "{}-01-01T00:00:00UTC".format(i)
#fechafin = "{}-12-31T00:00:00UTC".format(i)

'''
empty = {}
#Sacar estaciones que no presentan historico
for idEstacion in indicativos:
    cursor = list(historico.find({'idEstacion': idEstacion}, {'idEstacion':True, '_id':False}))

    if cursor == []:
        #Sacamos las comarcas que no tienen asociado un historico
        it = list(estacion.find({'indicativo': idEstacion},{'comarca_sg':True,  '_id':False}))
        aux=[]
        for i in it:
            aux.append(i['comarca_sg'])
        empty[idEstacion] = aux


text_file = open("../data/emptyCG-IDE.json", "w")
n = text_file.write(json.dumps(empty))
text_file.close()
'''

#2017-2021
fechaini = "2017-01-02T00:00:00UTC"
fechafin = "2021-01-31T00:00:00UTC"

for idEstacion in indicativos: #Recorremos la lista 
        
    #Url para valores diarios YYYY-MM-DDTHH:MM:SSUTC
    url_valoresDiaros = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{}/fechafin/{}/estacion/{}/?api_key={}".format(fechaini, fechafin,idEstacion,api_key)
    #Extraemos la url donde esta la informacion de la consulta a la API
    response = requests.request("GET", url_valoresDiaros, headers=headers)
    json_response = response.json()

    if json_response['estado'] == 404:
        print("Descripcion error: {} para la estacion {}".format(json_response['descripcion'], idEstacion))
    elif response.status_code == 200 and json_response['estado'] == 200:
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

        aux = {}
        
        #diccionario que va a mongo
        semanal = {'2017':[None]*53, '2018':[None]*53, '2019':[None]*53, '2020':[None]*53, '2021':[None]*53}
        #Calcular media semanal
        semana = [None]*53
        contador = [0]*53
        anio = 2017 
        semanaFinal =[None]*53
        for api in json_response:
            if 'tmin' in api:
                t = ""
                for l, caracter in enumerate(api['tmin']): #Cambiar formato de la temperatura
                    t += '.' if (caracter == ',') else caracter

                #fecha_dt = datetime.strptime(api['fecha'], '%Y-%m-%d')
                #aux[fecha_dt] = float(t)
                aux[api['fecha']] = float(t)


                fecha_dt = datetime.strptime(api['fecha'], '%Y-%m-%d')

                semanaActual = fecha_dt.isocalendar()[1]-1
                if anio != fecha_dt.year and (semanaActual >= 0 and semanaActual < 52):
                    #Meter valores medios semanales
                    for i in range(0,len(semana)):
                        if semana[i] == None:
                            semanaFinal[i] = None
                        else:
                            semanaFinal[i] = semana[i]/contador[i]
                    semanal[str(anio)] = semanaFinal
                    #Restablecer contadores 
                    semana = [None]*53
                    contador = [0]*53
                    anio = fecha_dt.year
                    semanaFinal = [None]*53
                
                if semana[semanaActual]==None:
                    semana[semanaActual] = float(t)
                else:
                    semana[semanaActual] += float(t)
                
                contador[semanaActual] += 1

        #Meter valores medios semanales del ultimo año
        for i in range(0,len(semana)):
            if semana[i] == None:
                semanaFinal[i] = None
            else:
                semanaFinal[i] = semana[i]/contador[i]
        semanal[str(anio)] = semanaFinal   
        df.append({'idEstacion': idEstacion, 'historico':aux, 'historico(semanal)': semanal})
        

text_file = open("data/historico1.json", "w")
n = text_file.write(json.dumps(df))
text_file.close()
j+=1
    
#records = df.to_dict(orient='records')

historico = db.historico
historico.delete_many({})
historico.insert_many(df)           
    




