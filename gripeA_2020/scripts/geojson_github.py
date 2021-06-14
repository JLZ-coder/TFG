import sys, json, os
from git import Repo
from datetime import date, datetime
from git import Git

def from_geojson_to_github(): 
    print("Subida de ficheros a github")
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
        os.chdir(repo_dir)
        commit_message = 'Subida semanal de geojson ' + today
        repo.index.add(file_list)
        repo.git.add(update=True)
        repo.index.commit(commit_message)
        origin = repo.remote('origin')
        origin.pull()
        origin.push()
    except Exception as e:
        print('Some error occured while pushing the code')
        print(e)
        return 1

    return 0