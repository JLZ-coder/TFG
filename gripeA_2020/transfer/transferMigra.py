
class transferMigra:

    def __init__(self,especie,fecha_anill,fecha_recu,long,lat,geohash,longR,latR,geohashR, index):
        self._especie = especie
        self._fecha_anill = fecha_anill
        self._fecha_recu = fecha_recu
        self._long = long
        self._lat = lat
        self._geohash = geohash
        self._longR = longR
        self._latR = latR
        self._geohashR = geohashR
        self._index = index

    def get_especie(self):
        return self._especie
    def set_especie(self, arg):
        self._especie = arg

    def get_fecha_anill(self):
        return self._fecha_anill
    def set_fecha_anill(self, arg):
        self._fecha_anill = arg

    def get_fecha_recu(self):
        return self._fecha_recu
    def set_fecha_recu(self, arg):
        self._fecha_recu = arg

    def get_lat(self):
        return self._lat
    def set_lat(self, arg):
        self._lat = arg

    def get_long(self):
        return self._long
    def set_long(self, arg):
        self._long = arg

    def get_geohash(self):
        return self._geohash
    def set_geohash(self, arg):
        self._geohash = arg

    def get_longR(self):
        return self._longR
    def set_longR(self, arg):
        self._longR = arg

    def get_latR(self):
        return self._latR
    def set_latR(self, arg):
        self._latR = arg

    def get_geohashR(self):
        return self._geohashR
    def set_geohashR(self, arg):
        self._geohashR = arg

    def get_index(self):
        return self._index
    def set_index(self, arg):
        self._index = arg