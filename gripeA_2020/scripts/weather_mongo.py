import json
import sys
import requests
import re
import pandas as pd
import pymongo
from pymongo import MongoClient
from datetime import datetime, timedelta, date
import sys
import codecs

api_key='eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlbWlsaW92YUB1Y20uZXMiLCJqdGkiOiJiZDc2MzgzMS1hMWU4LTQ4MTktOTE2Yy1lYzQ5MjE2OTJiYjAiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTYwNjQ3NTk4NiwidXNlcklkIjoiYmQ3NjM4MzEtYTFlOC00ODE5LTkxNmMtZWM0OTIxNjkyYmIwIiwicm9sZSI6IiJ9.0Z3PqEjKyMFhUztyu2LAPV7zYPEaeh2RXndZQdryTrE'
api_key_tutiempo = "XwDqzzz4q4q748k"
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
estacion = db.estaciones
historico = db.historico
temperatura = db.temperatura
comarca = db.comarcas

headers = {
        'cache-control': "no-cache"
}

bisiesto = ["2012", "2016","2020","2024"]
fechaInicial = "2017-01-02"
fechaFinal = "2021-05-02"

semanaFinal = datetime.strptime(fechaFinal, '%Y-%m-%d')
nSemanaFinal = semanaFinal.isocalendar()[1]-1


estacionDebug = ""
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

        estacion.update_one({'comarca_sg':key},{"$set": {"estacionesAdd":p}})
#Listamos todas las estaciones y volcamos en formato excel
def listStacion():
    cursor = estacion.find({})
    df = pd.DataFrame(list(cursor))
    df.to_excel('data/estaciones.xlsx', index=False)

def responseApi(url, idEstacion):
#Extraemos la url donde esta la informacion de la consulta a la API
    response = requests.request("GET", url, headers=headers)
    json_response = response.json()

    if json_response['estado'] == 404:
        print("Descripcion error: {} para la estacion {}".format(json_response['descripcion'], idEstacion))
        return False
    elif response.status_code == 200 and json_response['estado'] == 200:
        #Extraemos la informacion de la API
        response = requests.request("GET", json_response['datos'], headers=headers)
        try:
            json_response = response.json()

            #Extraemos la url donde esta la informacion de la consulta a la API
            response = requests.request("GET", url, headers=headers)
        
            json_response = response.json()

            #Extraemos la informacion de la API
            response = requests.request("GET", json_response['datos'], headers=headers)

            json_response = response.json()
        except:
            print(response)
            return False
    
    return json_response
    


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
        url_valoresDiarios = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{}/fechafin/{}/estacion/{}/?api_key={}".format(fechaini, fechafin,idEstacion,api_key)
        
        json_response = responseApi(url_valoresDiarios, idEstacion)
        if json_response == False:
            continue

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

        #Relleno años vacios del array de booleanos
        anio += 1
        while anio <= 2021:
            completo[str(anio)] = [*range(0,len(semana))]
            anio += 1

        df.append({'idEstacion': idEstacion, 'historico(semanal)': semanal, 'boolCompleto': completo})
        

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


    text_file = open("data/emptyCG-IDE.json", "w")
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
        
        estacionDebug = it['comarca_sg']
        if valor == []:#Si la estacion principal no tiene datos se busca la siguiente más cercana
            aux = []
            i = 1
            while aux == []:
                aux = list(historico.find({'idEstacion': it['estacionesAdd'][i]}, {'_id':False, 'historico(semanal)':True,'boolCompleto': True}))
                i +=1

            his, comp = fillEmptyWeeks(aux[0]['historico(semanal)'], aux[0]['boolCompleto'], it['estacionesAdd'], it['comarca_sg'], i)
        else:
            his, comp = fillEmptyWeeks(valor[0]['historico(semanal)'], valor[0]['boolCompleto'], it['estacionesAdd'], it['comarca_sg'], 1)

        df.append({'comarca_sg': it['comarca_sg'], 'historicoFinal': his })

    temperatura.delete_many({})
    temperatura.insert_many(df) 

#His -> diccionario por años con las temperaturas
#BooleanArray -> diccionario por posiciones donde hay semanas vacias
#RestoEstaciones -> Diferentes estaciones para aplicar recursion buscando ese valor perdido
#index -> indice de la lista de RestoEstaciones

