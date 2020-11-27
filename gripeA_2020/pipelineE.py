import requests
import re
# este sys me suobra mucho y habrá que quitarlo
import sys
import time
import json
import pymongo
from pymongo import MongoClient
import pygeohash as geohash
from datetime import datetime, timedelta
import math
from neo4j import GraphDatabase
import random
import string

#from dao.daoBrotes import daoBrotes
#from dao.daoComar import daoComar



# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
migrations = db.migrations
com = db.comarcas
diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

# daoComar = daoComar()
# daoBrotes = daoBrotes()

# Saca geohash de 3 digitos que caen en espana
def geohashEsp():
    cursor = com.find({})
    geoESP = set()
    geoComar = {}

    for it in cursor:
        geo = geohash.encode(float(it['Latitud']), float(it['Longitud']))
        geoESP.add(geo[0:3])

        if geo[0:4] not in geoComar:
            geoComar[geo[0:4]] = [it['CPROyMUN']]
        else:
            geoComar[geo[0:4]].append(it['CPROyMUN'])

    return geoESP, geoComar


def migraHaciaEsp(geoESP): 

    startPoints = dict()
    for geo in geoESP:
        response = driver.session().run('MATCH (n)-[r]->(x:Region) WHERE x.location starts with "{}" RETURN n.location, r.index'.format(geo)).values()
        for r in response:
            if r[0][0:4] not in startPoints:
                startPoints[r[0][0:4]] = [r[1]]
            else:
                startPoints[r[0][0:4]].append(r[1])

    return startPoints

def genera_Brotes(startPoints):
    # {'_id': ObjectId('5f9465f402f12b902433b244'), 
    # 'oieid': '1000097712', 
    # 'diseade_id': '15',  ESTE
    # 'country': 'AFG',     ESTE
    # 'start': datetime.datetime(2018, 1, 23, 0, 0),    ESTE
    # 'status': 'Continuing', 
    # 'city': 'Hirat',  ESTE
    # 'district': 'Injel',
    # 'subdistrict': 'South',
    # 'epiunit': 'Farm',
    # 'location': 'South', 
    # 'lat': '34.352865',   ESTE
    # 'long': '62.204029',  ESTE
    # 'affected_population': ' ', 
    # 'geohash': 'tqh5rmxxfyjv',    ESTE (SOLO 4 DIGITOS)
    # 'species': 'Birds',   ESTE
    # 'at_risk': '54000',   ESTE
    # 'cases': '4450',      ESTE
    # 'deaths': '4450',     ESTE
    # 'preventive_killed': '49550'}     ESTE

    # {
    #     "type": "Feature",
    #     "geometry":
    #         {
    #             "type": "Point",
    #             "Coordinates": [34.352865, 62.204029, 0]
    #         },
    #     "properties":
    #         {
    #             "diseade": 'Highli Path Avian influenza',
    #             "country": "AFG",
    #             "start": datetime.datetime(2018, 1, 23, 0, 0) cambiar
    #             "city": 'Hirat'
    #             "geohash": "tqh5",
    #             "species":"Birds",
    #             'at_risk': '54000',       cambiar
    #             'cases': '4450',          cambiar
    #             'deaths': '4450',         cambiar
    #             'preventive_killed': '49550'  cambiar
    #         }
    # }
    feat_col_brote = {
        "type": "FeatureCollection",
        "features": []
    }
    geojson = {}
    brotes_col = {}
    for geo in startPoints.keys():
        cursor = daoBrotes.find({
            "geohash": {
                "$regex": '{}.*'.format(geo)
            }
        })

        for it in cursor:

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
                    "end": math.floor(it['end'].timestamp() * 1000),
                    "city": it['city'],
                    "species": it['species'],
                    "at_risk": int(it['at_risk']),
                    "cases": int(it['cases']),
                    "deaths": int(it['deaths']),
                    "preventive_killed": int(it['preventive_killed'])
                }
            }
            if it['geohash'][0:4] not in geojson:
                geojson[it['geohash'][0:4]] = startPoints[it['geohash'][0:4]]

            if it['geohash'][0:4] not in brotes_col:
                brotes_col[it['geohash'][0:4]] = [aux]
            else:
                brotes_col[it['geohash'][0:4]].append(aux)

            feat_col_brote['features'].append(aux)

    return geojson, brotes_col, feat_col_brote





