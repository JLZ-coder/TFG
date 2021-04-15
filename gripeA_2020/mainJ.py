import sys, json
from factories.Factory import Factory
from factories.OutbreakBuilder import OutbreakBuilder
from factories.TempBuilder_copy import TempBuilder
from factories.ComarcasBuilder import ComarcasBuilder
from factories.MigrationProbBuilder import MigrationProbBuilder
from model.ModelSelector import ModelSelector
from model.GeojsonGenerator import GeojsonGenerator
from controller.controller_copy import Controller
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



def main(argv):
    dataBuilderList = list()
    dataBuilderList.append(OutbreakBuilder())
    dataBuilderList.append(TempBuilder())
    dataBuilderList.append(ComarcasBuilder())
    dataBuilderList.append(MigrationProbBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    default_params = dict()
    default_params["online"] = True
    default_params["temporaryWindow"] = 12
    default_params["start_date"] = None
    # default_params["start_date"] = {
    #     "day":1,
    #     "month":1,
    #     "year": 2021
    # }
    default_params["weeks"] = 52
    default_params["min_geohash_cover"] = 0.8
    default_params["thresholdAlert"] = 4
    default_params["rangeOfValues"] = [0.1, 1, 0.3]

    modelSelector.setParameters(default_params)

    geojsonGen = GeojsonGenerator()

    date = None

    control = Controller(modelSelector, dataFact, geojsonGen)

    #toolOffLine(control)

    #control.runOnlineTool()
    control.runOnlineTool(None)



    return 0


if __name__ == "__main__":
    main(sys.argv[1:])