def fillEmptyWeeks(his, booleanArray, restoEstaciones, comarca, index):
    aux = his
    auxBoolean = {'2017':[], '2018':[], '2019':[], '2020':[], '2021':[]}
    for anio, lista in booleanArray.items():
        i = 0
       
        for semana in lista:
            indice = index
            if semana == 52 and anio not in bisiesto: #Solo acceder a la semana 52 de años bisiestos
                continue

            if (str(semanaFinal.year)) !=  anio or (semana < nSemanaFinal):
                aux[anio][semana] = search(anio,restoEstaciones, indice, comarca, semana)
                if aux[anio][semana] == None: #Lo eliminamos de la lista
                    auxBoolean[anio].append(i)

            i+=1

    return aux, auxBoolean
    
def search(anio, restoEstaciones, index, comarca, semana):
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

def firstPrediction():

    #Sacamos la prediccion de las comarcas
    cursor = comarca.find({})

    for it in cursor:
        latitud = it["Latitud"]
        longitud = it["Longitud"]
        url = "https://api.tutiempo.net/json/?lan=es&apid={}&ll={},{}".format(api_key_tutiempo,latitud,longitud)
       
        #Si la consulta no da ningun valor, guardamos en el diccionario y le damos un valor de None para no volver a buscar 
        response = requests.request("GET", url, headers=headers)
        json_response = response.json()
        #Comprobamos si existe un error

        if "error" in json_response: 
            continue
            
        #Calculamos la media de la prediccion
        avgPredict = 0
        for i in range(1,8):
            avgPredict += json_response["day{}".format(i)]['temperature_min']

        avgPredict = avgPredict/7

        #Guardamos la media de la prediccion
        temperatura.update_one({"comarca_sg": it['comarca_sg']}, {"$set": {"prediccion": avgPredict}})
           
def secondPrediction(value):
    cursor = temperatura.find({"prediccion":{"$exists": False}})
   
    #Sacamos coordenadas estacion para la predicción 
    dEstacion = dict()
    file = "data/estaciones.json"
    listaEstaciones = pd.read_json(file)
    listaEstaciones.set_index("indicativo",inplace = True)
    cont = 0
    for it in cursor:
        cursor = list(estacion.find({"comarca_sg": it['comarca_sg']}))
        estacionList = cursor[0]['estacionesAdd']
        ok = False
        i = 0
        # if it["comarca_sg"] ==  "SP37046":
        #     print(1)
        while not ok and i < len(estacionList):
            #Si ya existe en el diccionario, no accedemos a la api
            auxStation = estacionList[i]
            #Aumentamos contador
            i+=1
            if auxStation in dEstacion:
                #Si el valor es None, pasamos a la siguiente estación
                if dEstacion[auxStation] == None:
                    continue

                temperatura.update_one({"comarca_sg": it['comarca_sg']}, {"$set": {"prediccion": dEstacion[auxStation]}})
                ok = True
                continue
            
            indice = listaEstaciones.index.get_loc(auxStation)

            if value == "mongo":
                latitud = cursor[0]["latitud_D"]
                longitud = cursor[0]["longitud_D"]
            else:
                latitud = changeCoordenates(listaEstaciones["latitud"][indice])
                longitud = changeCoordenates(listaEstaciones["longitud"][indice])

            


            url = "https://api.tutiempo.net/json/?lan=es&apid={}&ll={},{}".format(api_key_tutiempo,latitud,longitud)

            #Si la consulta no da ningun valor, guardamos en el diccionario y le damos un valor de None para no volver a buscar 
            response = requests.request("GET", url, headers=headers)
            json_response = response.json()
            #Comprobamos si existe un error

            if "error" in json_response: 
                dEstacion[auxStation] = None
                cont += 1
                continue
            
            #Calculamos la media de la prediccion
            avgPredict = 0
            for i in range(1,8):
                avgPredict += json_response["day{}".format(i)]['temperature_min']

            avgPredict = avgPredict/7

            #Guardamos la media de la prediccion
            temperatura.update_one({"comarca_sg": it['comarca_sg']}, {"$set": {"prediccion": avgPredict}})
            dEstacion[auxStation] = avgPredict
            #Actualizamos variables
            ok = True
    
def changeCoordenates(coordenada):
    D = int(coordenada[0:2]) 
    M = int(coordenada[2:4]) 
    S = int(coordenada[4:6]) 
    
    DD = D + float(M)/60 + float(S)/3600 
    
    return DD

