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
outbreaks = db.outbreaks
# migrations = db.migrations
# com = db.comarcas
# especie = db.especies

diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}

# Driver de neo4j user neo4j y contraseña 1234
# TODO
neo4j_db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

# Devuelve routes que es un diccionario tipo "eqty"(geohash de españa) : [ {"geoBrote" : etyq, "especie" : 1470}, {"geoBrote" : ...}, ... ]
# geoEsp: Lista de nodos de los que se quiere buscar sus nodos asociados
# TODO
# TAM_GEO_BROT (4 o 5): Tamaño de los geohashes que se quieren devolver
def get_routes(geoESP, TAM_GEO_BROT): 

    routes = dict()
    routes_reverse = dict()

    for geo in geoESP:
        response = neo4j_db.session().run('MATCH (n:Region)-[r]-(x:Region) WHERE n.location starts with "{}" RETURN x.location, r.especie'.format(geo)).values()

        for r in response:
            if r[0][0:4] not in routes_reverse:
                routes_reverse[r[0][0:4]] = [{"geoEsp" : geo, "especie" : r[1]}]
            else:
                routes_reverse[r[0][0:4]].append({"geoEsp" : geo, "especie" : r[1]})

            if geo not in routes:
                routes[geo] = [{"geoBrote" : r[0][0:4], "especie": r[1]}]
            else:
                routes[geo].append({"geoBrote" : r[0][0:4], "especie": r[1]})

    return routes, routes_reverse

def get_routes_with_outbreaks(routes_reverse, last_N_days):

    lista_geo_Brotes = routes_reverse.keys()
    geo_oieid = dict()
    routes_with_outbreaks = dict()

    today = date.today()
    fecha = datetime.now() + timedelta(days = -today.weekday())
    mas_antiguo = fecha - timedelta(days = last_N_days)

    feat_col_brote = {
        "type": "FeatureCollection",
        "features": []
    }

    for geo in lista_geo_Brotes:
        cursor = outbreaks.find({
            "geohash": {"$regex": '{}.*'.format(geo)},
            "report_date" : {"$gte" : mas_antiguo}
        })

        for it in cursor:
            routes_with_outbreaks[geo] = routes_reverse[geo]

            if geo not in geo_oieid:
                geo_oieid[geo] = [it['oieid']]
            else:
                geo_oieid[geo].append(it['oieid'])

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
                    "end": "" if it['end'] == "" else math.floor(it['end'].timestamp() * 1000),
                    "city": it['city'],
                    "species": it['species'],
                    "at_risk": int(it['at_risk']),
                    "cases": int(it['cases']),
                    "deaths": int(it['deaths']),
                    "preventive_killed": int(it['preventive_killed'])
                }
            }

            feat_col_brote['features'].append(aux)

    return feat_col_brote, geo_oieid, routes_with_outbreaks


def get_comarcas_with_outbreaks(routes_with_outbreaks):

    lista_geo_Brotes = routes_with_outbreaks.keys()
    geo_comarca = dict()
    routes_with_outbreaks = dict()

    today = date.today()
    fecha = datetime.now() + timedelta(days = -today.weekday())
    mas_antiguo = fecha - timedelta(days = last_N_days)

    feat_col_brote = {
        "type": "FeatureCollection",
        "features": []
    }

    for geo in lista_geo_Brotes:
        cursor = outbreaks.find({
            "geohash": {"$regex": '{}.*'.format(geo)},
            "report_date" : {"$gte" : mas_antiguo}
        })

        for it in cursor:
            routes_with_outbreaks[geo] = routes_reverse[geo]

            if geo not in geo_oieid:
                geo_oieid[geo] = [it['oieid']]
            else:
                geo_oieid[geo].append(it['oieid'])

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
                    "end": "" if it['end'] == "" else math.floor(it['end'].timestamp() * 1000),
                    "city": it['city'],
                    "species": it['species'],
                    "at_risk": int(it['at_risk']),
                    "cases": int(it['cases']),
                    "deaths": int(it['deaths']),
                    "preventive_killed": int(it['preventive_killed'])
                }
            }

            feat_col_brote['features'].append(aux)

    return feat_col_brote, geo_oieid, routes_with_outbreaks



# # def modelo(last_N_days, startPoints, geoESP):
# #     alertaComarcasGeo={}
# #     tablaGeoComarca = json.load(open("tablaGeoComarca.txt",  encoding='utf-8'))

