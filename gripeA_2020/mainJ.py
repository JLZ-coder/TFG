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

from factories.Factory import Factory
from factories.OutbreakBuilder import OutbreakBuilder
from model.Quintile import Quintile
from controller.Controller import Controller


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


def genera_brotes_ultimosDias(last_days):

    feat_col_brote = {
        "type": "FeatureCollection",
        "features": []
    }

    today = date.today()
    fecha = datetime.now() + timedelta(days = -today.weekday())
    mas_antiguo = fecha - timedelta(days = last_days)

    lista = brotes_db.find({"report_date" : {"$gte" : mas_antiguo}})

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

def genera_brotes(listaBrotes):

    feat_col_brote = {
        "type": "FeatureCollection",
        "features": []
    }

    for it in listaBrotes:
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

    for it in listaMigraciones:

        comarca_long = listaMigraciones[it]["long"]
        comarca_lat = listaMigraciones[it]["lat"]
        for brote in listaMigraciones[it]["brotes"]:

            aux = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [float(comarca_long), float(comarca_lat), float(brote['long']), float(brote['lat'])]
                    },
                    "properties": {
                        "idBrote": brote['oieid'],
                        "idAlerta": it,
                        "idComarca": it
                    }
                }

            feat_col_migracion['features'].append(aux)

    return feat_col_migracion


def genera_alertas(listAlertas, comarcas):

    feat_col_alertas = {
        "type": "FeatureCollection",
        "features": []
    }

    i = 0
    while (i < len(alertas)):
        alertas = listAlertas[i]
        start = alertas["start"]
        end = alertas["end"]

        for it in comarcas:
            risk = 0

            if it['comarca_sg'] in alertas:
                risk = alertas[it['comarca_sg']]

            aux={
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(it['Longitud']), float(it['Latitud'])]
                },
                "properties": {
                    "id": it['comarca_sg'], #Será el id de comarca
                    "riskLevel": risk,
                    "number_of_cases": 0,
                    "startDate": start.timestamp() * 1000,
                    "endDate": end.timestamp() * 1000,
                    # "codeSpecies": 1840,
                    # "species": "Anas crecca",
                    # "commonName": "Pato cuchara",
                    # "fluSubtype": "H5",
                    "idComarca": it['comarca_sg'],
                    "comarca": it['com_sgsa_n'],
                    "CPRO": it['CPRO'],
                    "province": it['provincia'],
                    "CPROyMUN": it['CPROyMUN']
                }
            }
            feat_col_alertas["features"].append(aux)

    return feat_col_alertas

# def main(argv):

#     # Variables del programa
#     FRAME_N_DAYS = 365
#     TAM_GEO_ESP = 4
#     LAST_N_DAYS = 90

#     # El esquema:
#     #     - En la base de datos de brotes buscar los que esten dentro del marco de tiempo de N dias
#     #     - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
#     #         + Si hay un nodo, se miran todos los demas nodos asociados a este.
#     #     - Con los nodos relacionados con brote miramos en tablaGeoComarca a ver si hay alguna comarca asociada a estos geohash.
#     #     - Con esto ya tendriamos comarcas y brotes asociados por una ruta (la migracion)

#     # - En la base de datos de brotes buscar los que esten dentro del marco de tiempo de N dias
#     today = date.today()
#     fecha = date.today() + timedelta(days = -today.weekday())
#     fecha_fin = date.today() + timedelta(weeks = 1);

#     mas_antiguo = fecha - timedelta(days = FRAME_N_DAYS)
#     ultimos = fecha - timedelta(days = LAST_N_DAYS)
#     mas_antiguo = datetime.combine(mas_antiguo, datetime.min.time())
#     ultimos = datetime.combine(mas_antiguo, datetime.min.time())


#     semana_inicio = datetime.combine(fecha, datetime.min.time())
#     semana_fin = datetime.combine(fecha_fin, datetime.min.time())

#     listaBrotes_todo = brotes_db.find({"report_date" : {"$gte" : mas_antiguo}})
#     listaBrotes = brotes_db.find({"report_date" : {"$gte" : ultimos}})

#     # - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
#     #     + Si hay un nodo, se miran todos los demas nodos asociados a este y lo guardamos si alguno de los nodos asociados esta en España

#     tablaGeoComarca = json.load(open("data/tablaGeoComarca4.txt",  encoding='utf-8'))
#     comarca_brotes = {}

#     for brote in listaBrotes:
#         geo_del_brote = brote['geohash'][0:4]

#         response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie'.format(geo_del_brote)).values()

