import string
from pymongo import MongoClient
import pygeohash as geohash
import sys
import json

# Realiza las tablas geoComarca (Lista de todos los geohashes de españa junto con sus comarcas) y comarcaGeo (todas las comarcas junto con sus
# geohash)

client = MongoClient('mongodb://localhost:27017/')
db = client.lv
comarcas = db.comarcas

def getDigits():
    digits = list(string.ascii_lowercase)
    no_digits = ['a', 'o', 'l', 'i']

    for i in digits:
        if i in no_digits:
            digits.remove(i)

    for i in range(10):
        digits.append(str(i))


    return digits

# Saca geohash de 3 digitos que caen en espana
def geohashEsp():
    cursor = comarcas.find({})
    geoESP = set()
    comar = {}

    for it in cursor:
        geo = geohash.encode(float(it['Latitud']), float(it['Longitud']))
        geoESP.add(geo[0:3])

        comar.update( {
            it['comarca_sg'] :
                {
                    "comarca_sg" : it['comarca_sg'],
                    "com_sgsa_n" : it['com_sgsa_n'],
                    "long" : it['Longitud'] ,
                    "lat" : it['Latitud'] ,
                    "cpro" : it['CPRO'] ,
                    "provincia" : it['provincia'] ,
                    "cproymun" : it['CPROyMUN'] ,
                    "geohash" : it['geohash'] ,
                    "izqS" : it['izqS'] ,
                    "derI" : it['derI']
                }
        } )

    return geoESP, comar


# Lista de geohash 3 de espana

# Recorre la lista de geohash 3 y para cada uno recorre todos los geohashes de n>3 digitos y devuelve las comarcas que "pisa" junto con su peso

# Devuelve un fichero con diccionario "geohash --> {comarcas, peso}"
def geo_comarcas_gen(lista, max_n, comar):
    if max_n <= 3:
        raise Exception("Usando geohash demasiados grandes en geo_comarcas()")

    digits = getDigits()

    collect = {}

    for it in lista:
        collect.update( geo_comarcas(it, 3, max_n, digits, comar) )

    return collect

def overlapPropLat(geoboxLat, comarboxLat):
    if geoboxLat[1] > comarboxLat[0] and comarboxLat[1] > geoboxLat[0]:
        sup = min(geoboxLat[1], comarboxLat[1])
        bot = max(comarboxLat[0], geoboxLat[0])

        return sup - bot
    else:
        return 0

def overlapPropLong(geoboxLong, comarboxLong):
    if geoboxLong[1] > comarboxLong[0] and comarboxLong[1] > geoboxLong[0]:
        sup = min(geoboxLong[1], comarboxLong[1])
        bot = max(comarboxLong[0], geoboxLong[0])

        return sup - bot
    else:
        return 0

# eqwr : [ {sp12300 : 0.4}, ... ]
def geo_comarcas(geo, n, max_n, digits, comar):
    if len(geo) == max_n:
        lat, long, lat_err, long_err = geohash.decode_exactly(geo)

        lat_range = (lat - lat_err, lat + lat_err)
        long_range = (long - long_err, long + long_err)

        collect = {geo : []}

        for it in comar.keys():
            lat_range_mongo = (comar[it]['derI'][1], comar[it]['izqS'][1])
            long_range_mongo = (comar[it]['izqS'][0], comar[it]['derI'][0])

            base = overlapPropLong(long_range, long_range_mongo)
            altura = overlapPropLat(lat_range, lat_range_mongo)
            if base and altura:
                area = base * altura
                areaGeo = (long_range[1] - long_range[0]) * (lat_range[1] - lat_range[0])
                peso = area / areaGeo
                collect[geo].append({"cod_comarca" : it, "peso" : peso})

        return collect
    else:
        collect = {}

        for digit in digits:
            collect.update( geo_comarcas(geo + digit, n + 1, max_n, digits, comar) )

        return collect

# sp12300 : [ {ezqr : 0.4}, ... ]
def comarcas_geo(tablaGeoComarca, comar):
    tablaComarcaGeo = {}

    for i in tablaGeoComarca.keys():
        for j in tablaGeoComarca[i]:
            cod_comar = j['cod_comarca']
            peso = j['peso']

            if cod_comar in tablaComarcaGeo:
                tablaComarcaGeo[cod_comar].append({"geohash" : i, "peso" : peso})
            else:
                tablaComarcaGeo[cod_comar] = [{"geohash" : i, "peso" : peso}]


    return tablaComarcaGeo

def generaTablas():

    geoEsp, comar = geohashEsp()
    tablaGeoComarca = geo_comarcas_gen(geoEsp, 4, comar)
    tablaComarcaGeo = comarcas_geo(tablaGeoComarca, comar)

    return tablaGeoComarca, tablaComarcaGeo

def main(argv):

    tablaGeoComarca, tablaComarcaGeo = generaTablas()
    text_file = open("tablaGeoComarca.txt", "w")
    n = text_file.write(json.dumps(tablaGeoComarca))
    text_file.close()

    text_file = open("tablaComarcaGeo.txt", "w")
    n = text_file.write(json.dumps(tablaComarcaGeo))
    text_file.close()


if __name__ == "__main__":
    main(sys.argv[1:])
