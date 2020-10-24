import requests
import re
# este sys me suobra mucho y habrá que quitarlo
import sys
import time
import json
import pymongo
from pymongo import MongoClient
import pygeohash as geohash
from datetime import datetime

# Realiza el scraping de la web de wahis para recoger los brotes

# GLOBALS
client = MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks


def extract_data(page):
    out = ''
    p = re.compile('start of the event</td>[^>]+>(\d{1,2}/\d{1,2}/\d{4}).*?'
                   'Outbreak Status</td>[^>]+>(\w+).*?'
                   'resolution of the outbreak</td>[^>]+>(\d{1,2}/\d{1,2}/\d{4})?.*?'
                   'ta_left">[^<]+</td>[^>]+>(\w+)?.*?'
                   'ta_left">[^<]+</td>[^>]+>(\w+)?.*?'
                   'ta_left">[^<]+</td>[^>]+>(\w+)?.*?'
                   'Unit Type</td>[^>]+>(\w+).*?'
                   'Location</td>[^>]+>(\w+).*?'
                   'Latitude</td>[^>]+>(-?\d+\.\d+).*?'
                   'Longitude</td>[^>]+>(-?\d+\.\d+).*?'
                   'Description of Affected Population</td>[^>]+>(.*?)</td>', re.DOTALL & re.MULTILINE * re.IGNORECASE)

    m = p.findall(page)

    if len(m) > 0:
        out = m[0]
    else:
        out = ('', '', '', '', '', '', '', '', '', '', '')

    p = re.compile('vacborder">([^<]*)?</td>.*?'
                   'vacborder">(\d+)?</td>.*?'
                   'vacborder">(\d+)?</td>.*?'
                   'vacborder">(\d+)?</td>.*?'
                   'vacborder(?: last)?">(\d+)?</td>.*?', re.DOTALL & re.MULTILINE * re.IGNORECASE)
    m = p.findall(page)
    return out, m


# recoge la informacion y lo mete en el db mongodb
def get_ob_page(cty, id, lista, disease, year):
    global outbreaks
    url = 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary/outbreakreport'
    r = requests.post(url, data={'reportid': id, 'summary_country': cty})
    ob, anlist = extract_data(r.content.decode('latin1'))
# extrae los detalles en la pagina de 'url', ob

    if  ob[0] != "" and ob[8] != "" and ob[9] != "":
        start = datetime.strptime(ob[0], "%d/%m/%Y")
        hash = geohash.encode(float(ob[8]), float(ob[9]))

        if ob[1] == 'Resolved' and outbreaks.find({'oieid': id}).count() == 0:
            print("Ignorando caso resuelto")
            pass

        elif ob[1] == 'Resolved' and outbreaks.find({'oieid': id}).count() != 0:
            print("Borrando caso resuelto {}".format(id))
            outbreaks.delete_one({'oieid':  id})

        else:
            outbreak = {}
            outbreak["oieid"] = id
            outbreak["diseade_id"] = disease
            outbreak["country"] = cty
            outbreak["start"] = start
            outbreak["status"] = ob[1]
            outbreak["city"] = ob[3]
            outbreak["district"] = ob[4]
            outbreak["subdistrict"] = ob[5]
            outbreak["epiunit"] = ob[6]
            outbreak["location"] = ob[7]
            outbreak["lat"] = ob[8]
            outbreak["long"] = ob[9]
            outbreak["affected_population"] = ob[10]
            outbreak["geohash"] = hash
            if len(anlist) > 0:
                outbreak["species"] = anlist[0][0]
                outbreak["at_risk"] = anlist[0][1]
                outbreak["cases"] = anlist[0][2]
                outbreak["deaths"] = anlist[0][3]
                outbreak["preventive_killed"] = anlist[0][4]
            else:
                outbreak["species"] = ""
                outbreak["at_risk"] = ""
                outbreak["cases"] = ""
                outbreak["deaths"] = ""
                outbreak["preventive_killed"] = ""

            print("Metiendo caso sin resolver {}".format(id))
            outbreaks.delete_one({'oieid': id})
            outbreaks.insert_one(outbreak)