#         # relacion
#         # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
#         # ej: ['sp0j', 1470]
#         for relacion in response:
#             if relacion[0] in tablaGeoComarca:
#                 for comarca in tablaGeoComarca[relacion[0]]:
#                     cod = comarca["cod_comarca"]
#                     if cod not in comarca_brotes:
#                         comarca_brotes[cod] = [{"peso" : comarca["peso"], "oieid" : brote["oieid"], "datos" : brote}]
#                     else:
#                         comarca_brotes[cod].append({"peso" : comarca["peso"], "oieid" : brote["oieid"], "datos" : brote})

#     # - Con los nodos relacionados con brote miramos en tablaGeoComarca a ver si hay alguna comarca asociada a estos geohash.
#     migraciones = dict()

#     for brote in listaBrotes_todo:
#         geo_del_brote = brote['geohash'][0:4]

#         response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie'.format(geo_del_brote)).values()

#         # relacion
#         # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
#         # ej: ['sp0j', 1470]
#         for relacion in response:
#             if relacion[0] in tablaGeoComarca:
#                 for comarca in tablaGeoComarca[relacion[0]]:
#                     cod = comarca["cod_comarca"]
#                     long = comarca["long"]
#                     lat = comarca["lat"]
#                     if cod not in migraciones:
#                         migraciones[cod] = {"brotes" : [], "long" : 0, "lat" : 0}
#                         migraciones[cod]["brotes"] = [{"oieid" : brote["oieid"], "long" : brote["long"], "lat" : brote["lat"]}]
#                         migraciones[cod]["long"] = long
#                         migraciones[cod]["lat"] = lat
#                     else:
#                         migraciones[cod]["brotes"].append({"oieid" : brote["oieid"], "long" : brote["long"], "lat" : brote["lat"]})

#     # Según los datos calcular las comarcaBrotes
#     comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(comarca_brotes[k]), reverse=True)
#     alertas = dict()

#     # Cuartiles
#     alertaMax = 5
#     porcentaje = 0.2
#     percentil = math.ceil(len(comarca_brotes_sorted) * porcentaje)
#     cont = 1
#     for comarca in comarca_brotes_sorted:
#         alertas[comarca] = {"start" : semana_inicio, "end" : semana_fin, "nivel" : alertaMax}

#         if cont == percentil:
#             alertaMax -= 1
#             porcentaje += 0.2
#             percentil = math.ceil(len(comarca_brotes_sorted) * porcentaje)

#         cont += 1

#     comarcas = comarcas_db.find({})


#     # - Con esto ya tendriamos comarcas y brotes asociados por una ruta (la migracion)
#     feat_col_brote = genera_brotes_ultimosDias(365)
#     feat_col_alerta = genera_alertas(alertas, comarcas, semana_inicio, semana_fin)
#     feat_col_migra = genera_migraciones(migraciones)

#     pass

#     return 0

def main(argv):
    builderList = list()
    builderList.append(OutbreakBuilder())

    fact = Factory(builderList)

    model = Quintile(fact)

    control = Controller(model)

    listAlertas = control.run()


    today = date.today()
    fecha = date.today() + timedelta(days = -today.weekday())
    mas_antiguo = fecha - timedelta(days = FRAME_N_DAYS)
    mas_antiguo = datetime.combine(mas_antiguo, datetime.min.time())

    listaBrotes_todo = brotes_db.find({"report_date" : {"$gte" : mas_antiguo}})

    migraciones = dict()

    for brote in listaBrotes_todo:
        geo_del_brote = brote['geohash'][0:4]

        response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie'.format(geo_del_brote)).values()

        # relacion
        # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
        # ej: ['sp0j', 1470]
        for relacion in response:
            if relacion[0] in tablaGeoComarca:
                for comarca in tablaGeoComarca[relacion[0]]:
                    cod = comarca["cod_comarca"]
                    long = comarca["long"]
                    lat = comarca["lat"]
                    if cod not in migraciones:
                        migraciones[cod] = {"brotes" : [], "long" : 0, "lat" : 0}
                        migraciones[cod]["brotes"] = [{"oieid" : brote["oieid"], "long" : brote["long"], "lat" : brote["lat"]}]
                        migraciones[cod]["long"] = long
                        migraciones[cod]["lat"] = lat
                    else:
                        migraciones[cod]["brotes"].append({"oieid" : brote["oieid"], "long" : brote["long"], "lat" : brote["lat"]})

    feat_col_brote = genera_brotes_ultimosDias(365)
    feat_col_alerta = genera_alertas(listAlertas, comarcas)
    feat_col_migra = genera_migraciones(migraciones)
    return 0




if __name__ == "__main__":
    main(sys.argv[1:])