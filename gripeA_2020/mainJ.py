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
import os, sys

from factories.Factory import Factory
from factories.OutbreakBuilder import OutbreakBuilder
from factories.TempBuilder import TempBuilder
from factories.ComarcasBuilder import ComarcasBuilder
from controller import controller
from model.ModelSelector import ModelSelector
from model.GeojsonGenerator import GeojsonGenerator


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


def main(argv):
    dataBuilderList = list()
    dataBuilderList.append(OutbreakBuilder())
    dataBuilderList.append(TempBuilder())
    dataBuilderList.append(ComarcasBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    date = None
    geojsonGen = GeojsonGenerator()

    control = controller.Controller(modelSelector, dataFact, geojsonGen)

    control.run(date,12)

    return 0




if __name__ == "__main__":
    main(sys.argv[1:])