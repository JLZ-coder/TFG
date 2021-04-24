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

def main(argv):
    dataBuilderList = list()
    dataBuilderList.append(OutbreakBuilder())
    dataBuilderList.append(TempBuilder())
    dataBuilderList.append(ComarcasBuilder())
    dataBuilderList.append(ReportBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    # uploader = gDriveUploader()
    # uploader.upload_file('markdown/informePrueba.pdf', 'informePrueba.pdf', 'alertas')
    # lista_url = uploader.get_url_from('informePrueba.pdf', 'alertas')

    geojsonGen = GeojsonGenerator()

    control = Controller(modelSelector, dataFact, geojsonGen)

    control.runOnlineTool()

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])