# #     today = date.today()
# #     fecha = datetime.now() + timedelta(days = -today.weekday())
# #     mas_antiguo = fecha - timedelta(days = last_N_days)


# #     listaBrotes = outbreaks.find({"report_date" : {"$gte" : mas_antiguo}})

# #     for brote in listaBrotes:
# #         response = neo4j_db.session().run('MATCH (n)-[r]-(x:Region) WHERE n.location starts with "{}" RETURN x.location, r.index'.format(brote['geohash'][0:4])).values()

# #         # geo4SPList = {}
# #         # for r in response:
# #         #     if r[0] in startPoints:
# #         #         geo4SPList[r[0]] = startPoints[r[0]]
# #         #     else:
# #         #         print(r[0])

# #         # for nodoGeo4 in geo4SPList:

# #         #     listaComarcasAfectadas = tablaGeoComarca[nodoGeo4]
# #         #     for comarcaAfectada in listaComarcasAfectadas:
# #         #         comarca = list(comarcaAfectada.keys())[0]
# #         #         peso = list(comarcaAfectada.values())[0]
# #         #         if comarca not in alertaComarcasGeo:
# #         #             alertaComarcasGeo[comarca] = [brote['geohash'][0:4], peso, nodoGeo4]
# #         #         else:
# #         #             alertaComarcasGeo[comarca].append([brote['geohash'][0:4], peso, nodoGeo4])

# #primera version modelo propuesta por irene 
# # El 20% con más brotes asociados, lo ponemos en nivel 5, el 20% siguiente en nivel 4.... y así hasta nivel 1.
# def calcularRiesgo(alertaComarcasGeo_sorted):

#     riesgoCG = {} #Pares (IdComarca, nivelRiesgo)
#     i = 0
#     #Limites
#     nivel5= len(alertaComarcasGeo_sorted) * 0.2 
#     nivel4= len(alertaComarcasGeo_sorted) * 0.2 + nivel5
#     nivel3= len(alertaComarcasGeo_sorted) * 0.2 + nivel4
#     nivel2= len(alertaComarcasGeo_sorted) * 0.2 + nivel3
#     nivel1 = len(alertaComarcasGeo_sorted)
#     for comarca in alertaComarcasGeo_sorted:

#         if i < nivel5:
#             riesgoCG[comarca] = 5
#         elif i >= nivel5 and i < nivel4:
#             riesgoCG[comarca] = 4
#         elif i >= nivel4 and i < nivel3:
#             riesgoCG[comarca] = 3
#         elif i >= nivel3 and i < nivel2:
#             riesgoCG[comarca] = 2
#         elif i >= nivel2 and i < nivel1:
#             riesgoCG[comarca] = 1

#         i+=1

#     return riesgoCG

# #Relacionamos los brotes con las comarcas
# def modelo(last_N_days, startPoints, geoEsp):
#     alertaComarcasGeo={}
#     tablaGeoComarca = json.load(open("tablaGeoComarca.txt",  encoding='utf-8'))

#     today = date.today()
#     fecha = datetime.now() + timedelta(days = -today.weekday())
#     mas_antiguo = fecha - timedelta(days = last_N_days)

#     listaBrotesNdias = outbreaks.find({"report_date" : {"$gte" : mas_antiguo}})
#     # listaBrotesNdias = outbreaks.find({})

#     listaBrotesEsp = startPoints.keys()

#     for brote in listaBrotesNdias:
#         if (brote['geohash'][0:4] in listaBrotesEsp):
#             for geocomarca in startPoints[brote['geohash'][0:4]]:
#                 if geocomarca['geoEsp'] in tablaGeoComarca:
#                     for comarca in tablaGeoComarca[ geocomarca['geoEsp'] ]:
#                         if comarca['cod_comarca'] not in alertaComarcasGeo:
#                             alertaComarcasGeo[ comarca['cod_comarca'] ] = [ {"oieid" : brote['oieid'], "peso" : comarca['peso'], "brote": brote, "arista" : geocomarca['migra'], "especie": geocomarca['especie']} ]
#                         else:
#                             alertaComarcasGeo[ comarca['cod_comarca'] ].append({"oieid" : brote['oieid'], "peso" : comarca['peso'], "brote": brote, "arista" : geocomarca['migra'], "especie":geocomarca['especie'] })

#     alertaComarcasGeo_sorted = sorted(alertaComarcasGeo, key=lambda k: len(alertaComarcasGeo[k]), reverse=True)

