# import requests
# import re
import sys
# import time
import json
# import pymongo
from pymongo import MongoClient
# import pygeohash as geohash
from datetime import datetime, timedelta, date
import math
from neo4j import GraphDatabase
# import string



# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
brotes_db = db.outbreaks
# migrations = db.migrations
comarcas_db = db.comarcas
# especie = db.especies

diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}

# Driver de neo4j user neo4j y contraseña 1234
# TODO
neo4j_db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))


def genera_brotes(listaBrotes):

    feat_col_brote = {
        "type": "FeatureCollection",
        "features": []
    }

    lista = brotes_db.find({})

    for it in lista:
        aux = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(it['long']), float(it['lat'])]
                },
                "properties": {
                    "id": it['oieid'],
                    "disease": diseases[it['disease_id']],
                    "country": it['country'],
                    "start": math.floor(it['start'].timestamp() * 1000),
                    # "end": "" if it['end'] == "" else math.floor(it['end'].timestamp() * 1000),
                    "city": it['city'],
                    # "species": it['species'],
                    # "at_risk": int(it['at_risk']),
                    # "cases": int(it['cases']),
                    # "deaths": int(it['deaths']),
                    # "preventive_killed": int(it['preventive_killed'])
                    "serotipo": it['serotype'],
                    "moreInfo": it['urlFR'],
                    "epiUnit": it['epiunit'],
                    "reportDate": math.floor(it['report_date'].timestamp() * 1000)
                }
            }

        feat_col_brote['features'].append(aux)

    return feat_col_brote

def genera_migraciones(listaMigraciones):

    feat_col_migracion = {
        "type": "FeatureCollection",
        "features": []
    }

    for it in lista:
        aux = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(it['long']), float(it['lat'])]
                },
                "properties": {
                    "id": it['oieid'],
                    "disease": diseases[it['disease_id']],
                    "country": it['country'],
                    "start": math.floor(it['start'].timestamp() * 1000),
                    # "end": "" if it['end'] == "" else math.floor(it['end'].timestamp() * 1000),
                    "city": it['city'],
                    # "species": it['species'],
                    # "at_risk": int(it['at_risk']),
                    # "cases": int(it['cases']),
                    # "deaths": int(it['deaths']),
                    # "preventive_killed": int(it['preventive_killed'])
                    "serotipo": it['serotype'],
                    "moreInfo": it['urlFR'],
                    "epiUnit": it['epiunit'],
                    "reportDate": math.floor(it['report_date'].timestamp() * 1000)
                }
            }

        feat_col_migracion['features'].append(aux)

    return feat_col_migracion


def genera_alerta(nivelesAlerta, todasComarcas):

    feat_col_alertas = {
        "type": "FeatureCollection",
        "features": []
    }

    cursor = com.find({})

    for it in cursor:
        if it['comarca_sg'] in alertaComarcaRiesgo:
            brote = list(outbreaks.find({"oieid": alertaComarcasGeo[it['comarca_sg']][0]['oieid']}))
            especieFind = list(especie.find({"codigo anilla": alertaComarcasGeo[it['comarca_sg']][0]['especie']}))
            print(alertaComarcaRiesgo[it['comarca_sg']])
            feat_com={
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(it['Longitud']), float(it['Latitud'])]
                },
                "properties": {
                    "id": it['comarca_sg'], #Será el id de comarca
                    "riskLevel": alertaComarcaRiesgo[it['comarca_sg']],
                    "number_of_cases": brote[0]['affected_population'],

                    "species": brote[0]['species'],
                    "commonName": especie[0]['Nombre común'],
                    "fluSubtype": brote[0]['serotype'],
                    "comarca_sg": it['comarca_sg'],
                    "comarca": it['com_sgsa_n'],
                    #"CMUN": it['CPROyMUN'][-2:],
                    #"municipality": "Vitoria-Gasteiz",
                    "CPRO": it['CPRO'],
                    #"province": it['provincia'],
                    #"CODAUTO": it['CODAUTO'],
                    #"CA": it['comAutonoma'],
                    "CPROyMUN": it['CPROyMUN']   
                }
            }
            feat_col_alertas["features"].append(feat_com)

            return feat_col_alertas

def main(argv):

    # Variables del programa
    TAM_GEO_ESP = 4
    LAST_N_DAYS = 90

    # El esquema:
    #     - En la base de datos de brotes buscar los que esten dentro del marco de tiempo de N dias
    #     - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
    #         + Si hay un nodo, se miran todos los demas nodos asociados a este.
    #     - Con los nodos relacionados con brote miramos en tablaGeoComarca a ver si hay alguna comarca asociada a estos geohash.
    #     - Con esto ya tendriamos comarcas y brotes asociados por una ruta (la migracion)

    # - En la base de datos de brotes buscar los que esten dentro del marco de tiempo de N dias
    today = date.today()
    fecha = datetime.now() + timedelta(days = -today.weekday())
    mas_antiguo = fecha - timedelta(days = LAST_N_DAYS)

    listaBrotes = brotes_db.find({"report_date" : {"$gte" : mas_antiguo}})

    # - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
    #     + Si hay un nodo, se miran todos los demas nodos asociados a este y lo guardamos si alguno de los nodos asociados esta en España

    destinosAvesInfectadas = dict()
    setComarcas = set()
    setBrotes = set()
    tablaGeoComarca = json.load(open("data/tablaGeoComarca.txt",  encoding='utf-8'))

    for brote in listaBrotes:
        geo_del_brote = brote['geohash'][0:4]

        response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie'.format(geo_del_brote)).values()

        # relacion
        # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
        # ej: ['sp0j', 1470]
        for relacion in response:
            if brote['oieid'] not in destinosAvesInfectadas:
                destinosAvesInfectadas[brote['oieid']] = [relacion]
            else:
                destinosAvesInfectadas[brote['oieid']].append(relacion)

    # - Con los nodos relacionados con brote miramos en tablaGeoComarca a ver si hay alguna comarca asociada a estos geohash.
    comarcaBrotes = dict()
    migraciones = dict()

    for brote in destinosAvesInfectadas:
        for destino in destinosAvesInfectadas[brote]:

            if destino[0] in tablaGeoComarca:
                for comarca in tablaGeoComarca[destino[0]]:
                    if comarca['cod_comarca'] not in comarcaBrotes:
                        comarcaBrotes[comarca['cod_comarca']] = {brote}
                    else:
                        comarcaBrotes[comarca['cod_comarca']].add(brote)

    # Según los datos calcular las comarcaBrotes
    comarcaBrotes_sorted = sorted(comarcaBrotes, key=lambda k: len(comarcaBrotes[k]), reverse=True)
    alertas = dict()

    # Cuartiles
    alertaMax = 5
    porcentaje = 0.2
    percentil = math.ceil(len(comarcaBrotes_sorted) * porcentaje)
    cont = 1
    for comarca in comarcaBrotes_sorted:
        alertas[comarca] = alertaMax

        if cont == percentil:
            alertaMax -= 1
            porcentaje += 0.2
            percentil = math.ceil(len(comarcaBrotes_sorted) * porcentaje)

        cont += 1

    comarcas = comarcas_db.find({})


    # - Con esto ya tendriamos comarcas y brotes asociados por una ruta (la migracion)
    feat_col_brote = genera_brotes(list(setBrotes))
    feat_col_migra = genera_migraciones(list(comarcaBrotes))
    feat_col_alerta = genera_alertas(list(), comarcas)

    pass

    return 0





if __name__ == "__main__":
    main(sys.argv[1:])