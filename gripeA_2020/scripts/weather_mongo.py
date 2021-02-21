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
h = db.historico
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

df = list()
#url para valores mensuales
#url_mensualAnual = "https://opendata.aemet.es/opendata/api/valores/climatologicos/mensualesanuales/datos/anioini/2020/aniofin/2020/estacion/0252D/?api_key={}".format(api_key)
j=1
#Solo rango de 5 años 

#Valores para la URL
#fechaini = "{}-01-01T00:00:00UTC".format(i)
#fechafin = "{}-12-31T00:00:00UTC".format(i)


#2017-2021
fechaini = "2017-01-01T00:00:00UTC"
fechafin = "2020-12-31T00:00:00UTC"

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
 
        #Tmin, fecha
        aux = {}
        semanal = {"2017": [], "2018": [], "2019":[], "2020":[]}
        bisiesto = [2016,2020]#Años bisiestos
        cont = 1 #Semana
        media = 0 #Media semanal
        semana1= 0
        semana2= 0
        semana3= 0
        semana4= 0
        semana5= 0
        cont1= 0
        cont2= 0
        cont3= 0
        cont4= 0 
        cont5= 0
        meses31 = [1,3,5,7,8,10,12] #Meses con 31 dias
        meses30 = [4,6,9,11] #Meses con 30 dias
        mesAnterior = 1
        anio = 2017 
        for api in json_response:

            
            if 'tmin' in api:
                
                t = ""
                for l, caracter in enumerate(api['tmin']): #Cambiar formato de la temperatura
                    t += '.' if (caracter == ',') else caracter

                #fecha_dt = datetime.strptime(api['fecha'], '%Y-%m-%d')
                #aux[fecha_dt] = float(t)
                aux[api['fecha']] = float(t)


                fecha_dt = datetime.strptime(api['fecha'], '%Y-%m-%d')

                #Boolenaos para comprobar fin de mes
                booleanBisiesto = True if (fecha_dt.year in bisiesto) else False
                boolean31 = True if (fecha_dt.month in meses31) else False
                boolean30 = True if (fecha_dt.month in meses30) else False

                #Fin (booleano que indica si se ha terminado un mes)
                fin = False
                #media+=float(t)
                #3 CASOS
                #Fin de mes - OK
                # No fin de mes - Se termina el mes y se añade cuando los contadores estan a 0
                #    Meses vacios OK
                # No fin de mes pero pasa de año 
                # Ejemplo: mesAnterior 25 de diciembre Fecha actual 2 de enero
            
                #Es fin de mes y el mes de la fecha anterior no coincide con la actual, lo metemos a la bbdd
                if (boolean31 and fecha_dt.day == 31) or (boolean30 and fecha_dt.day == 30)  or (fecha_dt.month == 2 and fecha_dt.day == 29) or (fecha_dt.month == 2 and fecha_dt.day == 28 and not booleanBisiesto ) or (fecha_dt.month != mesAnterior ): 
                    #Añadimos el ultimo si es fin de mes
                    if fecha_dt.month == mesAnterior: #Caso normal
                        if fecha_dt.day <= 7:
                            semana1 += float(t)
                            cont1+=1
                        elif fecha_dt.day > 7 and fecha_dt.day <= 14:
                            semana2 += float(t)
                            cont2+=1
                        elif fecha_dt.day > 14 and fecha_dt.day <= 21:
                            semana3 += float(t)
                            cont3+=1
                        elif fecha_dt.day > 21 and fecha_dt.day <= 28:
                            semana4 += float(t)
                            cont4+=1
                        else:
                            semana5 += float(t)
                            cont5+=1
                        
                        #Se almacena en el diccionario
                        if cont1 != 0:
                            semanal[str(fecha_dt.year)].append(semana1/cont1)
                        else: 
                            semanal[str(fecha_dt.year)].append(None)
                        
                        if cont2 != 0:
                            semanal[str(fecha_dt.year)].append(semana2/cont2)
                        else: 
                            semanal[str(fecha_dt.year)].append(None)
                        
                        if cont3 != 0:
                            semanal[str(fecha_dt.year)].append(semana3/cont3)
                        else: 
                            semanal[str(fecha_dt.year)].append(None)
                        
                        if cont4 != 0:
                            semanal[str(fecha_dt.year)].append(semana4/cont4)
                        else: 
                            semanal[str(fecha_dt.year)].append(None)
                        
                        if cont5 != 0:
                            semanal[str(fecha_dt.year)].append(semana5/cont5)
                        else: 
                            semanal[str(fecha_dt.year)].append(None)
                        
                        #Reiniciamos contadores
                        semana1= 0
                        semana2= 0
                        semana3= 0
                        semana4= 0
                        semana5= 0
                        cont1= 0
                        cont2= 0
                        cont3= 0
                        cont4= 0 
                        cont5= 0

                        #Mes anterior actualizado
                        mesAnterior = 1 if (mesAnterior == 12) else mesAnterior + 1
                        if mesAnterior == 1:
                            anio += 1

                        fin = True
                        continue
                    else:
                        #3 casos
                        #Mes siguiente sin finalizar el anterior
                        #Mes siguiente fin de año
                        #Se añade al dataframe las semanas
                        i = 0
                        #En caso de que haya un mes sin datos se rellena de None
                        
                        if fecha_dt.year != anio: 
                            iterar = (12 - mesAnterior) + fecha_dt.month
                        else:
                            iterar = fecha_dt.month - mesAnterior

                         
                        for i in range(iterar):
    
                            #Se almacena en el diccionario
                            if cont1 != 0:
                                semanal[str(anio)].append(semana1/cont1)
                            else: 
                                semanal[str(anio)].append(None)
                            
                            if cont2 != 0:
                                semanal[str(anio)].append(semana2/cont2)
                            else: 
                                semanal[str(anio)].append(None)
                            
                            if cont3 != 0:
                                semanal[str(anio)].append(semana3/cont3)
                            else: 
                                semanal[str(anio)].append(None)
                            
                            if cont4 != 0:
                                semanal[str(anio)].append(semana4/cont4)
                            else: 
                                semanal[str(anio)].append(None)
                            
                            if cont5 != 0:
                                semanal[str(anio)].append(semana5/cont5)
                            else: 
                                semanal[str(anio)].append(None)
                            
                            #Reiniciamos contadores
                            semana1= 0
                            semana2= 0
                            semana3= 0
                            semana4= 0
                            semana5= 0
                            cont1= 0
                            cont2= 0
                            cont3= 0
                            cont4= 0 
                            cont5= 0

                            mesAnterior = 1 if (mesAnterior == 12) else mesAnterior + 1
                            if mesAnterior == 1:
                                anio += 1
                            fin = True
                            
                                   
                    #Fecha entrante añadida a la semana correspondiente
                if fecha_dt.day <= 7:
                    semana1 += float(t)
                    cont1+=1
                elif fecha_dt.day > 7 and fecha_dt.day <= 14:
                    semana2 += float(t)
                    cont2+=1
                elif fecha_dt.day > 14 and fecha_dt.day <= 21:
                    semana3 += float(t)
                    cont3+=1
                elif fecha_dt.day > 21 and fecha_dt.day <= 28:
                    semana4 += float(t)
                    cont4+=1
                else:
                    semana5 += float(t)
                    cont5+=1
            
                #Primero comprobamos fin de mes
                '''if (boolean31 and fecha_dt.day == 31) or (boolean30 and fecha_dt.day == 30)  or (fecha_dt.month == 2 and fecha_dt.day == 29) or (fecha_dt.month == 2 and fecha_dt.day == 28 and not booleanBisiesto ): 
                    semanal[fecha_dt.year].append(media/cont)
                    cont = 1
                    media = 0
                else:
                    if cont < 7: 
                        cont+=1
                    else:
                        semanal[fecha_dt.year].append(media/7)
                        cont = 1
                        media = 0
                '''
        
        if not fin:
            if cont1 != 0:
                semanal[str(fecha_dt.year)].append(semana1/cont1)
            else: 
                semanal[str(fecha_dt.year)].append(None)
            
            if cont2 != 0:
                semanal[str(fecha_dt.year)].append(semana2/cont2)
            else: 
                semanal[str(fecha_dt.year)].append(None)
            
            if cont3 != 0:
                semanal[str(fecha_dt.year)].append(semana3/cont3)
            else: 
                semanal[str(fecha_dt.year)].append(None)
            
            if cont4 != 0:
                semanal[str(fecha_dt.year)].append(semana4/cont4)
            else: 
                semanal[str(fecha_dt.year)].append(None)
            
            if cont5 != 0:
                semanal[str(fecha_dt.year)].append(semana5/cont5)
            else: 
                semanal[str(fecha_dt.year)].append(None)
        
       #Estación -> historico
        df.append({'idEstacion': idEstacion, 'historico':aux, 'historico(semanal)': semanal})
        

text_file = open("historico1.json", "w")
n = text_file.write(json.dumps(df))
text_file.close()
j+=1
    
#records = df.to_dict(orient='records')

historico = db.historico
historico.delete_many({})
historico.insert_many(df)           
    




