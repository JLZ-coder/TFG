import requests
from pymongo import MongoClient
import sys
import pandas as pd
from bs4 import BeautifulSoup

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

def webScarpping(df):
    for i in df['Event ID']:
        url = "http://empres-i.fao.org/empres-i/2/obd?idOutbreak={}".format(i)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        val = soup.find_all('table', class_='ftable')
        print(soup)
        print(1)
    return 0


#Download outbreaks last week
def downloadOutbreaks():
    return 0

#Main

def main(argv):

    df = loadOutbreaks()
    webScarpping(df)


    return 0



if __name__ == '__main__':
    main(sys.argv[1:])

