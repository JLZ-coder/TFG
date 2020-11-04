import json
import os
import pymongo
from pymongo import MongoClient

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
comarca = db.comarcas

def coordinatesFunc(df):

    
    #Extraccion de los cuatro rectangulos
    cursor = comarca.find()

    izqI = []
    izqS = []
    derI = []
    derS = []

    for it in cursor:
        coordenadas = it['coordinates']
        aux = 0
    
        for i in range(len(coordenadas)):
            if aux == 0: #Solo inicializa una vez
                if len(coordenadas[i][0]) > 3: 
                    minX = coordenadas[i][0][0][0] #Inicializo los puntos cuando hay un array dentro de un array
                    maxX = coordenadas[i][0][0][0]
                    minY = coordenadas[i][0][0][1]
                    maxY = coordenadas[i][0][0][1]
                else: 
                    minX = coordenadas[i][0][0] #Inicializo los puntos 
                    maxX = coordenadas[i][0][0]
                    minY = coordenadas[i][0][1]
                    maxY = coordenadas[i][0][1]

            for j in range(len(coordenadas[i])):

                if len(coordenadas[i][j]) > 3:
                    for k in range(len(coordenadas[i][j])):
                        if coordenadas[i][j][k][0] < minX:
                            minX = coordenadas[i][j][k][0]
                        elif coordenadas[i][j][k][0] > maxX:
                            maxX = coordenadas[i][j][k][0]
                        
                        if coordenadas[i][j][k][1] < minY:
                            minY = coordenadas[i][j][k][1]
                        elif coordenadas[i][j][k][1] > maxY:
                            maxY = coordenadas[i][j][k][1] 
                else:
                    if coordenadas[i][j][0] < minX:
                        minX = coordenadas[i][j][0]
                    elif coordenadas[i][j][0] > maxX:
                        maxX = coordenadas[i][j][0]
                    
                    if coordenadas[i][j][1] < minY:
                        minY = coordenadas[i][j][1]
                    elif coordenadas[i][j][1] > maxY:
                        maxY = coordenadas[i][j][1]
            aux = 1

        
        izqI.append([minX,minY]) #guardo los puntos en las listaas
        izqS.append([minX,maxY])
        derI.append([maxX,minY])
        derS.append([maxX,maxY])

    #se guardan las 4 listas en la base de datos

    cursor = comarca.find()
    df['izqI'] = izqI
    df['izqS'] = izqS
    df['derI'] = derI
    df['derS'] = derS

    return df




            
    

    #Carpeta destino

