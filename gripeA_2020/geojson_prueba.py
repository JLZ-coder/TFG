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
    it = outbreaks.find_one({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }

    brote = it

    diseases = {
        '15' : "Highly Path Avian influenza",
        '201' : "Low Path Avian influenza",
        '1164' : "Highly pathogenic influenza A viruses"
    }

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
    feat_col["features"].append(aux)

    return feat_col, brote

def comarcas():
    cursor = com.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }

    today = date.today()
    start = today + timedelta(days = -today.weekday())
    end = start + timedelta(weeks = 1)

    start = datetime.combine(start, datetime.min.time())
    end = datetime.combine(end, datetime.min.time())

    risk = 0
    for it in cursor:
        cod_comarca = it['comarca_sg']
        aux={
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(it['Longitud']), float(it['Latitud'])]
            },
            "properties": {
                "id": cod_comarca, #Será el id de comarca
                "riskLevel": risk,
                "number_of_cases": 0,
                "startDate": start.timestamp() * 1000,
                "endDate": end.timestamp() * 1000,
                # "codeSpecies": 1840,
                # "species": "Anas crecca",
                # "commonName": "Pato cuchara",
                # "fluSubtype": "H5",
                "idComarca": cod_comarca,
                "comarca": it['com_sgsa_n'],
                "CPRO": it['CPRO'],
                "province": it['provincia'],
                "CPROyMUN": it['CPROyMUN']
            }
        }
        feat_col['features'].append(aux)

    return feat_col

def migracion(brote):
    cursor = com.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }

    for it in cursor:
        cod_comarca = it['comarca_sg']
        aux = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [float(it['Longitud']), float(it['Latitud']), float(brote['long']), float(brote['lat'])]
                },
                "properties": {
                    "idBrote": brote["oieid"],
                    "idAlerta": cod_comarca,
                    "idComarca": cod_comarca
                }
            }

        feat_col['features'].append(aux)

    return feat_col

def main(argv):
    geobrotes, brote = brotes()

    comarc_centro = comarcas()

    migra = migracion(brote)

    # text_file = open("brotes.geojson", "w")
    # n = text_file.write(json.dumps(geobrotes))
    # text_file.close()

    text_file = open("alertas.geojson", "w")
    n = text_file.write(json.dumps(comarc_centro))
    text_file.close()

    # text_file = open("rutas.geojson", "w")
    # n = text_file.write(json.dumps(migra))
    # text_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])