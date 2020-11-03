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


def main(argv):
    cursor = outbreaks.find({})
    #print (math.floor(datetime.now().timestamp() * 1000))
    feat_col = {
        "type": "FeatureCollection",
        "features": []
    }
    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')
    i = 1
    for it in cursor:

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
                "preventive_killed": int(it['preventive_killed'])
            }
        }
        feat_col["features"].append(feat)
        i += 1

    # text_file = open("brotes.txt", "w")
    # n = text_file.write(json.dumps(feat_col))
    # text_file.close()
    # print (json.dumps(feat_col))



if __name__ == "__main__":
    main(sys.argv[1:])