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

# Realiza el scraping de la web de wahis para recoger los brotes

# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks

def main(argv):
    outbreaks.find()


if __name__ == "__main__":
    main(sys.argv[1:])