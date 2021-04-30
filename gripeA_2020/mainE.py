import sys, json
'''
from factories.Factory import Factory
from factories.OutbreakBuilder import OutbreakBuilder
from factories.TempBuilder import TempBuilder
from factories.ComarcasBuilder import ComarcasBuilder
from factories.MigrationProbBuilder import MigrationProbBuilder
from model.ModelSelector import ModelSelector
from model.GeojsonGenerator import GeojsonGenerator
from controller.controller import Controller
#from factories.ReportBuilder_copy import ReportBuilder
from factories.ReportBuilder import ReportBuilder
'''
from pymongo import MongoClient
from neo4j import GraphDatabase
from datetime import datetime, timedelta, date

def toolOffLine(control):

    #Abrir y validar con el esquema
    f = open("exampleTool.json", "r")
    content = f.read()
    schemaJson = json.loads(content)

    #Ejecutar n * m veces el modelo
    for i in schemaJson['rangeOfValues']['temporaryWindow']:
        for j in schemaJson['rangeOfValues']['probBirds']:
            control.changeProb(j)
            geojson_alerta = control.run(datetime.strptime(schemaJson['date'], '%Y-%m-%d'), schemaJson['weeks'], i*4)

    #Procesar los datos y generar en Markdown las gráficas


def prueba():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.lv
    brotes_db = db.outbreaks
    com_db = db.comarcas

    start = datetime(2021,1,1)
    end = datetime(2021,2,1)
    neo4j_db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

    listaBrotes = brotes_db.find({"observation_date" : {"$gte" : start, "$lt" : end}})

    tablaGeoComarca = json.load(open("data/tablaGeoComarca4.txt",  encoding='utf-8'))
    cursor = list(com_db.find({"comarca_sg": "SP49108"}))

    geoCom = cursor[0]['geohash'][0:4]
    response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location'.format(geoCom)).values()

    brote_geohash = dict() 

    count = 0
    for i in listaBrotes:
        count += 1
        if i['geohash'][0:4] not in brote_geohash:
            brote_geohash[i['geohash'][0:4]] = [i['oieid']]
        else:
            brote_geohash[i['geohash'][0:4]].append(i['oieid'])

    print(count)
    
    
    for i in response:
        if i[0] in brote_geohash:
            print(brote_geohash[i[0]])
    

    

    


def main(argv):

    prueba()
    '''dataBuilderList = list()
    dataBuilderList.append(OutbreakBuilder())
    dataBuilderList.append(TempBuilder())
    dataBuilderList.append(ComarcasBuilder())
    dataBuilderList.append(ReportBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    date = datetime(2020,1,1)
    geojsonGen = GeojsonGenerator()

    control = Controller(modelSelector, dataFact, geojsonGen)
    #ReportBuilder.reportPDF()
    #toolOffLine(control)
   
    #control.runOfflineTool(date, 52, 3)
    control.runOnlineTool()
'''
    return 0

if __name__ == "__main__":
    main(sys.argv[1:])