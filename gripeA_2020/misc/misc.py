# Saca geohash de 3 digitos que caen en espana
def geohashEsp():
    cursor = com.find({})
    geoESP = set()
    geoComar = {}

    for it in cursor:
        geo = geohash.encode(float(it['Latitud']), float(it['Longitud']))
        geoESP.add(geo[0:3])

        if geo[0:4] not in geoComar:
            geoComar[geo[0:4]] = [it['CPROyMUN']]
        else:
            geoComar[geo[0:4]].append(it['CPROyMUN'])

    return geoESP, geoComar