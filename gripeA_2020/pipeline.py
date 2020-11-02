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


# graph = Graph("bolt://localhost:7687", auth=("neo4j", "ed4r;bnf"))
# Realiza el scraping de la web de wahis para recoger los brotes

# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}

def genera_Brotes():
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
    cursor = outbreaks.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))

    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')
    for it in cursor:
        if it['geohash'][0:4] not in geojson:
            geojson[it['geohash'][0:4]] = json.loads('{ "type": "Feature", "geometry": { "type": "Point",'+
            '"Coordinates": ['+ it['lat'] +', '+ it['long'] +', 0] }, '+
            '"properties": { "disease": "'+ diseases[it['diseade_id']] +'", "country": "'+ it['country'] +'",'+
            '"start": "'+ str(math.floor(it['start'].timestamp() * 1000)) +'",'+
            '"city": "'+ it['city'] +'", "geohash": "'+ it['geohash'][0:4] + '", "species":"'+ it['species'] +'",' +
            '"at_risk": '+ it['at_risk'] +', "cases": '+ it['cases'] +', "deaths": '+ it['deaths'] +', "preventive_killed": '+
            it['preventive_killed'] +'} }')
        else:
            geojson[it['geohash'][0:4]]['properties']['at_risk'] = int(geojson[it['geohash'][0:4]]['properties']['at_risk']) + int(it['at_risk'])
            geojson[it['geohash'][0:4]]['properties']['cases'] = int(geojson[it['geohash'][0:4]]['properties']['cases']) + int(it['cases'])
            geojson[it['geohash'][0:4]]['properties']['deaths'] = int(geojson[it['geohash'][0:4]]['properties']['deaths']) + int(it['deaths'])
            geojson[it['geohash'][0:4]]['properties']['preventive_killed'] = int(geojson[it['geohash'][0:4]]['properties']['preventive_killed']) + int(it['preventive_killed'])


        print (geojson[it['geohash'][0:4]])

    return geojson

def genera_aristas(brotes):

    cursor = outbreaks.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    geojson = []
    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')
    for it in cursor:
        if it['geohash'][0:4] not in geojson:
            geojson[it['geohash'][0:4]] = json.loads('{ "type": "Feature", "geometry": { "type": "Point",'+
            '"Coordinates": ['+ it['lat'] +', '+ it['long'] +', 0] }, '+
            '"properties": { "disease": "'+ diseases[it['diseade_id']] +'", "country": "'+ it['country'] +'",'+
            '"start": "'+ str(math.floor(it['start'].timestamp() * 1000)) +'",'+
            '"city": "'+ it['city'] +'", "geohash": "'+ it['geohash'][0:4] + '", "species":"'+ it['species'] +'",' +
            '"at_risk": '+ it['at_risk'] +', "cases": '+ it['cases'] +', "deaths": '+ it['deaths'] +', "preventive_killed": '+
            it['preventive_killed'] +'} }')
        else:
            geojson[it['geohash'][0:4]]['properties']['at_risk'] = int(geojson[it['geohash'][0:4]]['properties']['at_risk']) + int(it['at_risk'])
            geojson[it['geohash'][0:4]]['properties']['cases'] = int(geojson[it['geohash'][0:4]]['properties']['cases']) + int(it['cases'])
            geojson[it['geohash'][0:4]]['properties']['deaths'] = int(geojson[it['geohash'][0:4]]['properties']['deaths']) + int(it['deaths'])
            geojson[it['geohash'][0:4]]['properties']['preventive_killed'] = int(geojson[it['geohash'][0:4]]['properties']['preventive_killed']) + int(it['preventive_killed'])


        print (geojson[it['geohash'][0:4]])

    return geojson



def main(argv):
    brotes = genera_Brotes()



if __name__ == "__main__":
    main(sys.argv[1:])