def thirdPrediction(parametro):
    cursor = temperatura.find({"prediccion":{"$exists": False}})
    
    for it in cursor:
        #Contadores a 0
        cont = 0
        prediccionTotal = 0

        #Sacamos de comarcas la provincia
        comarcaResult = list(comarca.find({"comarca_sg": it['comarca_sg']}))
        #Buscamos comarcas con la misma provincia
        provinciaResult = comarca.find({parametro: comarcaResult[0][parametro]})
        
        for it2 in provinciaResult:
            #Buscamos en la coleccion temperatura si tiene valor de prediccion
            provinciaPre = list(temperatura.find({'comarca_sg': it2['comarca_sg']}))
            #Si existe valor salimos 
            if provinciaPre != [] and ("prediccion" in provinciaPre[0]):
                prediccionTotal += provinciaPre[0]['prediccion']
                cont+=1
        
        #MediaTotal
        prediccionTotal = prediccionTotal/cont
        #Guardado en Mongo
        temperatura.update_one({"comarca_sg": it['comarca_sg']}, {"$set": {"prediccion": prediccionTotal}})

def prediction():
    #Busqueda por coordenadas centroides comarcas
    firstPrediction()
    #Busqueda por coordenadas comarca en estaciones  
    secondPrediction("mongo")
    #Busqueda por coordenadas estaciones más cercanas
    secondPrediction("listaE")
    #Prediccion provincia o comunidad autonoma
    thirdPrediction("provincia")
    thirdPrediction("comAutonoma")

#Para las estaciones que en la consulta para la semana x no haya tenido valor, rellenamos
def fillEmptyInfoCron(semana, anio):
    #Insercion en una coleccion Comarca - Historico (Juntando varias estaciones)
    cursor = estacion.find({})

    #Recorremos todas las estaciones
    for it in cursor:
        estaHis = list(historico.find({"idEstacion": it['indicativo']}))

        tMin = None if (estaHis == []) else estaHis[0]["historico(semanal)"][str(anio)][semana]

        #Si no hay Tmin en la estación principal buscamos el valor en el resto de estaciones
        if tMin == None:
            tMin = search(str(anio), it['estacionesAdd'], 1, it['comarca_sg'], semana)
        
        temperatura.update_one({"comarca_sg": it['comarca_sg']}, {"$set":{"historicoFinal.{}.{}".format(str(anio), semana): tMin}})

        

def cronTemp():
    #Lunes y domingo semana pasada
    start = date.today() - timedelta(days = 1)
    start = start + timedelta(days = -date.today().weekday())
    end = start + timedelta(days = 6)
    #Convert to datetime
    start = datetime.combine(start, datetime.min.time())
    end = datetime.combine(end, datetime.min.time())
    #Semana y anio 
    semanaM = start.isocalendar()[1]-1
    anioM = start.year
    #Datetime to string
    start = datetime.strftime(start, '%Y-%m-%d')
    end = datetime.strftime(end, '%Y-%m-%d')
    #Fecha para url
    fechaini = "{}T00:00:00UTC".format(start)
    fechafin = "{}T00:00:00UTC".format(end)

    #Indicativos
    cursor = estacion.find({},{'indicativo':True, '_id':False}).distinct('indicativo')

    indicativos = list(cursor)

    for idEstacion in indicativos: #Recorremos la lista
        minTotal = 0
        cont = 0 

        #Url para valores diarios YYYY-MM-DDTHH:MM:SSUTC
        url_valoresDiarios = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{}/fechafin/{}/estacion/{}/?api_key={}".format(fechaini, fechafin,idEstacion,api_key)
        
        json_response = responseApi(url_valoresDiarios, idEstacion)

        if json_response == False:
            continue

        for api in json_response:
            if 'tmin' in api:
                t = ""
                for l, caracter in enumerate(api['tmin']): #Cambiar formato de la temperatura
                    t += '.' if (caracter == ',') else caracter

                minTotal += float(t)
                cont+=1

        if cont > 0:
            minTotal = minTotal / cont
            #Actualizar en historico -> historico(semanal) y boolCompleto
            historico.update_one({"idEstacion": idEstacion}, {"$set":{"historico(semanal).{}.{}".format(anioM, semanaM): minTotal}})
            historico.update_one({"idEstacion": idEstacion}, {"$pull":{"boolCompleto.{}".format(anioM): semanaM}})

    #Rellenar las semanas vacias
    fillEmptyInfoCron(semanaM, anioM)




def main(argv):
    #estaciones() #Construye la coleccion de estaciones
    #listStacion()

    #generateListEmpty()
    #generateHistoric()
    #fillEmptyInfo()

    #Borrar campo prediccion de todos los documentos
    #temperatura.update_many({}, {"$unset": {"prediccion":1}})
    #temperatura.update_one({"idEstacion":"0002I"}, {"$pull":{"historicoFinal.2021": 8.8}})
    #Actualización diaria 
    cronTemp()
    #Prediccion
    prediction()

    return 0

if __name__ == "__main__":
    main(sys.argv[1:])