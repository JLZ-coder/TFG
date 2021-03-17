import json
import sys
import requests
import re
import pandas as pd
import dbf
#from aemet import *
import pymongo
from pymongo import MongoClient
from datetime import datetime
import sys

api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YWxlbmNpYWJhcmNlbG9uYUBnbWFpbC5jb20iLCJqdGkiOiJiYzY4MzM1Mi1kZjg3LTRlZTctYjQ4MS1hMDMyODQzZGMwMWIiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYxMDM4OTY0OCwidXNlcklkIjoiYmM2ODMzNTItZGY4Ny00ZWU3LWI0ODEtYTAzMjg0M2RjMDFiIiwicm9sZSI6IiJ9.BanUHViE2mFsnjne_ilriezZqkDRYYT3Vf4SkKOcE04'
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
estacion = db.estaciones
historico = db.historico
temperatura = db.temperatura

bisiesto = ["2012", "2016","2020","2024"]
fechaInicial = "2017-01-02"
fechaFinal = "2021-03-8"

semanaFinal = datetime.strptime(fechaFinal, '%Y-%m-%d')
nSemanaFinal = semanaFinal.isocalendar()[1]-1
#Creamos la colección que guardará la información relacionada con las estaciones
def estaciones():
    #Leemos el fichero que relaciona las estaciones con las comarcas
    file = "aemet/CG_estaciones.xlsx"
    df = pd.read_excel(file)

    #Insertamos la relacion de estaciones con comarcas en mongoDB
    records = df.to_dict(orient='records')
    estacion.delete_many({})
    estacion.insert_many(records)
    #Insercion de los datos en la base de datos
    file = "data/DistanciasCG_estaciones_200km.xlsx"
    df = pd.read_excel(file)
    df = df.groupby('Codigo_comarca')

    for key, item in df:
        p = df.get_group(key)
        #Eliminamos repetidos manteniendo el orden
        d = dict()
        for i in p['Estacion_cod']:
            if i not in d:
                d.setdefault(i,i) 

        p = list(d.keys())

        estacion.update({'comarca_sg':key},{"$set": {"estacionesAdd":p}})
#Listamos todas las estaciones y volcamos en formato excel
def listStacion():
    cursor = estacion.find({})
    df = pd.DataFrame(list(cursor))
    df.to_excel('data/estaciones.xlsx', index=False)
#Accedemos a la API
def generateHistoric():
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
    
    #2017-2021
    fechaini = "{}T00:00:00UTC".format(fechaInicial)
    fechafin = "{}T00:00:00UTC".format(fechaFinal)

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
            #Lista por año para saber que semanas no tienen valores
            completo = {'2017':[], '2018':[], '2019':[], '2020':[], '2021':[]}
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
                                completo[str(anio)].append(i)
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
                    completo[str(anio)].append(i)
                else:
                    semanaFinal[i] = semana[i]/contador[i]
            semanal[str(anio)] = semanaFinal   
            df.append({'idEstacion': idEstacion, 'historico':aux, 'historico(semanal)': semanal, 'boolCompleto': completo})
            

    text_file = open("data/historico1.json", "w")
    n = text_file.write(json.dumps(df))
    text_file.close()
    j+=1
        
    #records = df.to_dict(orient='records')
    historico.delete_many({})
    historico.insert_many(df) 
#Generamos lista de comarcas sin datos
def generateListEmpty():
    #Extraemos los indicativos de todas las estaciones
    cursor = estacion.find({},{'indicativo':True, '_id':False}).distinct('indicativo')

    indicativos = list(cursor)
    headers = {
        'cache-control': "no-cache"
    }

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
#Para comarcas sin asignación alguna
def fillEmptyInfo():
    #Insercion en una coleccion Comarca - Historico (Juntando varias estaciones)
    estaciones = estacion.find({})
    #Comarca->Historico
    df = []

    for it in estaciones:
        valor = list(historico.find({'idEstacion': it['indicativo']}, {'_id':False, 'historico(semanal)':True, 'boolCompleto': True}))
        
        if valor == []:#Si la estacion principal no tiene datos se busca la siguiente más cercana
            aux = []
            i = 1
            while aux == []:
                aux = list(historico.find({'idEstacion': it['estacionesAdd'][i]}, {'_id':False, 'historico(semanal)':True,'boolCompleto': True}))
                i +=1

            his, comp = fillEmptyWeeks(aux[0]['historico(semanal)'], aux[0]['boolCompleto'], it['estacionesAdd'], i)
        else:
            his, comp = fillEmptyWeeks(valor[0]['historico(semanal)'], valor[0]['boolCompleto'], it['estacionesAdd'], 1)

        df.append({'comarca_sg': it['comarca_sg'], 'historicoFinal': his, 'completo': comp })

    temperatura.delete_many({})
    temperatura.insert_many(df) 

#His -> diccionario por años con las temperaturas
#BooleanArray -> diccionario por posiciones donde hay semanas vacias
#RestoEstaciones -> Diferentes estaciones para aplicar recursion buscando ese valor perdido
#index -> indice de la lista de RestoEstaciones

def fillEmptyWeeks(his, booleanArray, restoEstaciones, index):
    aux = his
    auxBoolean = booleanArray
    for anio, lista in booleanArray.items():
        i = 0
        for semana in lista:
            indice = index
            if semana == 52 and anio not in bisiesto: #Solo acceder a la semana 52 de años bisiestos
                continue

            if (str(semanaFinal.year)) !=  anio or (semana < nSemanaFinal):
                aux[anio][semana] = search(anio,restoEstaciones, indice, semana)
                if aux[anio][semana] != None: #Lo eliminamos de la lista
                    auxBoolean[anio].pop(i)

            i+=1

    return aux, auxBoolean
    
def search(anio, restoEstaciones, index, semana):
    resulta = None
    ok = False
    i = index
    
    while not ok and i < len(restoEstaciones):
        consulta = list(historico.find({'idEstacion': restoEstaciones[i]}, {'_id':False, 'historico(semanal)':True}))
        if consulta != []:
            if consulta[0]['historico(semanal)'][anio][semana] != None: 
                resulta = consulta[0]['historico(semanal)'][anio][semana]
                ok = True
        i+=1

    return resulta


def main(argv):
    #estaciones() #Construye la coleccion de estaciones
    #listStacion()
    #generateListEmpty()
    #generateHistoric()
    fillEmptyInfo()

    return 0         



if __name__ == "__main__":
    main(sys.argv[1:])