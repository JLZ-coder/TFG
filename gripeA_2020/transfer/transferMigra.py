
class transferMigra:

    def __init__(self,data = {}):
        self._Especie = data['Especie']
        self._FechaAnillamiento = data['FechaAnillamiento']
        self._FechaRecuperacion = data['FechaRecuperacion']
        self._Long = data['Long']
        self._Lat = data['Lat']
        self._geohash = data['geohash']
        self._LongR = data['LongR']
        self._LatR = data['LatR']
        self._geohashR = data['geohashR']
        self._index = data['index']

    def get_Especie(self):
        return self._Especie
    def set_Especie(self, arg):
        self._Especie = arg

    def get_FechaAnillamiento(self):
        return self._FechaAnillamiento
    def set_FechaAnillamiento(self, arg):
        self._FechaAnillamiento = arg

    def get_FechaRecuperacion(self):
        return self._FechaRecuperacion
    def set_FechaRecuperacion(self, arg):
        self._FechaRecuperacion = arg

    def get_Lat(self):
        return self._Lat
    def set_Lat(self, arg):
        self._Lat = arg

    def get_Long(self):
        return self._Long
    def set_Long(self, arg):
        self._Long = arg

    def get_geohash(self):
        return self._geohash
    def set_geohash(self, arg):
        self._geohash = arg

    def get_LongR(self):
        return self._LongR
    def set_LongR(self, arg):
        self._LongR = arg

    def get_LatR(self):
        return self._LatR
    def set_LatR(self, arg):
        self._LatR = arg

    def get_geohashR(self):
        return self._geohashR
    def set_geohashR(self, arg):
        self._geohashR = arg

    def get_index(self):
        return self._index
    def set_index(self, arg):
        self._index = arg