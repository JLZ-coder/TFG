import requests
import re
# este sys me suobra mucho y habrá que quitarlo
import sys
import time
import json
import pymongo
from pymongo import MongoClient
import pygeohash as geohash
from datetime import datetime, timedelta, date
import math
import random

# Realiza el scraping de la web de wahis para recoger los brotes

# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
com = db.comarcas
diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}

def brotes():
    cursor = outbreaks.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }
    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')
    i = 1
    for it in cursor:

        if (it['end'].timestamp() >= (datetime.now() - timedelta(days = 90)).timestamp() ):
            feat = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(it['long']), float(it['lat'])]
                },
                "properties": {
                    "id": i,
                    "disease": diseases[it['disease_id']],
                    "country": it['country'],
                    "start": math.floor(it['start'].timestamp() * 1000),
                    "end": math.floor(it['end'].timestamp() * 1000),
                    "city": it['city'],
                    "species": it['species'],
                    "at_risk": int(it['at_risk']),
                    "cases": int(it['cases']),
                    "deaths": int(it['deaths']),
                    "preventive_killed": int(it['preventive_killed']),
                    "serotipo": "H5",
                    "moreInfo": "https://www.oie.int/wahis_2/public/wahid.php/Reviewreport/Review?page_refer=MapFullEventReport&reportid=33894",
                    "epiUnit" : "backyard"
                }
            }
            feat_col["features"].append(feat)
            i += 1

    return feat_col

def comarcas():
    cursor = com.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }
    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')
    i = 0
    # ite = iter(cursor)

    # “id”: 1,
    # "riskLevel":0,
    # "number_of_cases":0,
    # "startDate":1558383654414,
    # "endDate":1558383654414,     
    # "codeSpecies":1840,
    # “species”: “Anas crecca”,
    # “commonName”: “Pato cuchara”,
    # "fluSubtype":"H5",
    # "comarca_sg":"SP01059",
    # "comarca":"ARABA-ALAVA",
    # "CMUN":"059",
    # "municipality":"Vitoria-Gasteiz",
    # "CPRO":"01",
    # "province":"Araba/Álava",
    # "CODAUTO":"16",
    # "CA":"País Vasco",
    # "CPROyMUN":"01059"
    today = date.today()
    fecha = datetime.now() + timedelta(days = -today.weekday(), weeks=-1)

    risk = 0
    while i < 12:
        for it in cursor:
            # it = next(ite)
            feat = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(it['Longitud']), float(it['Latitud'])]
                },
                "properties": {
                    "id": it['comarca_sg'],
                    "riskLevel": risk,
                    "number_of_cases": random.randint(0, 100),
                    "startDate": math.floor(fecha.timestamp() * 1000),
                    "endDate": math.floor((fecha + timedelta(days = 7)).timestamp() * 1000),
                    "codeSpecies": 1840,
                    "species": "Anas crecca",
                    "commonName": "Pato cuchara",
                    "fluSubtype": "H5",
                    "comarca_sg": it['comarca_sg'],
                    "comarca": it['com_sgsa_n'],
                    "CPRO": it['CPRO'],
                    "province": it['provincia'],
                    "CPROyMUN": it['CPROyMUN']
                }
            }
            feat_col["features"].append(feat)

        text_file = open("alertas_{}.geojson".format(fecha.strftime("%d-%m-%y")), "w")
        n = text_file.write(json.dumps(feat_col))
        text_file.close()

        feat_col['features'].clear()

        cursor.rewind()
        fecha = fecha - timedelta(days = 7)
        i += 1
        risk += 1
        risk %= 4

    return feat_col

def migracion(brotes, comarcas):
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }
    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')

    # {"type":"FeatureCollection", 
    # "features":
    # [
    #   {"type":"Feature",
    #   "geometry":
    #         {
    #           "type":"LineString",
    #           "coordinates":[[-6.26666666666665,37.1],[10.55,55.9666666666666]]
    #         },
    #           "properties":
    #           {
    #              “idBrote”: 1, 
	#      “idAlerta”: 13,
    #           }
    #      }
    #    ]
    #   }

    i = 0
    j = 0
    while i < len(comarcas['features']):
        com_long = comarcas["features"][i]["geometry"]["coordinates"][0]
        com_lat = comarcas["features"][i]["geometry"]["coordinates"][1]
        com_id = comarcas["features"][i]["properties"]["id"]
        brot_long = brotes["features"][j]["geometry"]["coordinates"][0]
        brot_lat = brotes["features"][j]["geometry"]["coordinates"][1]
        brot_id = brotes["features"][j]["properties"]["id"]

        feat = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [ [com_long, com_lat], [brot_long, brot_lat] ]
            },
            "properties": {
                "idBrote": brot_id,
	            "idAlerta": com_id
            }
        }
        feat_col["features"].append(feat)
        i += 1
        j += 1
        j %= len(brotes['features'])
        # if i > 10:
        #     break

    return feat_col

def main(argv):
    geobrotes = brotes()

    comarc_centro = comarcas()

    migra = migracion(geobrotes, comarc_centro)

    # text_file = open("brotes.txt", "w")
    # n = text_file.write(json.dumps(geobrotes))
    # text_file.close()

    # text_file = open("alertas.txt", "w")
    # n = text_file.write(json.dumps(comarc_centro))
    # text_file.close()

    # text_file = open("migraciones.txt", "w")
    # n = text_file.write(json.dumps(migra))
    # text_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])