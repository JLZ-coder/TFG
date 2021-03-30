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


diseases = {
    '15' : "Highly Path Avian influenza",
    '201' : "Low Path Avian influenza",
    '1164' : "Highly pathogenic influenza A viruses"
}


def main(argv):
    dataBuilderList = list()
    dataBuilderList.append(OutbreakBuilder())
    dataBuilderList.append(TempBuilder())
    dataBuilderList.append(ComarcasBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    date = datetime(2020, 1, 1)
    geojsonGen = GeojsonGenerator()

    control = controller.Controller(modelSelector, dataFact, geojsonGen)

    control.run(date, 52, 6)

    return 0




if __name__ == "__main__":
    main(sys.argv[1:])