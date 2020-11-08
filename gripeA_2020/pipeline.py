import requests
import re
# este sys me suobra mucho y habrá que quitarlo
import sys
import time
import json
import pymongo
from pymongo import MongoClient
import pygeohash as geohash
from datetime import datetime
import math
from neo4j import GraphDatabase


# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}
com = db.comarcas

def geohashEsp():
    cursor = com.find({})
    geoESP = set()
    geoComar = {}

    for it in cursor:
        geo = geohash.encode(float(it['YCoord']), float(it['XCoord']))
        geoESP.add(geo[0:3])

        if geo[0:4] not in geoComar:
            geoComar[geo[0:4]] = [it['CPROyMUN']]
        else:
            geoComar[geo[0:4]].append(it['CPROyMUN'])

    return geoESP, geoComar

def migraHaciaEsp(geoESP):
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

    startPoints = set()
    for geo in geoESP:
        response = driver.session().run('MATCH (n)-[r]->(x:Region) WHERE x.location starts with "{}" RETURN n.location, r.index'.format(geo)).values()
        startPoints.update(response)

    driver.close()

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
    geojson = {}
    for geo in startPoints:
        cursor = outbreaks.find({
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
                geojson[it['geohash'][0:4]] = [aux]
            else:
                # geojson[it['geohash'][0:4]]['properties']['at_risk'] = int(geojson[it['geohash'][0:4]]['properties']['at_risk']) + int(it['at_risk'])
                # geojson[it['geohash'][0:4]]['properties']['cases'] = int(geojson[it['geohash'][0:4]]['properties']['cases']) + int(it['cases'])
                # geojson[it['geohash'][0:4]]['properties']['deaths'] = int(geojson[it['geohash'][0:4]]['properties']['deaths']) + int(it['deaths'])
                # geojson[it['geohash'][0:4]]['properties']['preventive_killed'] = int(geojson[it['geohash'][0:4]]['properties']['preventive_killed']) + int(it['preventive_killed'])
                geojson[it['geohash'][0:4]].append(aux)

            print (geojson[it['geohash'][0:4]])

    return geojson



def main(argv):
    # brotes = genera_Brotes()
    geoESP, geoComar = geohashEsp()
    startPoints = migraHaciaEsp(geoESP)
    brotes = genera_Brotes(startPoints)



if __name__ == "__main__":
    main(sys.argv[1:])