# lista los brotes que ha habido en un pais
# code - codigo de un pais
# id - id de una lista de brotes
# disease - codigo de la enfermedad
# year - año del brote
def get_cty_obs(code, id, disease, year):
    # global ob_ids
    global db
    global outbreaks

    lista = []
    url = 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary/listoutbreak'
    r = requests.post(url, data={'reportid': id, 'summary_country': code})
    p = re.compile('outbreak_report\("([A-Z]{3})",([0-9]+)\)', re.DOTALL & re.MULTILINE * re.IGNORECASE)
    ob_list = p.findall(r.content.decode('latin1'))
# cogiendo informacion de 'url', pagina que sale al pulsar el boton de lupa en la pagina principal
    print('Getting data for outbreak of disease {} in country {}'.format(id, code))
    # total = len(ob_list)
    # count = 1
# itera en la lista de brotes de un pais
    for ob in ob_list:
        cty, id = ob
        get_ob_page(cty, id, lista, disease, year)


def main(argv):
    # 15 - Highli Path Avian influenza
    # 201 - Lowi Path Avian influenza
    # 1164 - Highly pathogenic influenza A viruses (infection with) (non-poultry including wild birds) (2017 -)
    diseases = ['15', '201', '1164']
    # global lista
    global disease
    asian_countries = ['AFG', 'ARM', 'AZE', 'BHR', 'BGD', 'BTN', 'CHN', 'CYP', 'KHM', 'TWN', 'GEO', 'HKG', 'IND', 'IDN', 'IRN',
                       'IRQ', 'ISR', 'JPN', 'JOR', 'KAZ', 'KOR', 'KWT', 'KGZ', 'LAO', 'LBN', 'MYS', 'MNG', 'MDV', 'MMR', 'PAK',
                       'NPL', 'OMN', 'PRK', 'PSE', 'PHL', 'QAT', 'RUS', 'SAU', 'SGP', 'LKA', 'SYR', 'TJK', 'TLS', 'THA', 'TUR',
                       'TKM', 'ARE', 'UZB', 'VNM', 'YEM']

    european_countries = ['ALB', 'DEU', 'AND', 'AUT', 'BEL', 'BLR', 'BIH', 'BGR', 'CYP', 'HRV', 'DNK', 'SVK', 'SVN', 'ESP', 'EST',
                          'FIN', 'FRA', 'GRC', 'HUN', 'IRL', 'ISL', 'ITA', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO',
                          'MNE', 'NOR', 'NLD', 'POL', 'PRT', 'GBR', 'CZE', 'ROU', 'RUS', 'SMR', 'SRB', 'SWE', 'CHE', 'UKR', 'VAT']

    url = 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary'

    #start_year = 2019
    #finish_year = 2020
    year = time.strftime("%Y")

    disease_type_hidden = 0  # Terrestrial
    # disease_id_hidden = 1 # FMD

    for disease_id in diseases:
        oblist = []
        disease = disease_id
        disease_id_terrestrial = disease_id
        disease_type = 0
        counter = 0
        payload = {'year': year,
                   'disease_type_hidden': disease_type_hidden,
                   'disease_id_hidden': disease_id,
                   'selected_disease_name_hidden': 'h',
                   'disease_type': disease_type,
                   'disease_id_terrestrial': disease_id_terrestrial,
                   'disease_id_aquatic': -999
                   }
        # r es la pagina de 'url' con los parametros de 'payload'
        r = requests.post(url, data=payload)
        # p busca patrones en 'r'
        p = re.compile(
           # "outbreak_country\">[ \t\r\n]+([A-Za-z \-.']+)[^(]*\('([A-Z]{3})',([0-9]+)\);"
           "color='red'>[ \t\r\n]+([A-Za-z \-.']+)[^(]*\('([A-Z]{3})',([0-9]+)\);"
            , re.DOTALL & re.MULTILINE)
        # m son las palabras que concuerdan con la busqueda de 'p'
        m = p.findall(r.content.decode('latin1'))
        # oblist [('Afghanistan', 'AFG', '25887'), ...] cty, code, id
        oblist = oblist + m

        #outbreaks.delete_many({'oieid': '1000097712'})

        counter = 1
        for obs in oblist:
            stat, code, id = obs
            print("\nOutbreak {} of {}".format(counter, len(oblist)))
            if((code in asian_countries) or (code in european_countries)) and (stat == "Continuing"):
                print("Getting Continuing Outbreak {} in {}".format(id, code))
                get_cty_obs(code, id, disease, year)
            counter += 1


if __name__ == "__main__":
    main(sys.argv[1:])