def genera_alertas(brotes, brotes_col):
    feat_col_com = {
        "type": "FeatureCollection",
        "features": []
    }
    feat_col_migra = {
        "type": "FeatureCollection",
        "features": []
    }

    for brote in brotes:
        for migra in brotes[brote]:
            response = driver.session().run('MATCH (n)-[r]->(x:Region) WHERE r.index = {} RETURN x.location'.format(migra)).value()
            lat, long, lat_err, long_err = geohash.decode_exactly(response[0])
            if lat - lat_err < lat + lat_err:
                lat_range = (lat - lat_err, lat + lat_err)
            else:
                lat_range = (lat + lat_err, lat - lat_err)

            if long - long_err < long + long_err:
                long_range =  (long - long_err, long + long_err)
            else:
                long_range =  (long + long_err, long - long_err)

            cursor = com.find({})
            for it in cursor:
                if it['izqI'][1] < it['izqS'][1]:
                    lat_range_mongo = (it['izqI'][1], it['izqS'][1])
                else:
                    lat_range_mongo = (it['izqS'][1], it['izqI'][1])

                if it['izqI'][0] < it['derI'][0]:
                    long_range_mongo =  (it['izqI'][0], it['derI'][0])
                else:
                    long_range_mongo =  (it['derI'][0], it['izqI'][0])

                if (
                        (lat_range[0] < it['izqS'][1] and it['izqS'][1] < lat_range[1])
                        or
                        (lat_range[0] < it['izqI'][1] and it['izqI'][1] < lat_range[1])
                        or
                        (lat_range_mongo[0] < lat_range[0] and lat_range[0] < lat_range_mongo[1])
                    ) and (
                        (long_range[0] < it['izqI'][0] and it['izqI'][0] < long_range[1])
                        or
                        (long_range[0] < it['derI'][0] and it['derI'][0] < long_range[1])
                        or
                        (long_range_mongo[0] < long_range[0] and long_range[0] < long_range_mongo[1])
                    ):
                    feat_com = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(it['Longitud']), float(it['Latitud'])]
                        },
                        "properties": {
                            "id": it['CPROyMUN'],
                            "riskLevel": 0,
                            "number_of_cases": random.randint(0, 100),
                            "startDate": random.randint(1572890531000, 1604512931000),
                            "endDate": 1704512931000,
                            "codeSpecies": 1840,
                            "species": "Anas crecca",
                            "commonName": "Pato cuchara",
                            "fluSubtype": "H5",
                            "comarca_sg": it['comarca_sg'],
                            "comarca": it['com_sgsa_n'],
                            "CMUN": it['CPROyMUN'][-2:],
                            "municipality": "Vitoria-Gasteiz",
                            "CPRO": it['CPROyMUN'][:2],
                            "province": it['provincia'],
                            "CODAUTO": it['CODAUTO'],
                            "CA": it['comAutonoma'],
                            "CPROyMUN": it['CPROyMUN']
                        }
                    }
                    feat_col_com["features"].append(feat_com)

                    for b in brotes_col[brote]:
                        feat_migra = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [ [float(it['Longitud']), float(it['Latitud'])], [b['geometry']['coordinates'][0], b['geometry']['coordinates'][1]] ]
                            },
                            "properties": {
                                "idBrote": b['properties']['id'],
                                "idAlerta": it['CPROyMUN']
                            }
                        }
                        feat_col_migra["features"].append(feat_migra)

    return feat_col_com, feat_col_migra

def modelo(last_N_days, startPoints, geoESP):
    alertaComarcasGeo={}
    tablaGeoComarca = json.load(open("tablaGeoComarca.txt",  encoding='utf-8'))

    fecha = datetime.utcnow() - timedelta(days=last_N_days)
    
    listaBrotes = outbreaks.find({})
        
    for brote in listaBrotes:
        response = driver.session().run('MATCH (n)-[r]->(x:Region) WHERE n.location starts with "{}" RETURN x.location, r.index'.format(brote['geohash'][0:4])).values()
       
        geo4SPList = {}
        for r in response:
            if r[0] in startPoints:
                geo4SPList[r[0]] = startPoints[r[0]]
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

        
        

    alertaComarcasGeo
    

def main(argv):
    
    geoESP, geoComar = geohashEsp()
    startPoints = migraHaciaEsp(geoESP)
    modelo(120, startPoints, geoESP)

    brotes, brotes_col, brot = genera_Brotes(startPoints)
    alertas, migras = genera_alertas(brotes, brotes_col)

    driver.close()

    text_file = open("brotes.txt", "w")
    n = text_file.write(json.dumps(brot))
    text_file.close()
    text_file = open("migras.txt", "w")
    n = text_file.write(json.dumps(migras))
    text_file.close()
    text_file = open("alertas.txt", "w")
    n = text_file.write(json.dumps(alertas))
    text_file.close()



if __name__ == "__main__":
    main(sys.argv[1:])
