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

    control.runOnlineTool()

    # Subida de los geojson a master
    copia_a_destino = "cp -r /home/caballes/TFG/gripeA_2020/geojson/. /home/caballes/applicacionWeb/GeoJSON/"
    os.system(copia_a_destino)

    repo_dir = '/home/caballes/applicacionWeb/'
    repo = Repo(repo_dir)
    file_list = [
        'GeoJSON/alertas.geojson',
        'GeoJSON/brotes.geojson',
        'GeoJSON/rutas.geojson'
    ]
    now = datetime.now()
    today = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    try:
        commit_message = 'Subida semanal de geojson ' + today
        repo.index.add(file_list)
        repo.git.add(update=True)
        repo.index.commit(commit_message)
        origin = repo.remote('origin')
        origin.pull()
        origin.push()
    except:
        print('Some error occured while pushing the code')    

    return 0


if __name__ == "__main__":
    main(sys.argv[1:])