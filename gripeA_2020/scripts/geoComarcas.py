import string
from pymongo import MongoClient
import pygeohash as geohash

client = MongoClient('mongodb://localhost:27017/')
db = client.lv
comarcas = db.comarcas

# Saca geohash de 3 digitos que caen en espana
def geohashEsp():
    cursor = comarcas.find({})
    geoESP = set()
    comar = {}

    for it in cursor:
        geo = geohash.encode(float(it['Latitud']), float(it['Longitud']))
        geoESP.add(geo[0:3])

        # com = transferComar(
        #     comarca_sg=it['comarca_sg'],
        #     com_sgsa_n=it['com_sgsa_n'],
        #     long=it['Longitud'],
        #     lat=it['Latitud'],
        #     cpro=it['CPRO'],
        #     provincia=it['provincia'],
        #     cproymun=it['CPROyMUN'],
        #     geohash=it['geohash'],
        #     izqS=it['izqS'],
        #     derI=it['derI']
        # )
        comar.update( {
            it['comarca_sg'] : [
                { "comarca_sg" : it['comarca_sg'] },
                { "com_sgsa_n" : it['com_sgsa_n'] },
                { "long" : it['Longitud'] },
                { "lat" : it['Latitud'] },
                { "cpro" : it['CPRO'] },
                { "provincia" : it['provincia'] },
                { "cproymun" : it['CPROyMUN'] },
                { "geohash" : it['geohash'] },
                { "izqS" : it['izqS'] },
                { "derI" : it['derI'] }
            ]
        } )

    return geoESP, comar


# Lista de geohash 3 de espana

# Recorre la lista de geohash 3 y para cada uno recorre todos los geohashes de n>3 digitos y devuelve las comarcas que "pisa" junto con su peso

# Devuelve un fichero con diccionario "geohash --> {comarcas, peso}"
def geo_comarcas_gen(lista, n):
    if n <= 3:
        raise Exception("Usando geohash demasiados grandes en geo_comarcas()")

    digits = list(string.ascii_lowercase)
    no_digits = ['a', 'o', 'l', 'i']

    for i in digits:
        if i in no_digits:
            digits.remove(i)

    digits.append(range(10))

    collect = {}

    for it in lista:
        collect.update( geo_comarcas(it, n, digits, comar) )

    return collect

def overlapsLat(y1, y2):
    if y1[1]
    return = xmax1 >= xmin2 and xmax2 >= xmin1

def overlapsLong(x1, x2):


def geo_comarcas(geo, n, digits, comar):
    if len(geo) == n:
        lat, long, lat_err, long_err = geohash.decode_exactly(geo)

        lat_range = (lat - lat_err, lat + lat_err)
        long_range = (long - long_err, long + long_err)

        # if lat - lat_err < lat + lat_err:
        #     lat_range = (lat - lat_err, lat + lat_err)
        # else:
        #     lat_range = (lat + lat_err, lat - lat_err)

        # if long - long_err < long + long_err:
        #     long_range =  (long - long_err, long + long_err)
        # else:
        #     long_range =  (long + long_err, long - long_err)


        for it in comar.keys():
            lat_range_mongo = (comar[it]['derI'][1], comar[it]['izqS'][1])
            long_range_mongo = (comar[it]['izqS'][0], comar[it]['derI'][0])
            # if comar[it]['izqI'][1] < comar[it]['izqS'][1]:
            #     lat_range_mongo = (comar[it]['izqI'][1], comar[it]['izqS'][1])
            # else:
            #     lat_range_mongo = (comar[it]['izqS'][1], comar[it]['izqI'][1])

            # if comar[it]['izqI'][0] < comar[it]['derI'][0]:
            #     long_range_mongo =  (comar[it]['izqI'][0], comar[it]['derI'][0])
            # else:
            #     long_range_mongo =  (comar[it]['derI'][0], comar[it]['izqI'][0])

            if (
                    (lat_range[0] < comar[it]['izqS'][1] and comar[it]['izqS'][1] < lat_range[1])
                    or
                    (lat_range[0] < comar[it]['izqI'][1] and comar[it]['izqI'][1] < lat_range[1])
                    or
                    (lat_range_mongo[0] < lat_range[0] and lat_range[0] < lat_range_mongo[1])
                ) and (
                    (long_range[0] < comar[it]['izqI'][0] and comar[it]['izqI'][0] < long_range[1])
                    or
                    (long_range[0] < comar[it]['derI'][0] and comar[it]['derI'][0] < long_range[1])
                    or
                    (long_range_mongo[0] < long_range[0] and long_range[0] < long_range_mongo[1])
                ):
                pass
    else:
        collect = {}

        for digit in digits:
            collect.update( geo_comarcas(geo + digit, n + 1, digits, comar) )

        return collect

geoEsp, comar = geohashEsp()

