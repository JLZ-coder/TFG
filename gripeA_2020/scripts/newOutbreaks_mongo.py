import requests
from pymongo import MongoClient
import sys
import pandas as pd
from bs4 import BeautifulSoup
import json

# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks

#Load csv outbreaks (2017-2021)
def loadOutbreaks():
    file = 'data/AvianInfluenza.csv'
    df = pd.read_csv(file, sep=",")

    return df
#WebScrapping to get Cases and Deaths
#Parameters -> list(idOutbreak)

def webScraping(df):
    cases = []
    deaths = []
    payload = json.dumps({})
    for i in df['Event ID']:
        url = "http://empres-i.fao.org/empres-i/obdj?id={}&lang=EN".format(i)
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
        try:
            casos = s['outbreak']['speciesAffectedList'][0]['cases']
        except:
            casos = ""
        try:
            muertes = s['outbreak']['speciesAffectedList'][0]['deaths']
        except:
            muertes = ""

        cases.append(casos)
        deaths.append(muertes)


    df['cases'] = cases
    df['deaths'] = deaths

    records = df.to_dict(orient='records')
    outbreaks.delete_many({})
    
    outbreaks.insert_many(records)
    


#Download outbreaks last week
def downloadOutbreaks():
    #Descargamos el archivo 
    url = "https://us-central1-fao-empres-re.cloudfunctions.net/getEventsInfluenzaAvian"
    myFile = requests.get(url)
    #Guardamos
    open("data/outbreaksWeeks.csv", 'wb').write(myFile.content)
    #Abrimos csv para quedarnos con brotes nuevos de la ultima semana
    df = pd.read_csv('data/outbreaksWeeks.csv')

    print(df)

    return 0

#Main

def main(argv):

    #df = loadOutbreaks()
    #webScraping(df)
    downloadOutbreaks()


    return 0



if __name__ == '__main__':
    main(sys.argv[1:])