#     alertaComarcaRiesgo = calcularRiesgo(alertaComarcasGeo_sorted)
#     # return alertaComarcasGeo_sorted, alertaComarcasGeo

#     return alertaComarcaRiesgo, alertaComarcasGeo

# def genera_alerta(alertaComarcaRiesgo, alertaComarcasGeo):

#     #acceder bases de datos especies

#     feat_col_alertas = {
#         "type": "FeatureCollection",
#         "features": []
#     }

#     feat_col_migra = {
#         "type": "FeatureCollection",
#         "features": []
#     }

#     cursor = com.find({})

#     for it in cursor:
#         if it['comarca_sg'] in alertaComarcaRiesgo:
#             brote = list(outbreaks.find({"oieid": alertaComarcasGeo[it['comarca_sg']][0]['oieid']}))
#             especieFind = list(especie.find({"codigo anilla": alertaComarcasGeo[it['comarca_sg']][0]['especie']}))
#             print(alertaComarcaRiesgo[it['comarca_sg']])
#             feat_com={
#                 "type": "Feature",
#                 "geometry": {
#                     "type": "Point",
#                     "coordinates": [float(it['Longitud']), float(it['Latitud'])]
#                 },
#                 "properties": {
#                     "id": it['comarca_sg'], #Será el id de comarca
#                     "riskLevel": alertaComarcaRiesgo[it['comarca_sg']],
#                     "number_of_cases": brote[0]['affected_population'],
#                     "reportDate": brote[0]['report_date'].timestamp()*1000,
# <<<<<<< Updated upstream
#                     "startDate": brote[0]['start'].timestamp()*1000 ,
#                     "endDate":  "" if brote[0]['end'] == "" else brote[0]['end'].timestamp()*1000,
# =======
#                     # "startDate": brote[0]['start'].timestamp()*1000,
#                     # "endDate": brote[0]['end'].timestamp()*1000,
# >>>>>>> Stashed changes
#                     "codeSpecies": alertaComarcasGeo[it['comarca_sg']][0]['especie'],
#                     "species": brote[0]['species'],
#                     "commonName": especie[0]['Nombre común'],
#                     "fluSubtype": brote[0]['serotype'],
#                     "comarca_sg": it['comarca_sg'],
#                     "comarca": it['com_sgsa_n'],
#                     #"CMUN": it['CPROyMUN'][-2:],
#                     #"municipality": "Vitoria-Gasteiz",
#                     "CPRO": it['CPRO'],
#                     #"province": it['provincia'],
#                     #"CODAUTO": it['CODAUTO'],
#                     #"CA": it['comAutonoma'],
#                     "CPROyMUN": it['CPROyMUN']   
#                 }
#             }
#             feat_col_alertas["features"].append(feat_com)

            
#             feat_migra = {
#                 "type": "Feature",
#                 "geometry": {
#                     "type": "LineString",
#                     "coordinates": [ [float(it['Longitud']), float(it['Latitud'])], [float(brote[0]['long']), float(brote[0]['lat'])] ] #Comarca y brote asociado
#                 },
#                 "properties": {
#                     "idBrote": brote[0]['oieid'],
#                     "idAlerta": it['comarca_sg'] 
#                 }
#             }
#             feat_col_migra["features"].append(feat_migra)
#         else: #En caso de ser una comarca que no tendrá ningun brote asociado. El nivel de riesgo será 0
#             feat_com={
#                 "type": "Feature",
#                 "geometry": {
#                     "type": "Point",
#                     "coordinates": [float(it['Longitud']), float(it['Latitud'])]
#                 },
#                 "properties": {
#                     "id": it['comarca_sg'], #Será el id de comarca
#                     "riskLevel": 0,
#                     #"comarca_sg": it['comarca_sg'],
#                     "comarca": it['com_sgsa_n'],
#                     #"CMUN": it['CPROyMUN'][-2:],
#                     #"municipality": "Vitoria-Gasteiz",
#                     "CPRO": it['CPRO'],
#                     #"province": it['provincia'],
#                     #"CODAUTO": it['CODAUTO'],
#                     #"CA": it['comAutonoma'],
#                     "CPROyMUN": it['CPROyMUN']   
#                 }
#             }
#             feat_col_alertas["features"].append(feat_com)

#     return feat_col_alertas, feat_col_migra


