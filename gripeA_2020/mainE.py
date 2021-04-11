import sys, json
from factories.Factory import Factory
from factories.OutbreakBuilder import OutbreakBuilder
from factories.TempBuilder import TempBuilder
from factories.ComarcasBuilder import ComarcasBuilder
from model.ModelSelector import ModelSelector
from model.GeojsonGenerator import GeojsonGenerator
from controller import controller
from datetime import datetime, timedelta, date

def toolOffLine(control):

    #Abrir y validar con el esquema
    f = open("data/exampleTool.json", "r")
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
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    date = None
    geojsonGen = GeojsonGenerator()

    control = controller.Controller(modelSelector, dataFact, geojsonGen)

    toolOffLine(control)
    #control.run(date,12)

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])