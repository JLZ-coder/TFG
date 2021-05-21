import sys, json
from factories.Factory import Factory
from factories.OutbreakBuilder import OutbreakBuilder
from factories.TempBuilder import TempBuilder
from factories.ComarcasBuilder import ComarcasBuilder
from factories.MigrationProbBuilder import MigrationProbBuilder
from model.ModelSelector import ModelSelector
from model.GeojsonGenerator import GeojsonGenerator
from controller.controller import Controller
from factories.ReportBuilder import ReportBuilder
from datetime import datetime, timedelta, date
from model.gdriveUploader import gDriveUploader
import matplotlib.pyplot as plt

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
    dataBuilderList.append(ReportBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    geojsonGen = GeojsonGenerator()

    control = Controller(modelSelector, dataFact, geojsonGen)

    start = datetime(2021, 2, 10)
    control.runOfflineTool(start, 6)
    # Comenzando desde 52 semanas atras, un anio atras
    # control.runOnlineTool(52)
  
    # # x-axis values
    # x = [1,2,3,4,5,6,7,8,9,10]
    # # y-axis values
    # y = [2,4,5,7,6,8,9,11,12,12]
    
    # # plotting points as a scatter plot
    # plt.scatter(x, y, label= "stars", color= "green", 
    #             marker= "*", s=30)
    
    # # x-axis label
    # plt.xlabel('x - axis')
    # # frequency label
    # plt.ylabel('y - axis')
    # # plot title
    # plt.title('My scatter plot!')
    # # showing legend
    # plt.legend()
    
    # # function to show the plot
    # plt.show()
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])