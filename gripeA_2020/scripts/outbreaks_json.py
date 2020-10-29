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

    #print(f'Hola, {math.floor(datetime.now().timestamp() * 1000)}')
    i = 1
    for it in cursor:
        geojson = json.loads('{ "type": "Feature", "geometry": { "type": "Point",'+
        '"Coordinates": ['+ it['lat'] +', '+ it['long'] +', 0] }, '+
        '"properties": { "id": '+ str(i) +', "disease": "'+ diseases[it['diseade_id']] +'", "country": "'+ it['country'] +'",'+
        '"start": "'+ str(math.floor(it['start'].timestamp() * 1000)) +'", "end": '+ str(math.floor(it['end'].timestamp() * 1000)) + ','
        '"city": "'+ it['city'] +'", "species":"'+ it['species'] +'",' +
        '"at_risk": '+ it['at_risk'] +', "cases": '+ it['cases'] +', "deaths": '+ it['deaths'] +', "preventive_killed": '+
        it['preventive_killed'] +'} }')
        i += 1
        print (geojson)



if __name__ == "__main__":
    main(sys.argv[1:])