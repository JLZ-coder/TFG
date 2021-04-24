import requests
from pymongo import MongoClient
import sys
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, date
import pygeohash as geohash
import numpy as np

# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks

#Load csv outbreaks (2017-2021)
def loadOutbreaks():
    file = 'data/AvianInfluenza.csv'
    df = pd.read_csv(file, sep=",")
    #Renombramos
    df.rename(columns={'Event ID': 'oieid', 'Disease': 'disease', 'Serotype': 'serotype', 'Locality': 'city', 
        'lon': 'long', 'Country': 'country', 'Region': 'region','Location': 'location', 'Species': 'species', 'Date': 'date'}, inplace=True)
    
    #Solo nos quedamos con brotes de Europa
    indexNames = df[ df['region'] != 'Europe' ].index
    df.drop(indexNames , inplace=True)
    
    df = df.fillna(value="No Data")

    #Convertimos string a datetime columna Report Date
    df['report_date'] = pd.to_datetime(df['report_date'], format='%Y-%m-%d')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

    df = webScraping(df)

    records = df.to_dict(orient='records')
    outbreaks.delete_many({})
    
    outbreaks.insert_many(records)

#WebScrapping to get Cases and Deaths
#Parameters -> list(idOutbreak)

def webScraping(df):
    cases = []
    deaths = []
    animalType = []
    geohashA = []
    fullReport=[]
    observationDate = []
    country = []
    payload = json.dumps({})
    for i in df.index:
        url = "http://empres-i.fao.org/empres-i/obdj?id={}&lang=EN".format(df['oieid'][i])
        r = requests.get(url,
            data = payload,  
            headers={
                'Host': 'empres-i.fao.org',
                # 'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                #'DNT': '1',
                'X-Requested-With': 'XMLHttpRequest',
                # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.57',
                #'Referer': 'http://empres-i.fao.org/empres-i/2/obd?idOutbreak=287665',
                #'Accept-Encoding': 'gzip',
                #'Accept-Language': 'en'
            })
        s = json.loads(r.text)
        
        #Carga de valores obtenidos por requests en variables
        try:
            casos = s['outbreak']['speciesAffectedList'][0]['cases']
        except:
            casos = ""
        try:
            muertes = s['outbreak']['speciesAffectedList'][0]['deaths']
        except:
            muertes = ""
        try:
            animal = s['outbreak']['speciesAffectedList'][0]['animalType']
        except:
            animal = ""

        #Geohash
        valueGeohash = geohash.encode(float(df['lat'][i]), float(df['long'][i]))

        #Guardado en listas
        cases.append(casos)
        deaths.append(muertes)
        animalType.append(animal)
        geohashA.append(valueGeohash)
        fullReport.append("http://empres-i.fao.org/empres-i/2/obd?idOutbreak={}".format(df['oieid'][i]))


        #Si el valor de ObservationDate es NaN, ponemos el valor del reporte
        valOb = df['report_date'][i] if (df['observation_date'][i] == "No Data") else datetime.strptime( df['observation_date'][i], '%Y-%m-%d')
        observationDate.append(valOb)

        #Cambiar nombres de reino unido
        if s['outbreak']['country'] == "U.K. of Great Britain and Northern Ireland":
            country.append(s['outbreak']['admin1'])
        else: 
            country.append(df['country'][i])


    df['cases'] = cases
    df['deaths'] = deaths
    df['epiunit'] = animalType 
    df['geohash'] = geohashA
    df['urlFR'] = fullReport
    df['observation_date'] = observationDate
    df['country'] = country


    return df


#Download outbreaks last week
def downloadOutbreaks():
    #Descargamos el archivo 
    url = "https://us-central1-fao-empres-re.cloudfunctions.net/getEventsInfluenzaAvian"
    myFile = requests.get(url)
    #Guardamos
    open("data/outbreaksWeeks.csv", 'wb').write(myFile.content)
    #Abrimos csv para quedarnos con brotes nuevos de la ultima semana
    df = pd.read_csv('data/outbreaksWeeks.csv')
    df.rename(columns={'event_id': 'oieid', 'Disease': 'disease', 'Serotype': 'serotype', 'locality': 'city', 
        'lon': 'long', 'Country': 'country', 'Location': 'location', 'Species': 'species', 'display_date': 'date'}, inplace=True)
    
    #Solo con brotes de Europa
    indexNames = df[ df['region'] != 'Europe' ].index
    df.drop(indexNames , inplace=True)

    df = df.fillna(value="No Data")

    #Buscar los de la ultima semana
    #fecha de hoy
    today = datetime.today()
    #Lunes de esta semana
    monday = today + timedelta(days = -today.weekday())
    #Semana anterior 
    lastWeek = monday - timedelta(weeks = 8)
    #Indices para borrar el resto de filas
    dfAux = []
    #Convertimos string a datetime columna Report Date
    df['report_date'] = pd.to_datetime(df['report_date'], format='%Y-%m-%d')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    for i in df.index:
        
        if df['observation_date'][i] == "No Data":
            dateOutbreak = df['report_date'][i]
        else:
            dateOutbreak = datetime.strptime(df['observation_date'][i], '%Y-%m-%d') 

        if dateOutbreak >= lastWeek and dateOutbreak <= monday:
            continue

        dfAux.append(i)

    df = df.drop(dfAux,axis=0)
    df = webScraping(df)


    records = df.to_dict(orient='records')

    #Si el brote ya existe remplazamos la nueva infomación y si no, lo añade
    for i in records:
        outbreaks.replace_one({'oieid': i['oieid']}, i, upsert = True)
    

#Main

def main(argv):
  
    loadOutbreaks()
    downloadOutbreaks()

    return 0

if __name__ == '__main__':
    main(sys.argv[1:])