def main(argv):

    # Variables del programa
    TAM_GEO_ESP = 4

    # El esquema:
    #     - Calculamos los geohashes de España (4 o 5 digitos)
    #     - Con los geohashes de España miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
    #         + Si hay un nodo con un geohash de España se mira a que otro nodo esta unido y se guarda este otro nodo.
    #     - Con los nodos correspondientes a brotes miramos en mongodb/outbreaks a ver si hay algun brote asociado a estos geohash.
    #     - Tambien miramos las comarcas asociadas a los geohashes de España (los que tienen algún brote asociado)
    #     - Con esto ya tendriamos comarcas y brotes asociados por una ruta (la migracion)


    # - Calculamos los geohashes de España (4 o 5 digitos)

    # $$$$ tablaGeoComarca con todos los geohashes (4 y 5 digitos) de España
    tablaGeoComarca = {}

    if (TAM_GEO_ESP == 4):
        with open("tablaGeoComarca.txt") as json_file:
            tablaGeoComarca = json.load(json_file)
    elif (TAM_GEO_ESP == 5):
        with open("tablaGeoComarca5.txt") as json_file:
            tablaGeoComarca = json.load(json_file)


    # - Con los geohashes de España miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
    #     + Si hay un nodo con un geohash de España se mira a que otro nodo esta unido y se guarda este otro nodo.
    today = date.today()
    fecha = datetime.now() + timedelta(days = -today.weekday())
    mas_antiguo = fecha - timedelta(days = last_N_days)
    listaBrotes = outbreaks.find({"report_date" : {"$gte" : mas_antiguo}})

    # geoEsp = tablaGeoComarca.keys()

    # $$$$ routes diccionario tipo "geohash español" : "lista con geohash asociados de migraciones y especie"
    # routes, routes_reverse = get_routes(geoEsp, TAM_GEO_ESP)

    for brote in listaBrotes:
        response = neo4j_db.session().run('MATCH (n)-[r]-(x:Region) WHERE n.location starts with "{}" RETURN x.location, r.especie'.format(brote['geohash'][0:4])).values()

        geo_comarcas_con_brotes = {}
        for geo_esp in response:
            if r[0] in tablaGeoComarca:
                geo_comarcas_con_brotes = r[0]
            else:
                print(r[0])

        for nodoGeo4 in geo4SPList:

            listaComarcasAfectadas = tablaGeoComarca[nodoGeo4]
            for comarcaAfectada in listaComarcasAfectadas:
                comarca = list(comarcaAfectada.keys())[0]
                peso = list(comarcaAfectada.values())[0]
                if comarca not in alertaComarcasGeo:
                    alertaComarcasGeo[comarca] = [brote['geohash'][0:4], peso, nodoGeo4]
                else:
                    alertaComarcasGeo[comarca].append([brote['geohash'][0:4], peso, nodoGeo4])

    # - Con los nodos correspondientes a brotes miramos en mongodb/outbreaks a ver si hay algun brote asociado a estos geohash.

    feat_col_brote, geo_oieid, routes_with_outbreaks = get_routes_with_outbreaks(routes_reverse, 90)

    # - Tambien miramos las comarcas asociadas a los geohashes de España (los que tienen algún brote asociado)



    # - Con esto ya tendriamos comarcas y brotes asociados por una ruta (la migracion)


    pass
#     geoESP, geoComar = geohashEsp()
#     startPoints = get_startPoints(geoESP)

#     brotes, brotes_col, brot = genera_Brotes(startPoints)
#     # alertas, migras = genera_alertas(brotes, brotes_col)

#     #comarcaRiesgo -> lista de las comarcas que estan en alerta junto a su nivel de riesgo
#     #alertaComarcasGeo -> lista de las comarcas con su brote y migracion asociado
#     comarcaRiesgo, alertaComarcasGeo = modelo(90, startPoints, geoESP)

#     #Generar Json de las alertas
#     alertas, migra = genera_alerta(comarcaRiesgo, alertaComarcasGeo)
# <<<<<<< Updated upstream
# =======

    
# >>>>>>> Stashed changes

#     neo4j_db.close()

#     text_file = open("brotes.geojson", "w")
#     n = text_file.write(json.dumps(brot))
#     text_file.close()
#     text_file = open("migras.geojson", "w")
#     n = text_file.write(json.dumps(migra))
#     text_file.close()
#     text_file = open("alertas.geojson", "w")
#     n = text_file.write(json.dumps(alertas))
#     text_file.close()



if __name__ == "__main__":
    main(sys.argv[1:])