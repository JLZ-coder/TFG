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
import os
from git import Repo
from scripts.newOutbreaks_mongo import downloadOutbreaks
from scripts.weather_mongo import cronTemp, prediction
from scripts.geojson_github import from_geojson_to_github

def main(argv):
    downloadOutbreaks()

    cronTemp()
    prediction()

    dataBuilderList = list()
    dataBuilderList.append(OutbreakBuilder())
    dataBuilderList.append(TempBuilder())
    dataBuilderList.append(ComarcasBuilder())
    dataBuilderList.append(ReportBuilder())
    dataFact = Factory(dataBuilderList)

    modelSelector = ModelSelector()

    geojsonGen = GeojsonGenerator()

    control = Controller(modelSelector, dataFact, geojsonGen)

    control.runOnlineTool()

    from_geojson_to_github()   

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])