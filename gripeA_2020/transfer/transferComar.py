
class transferComar:

    def __init__(self,data = {}):
        self._comarca_sg = data['comarca_sg']
        self._com_sgsa_n = data['com_sgsa_n']
        self._Longitud = data['Longitud']
        self._Latitud = data['Latitud']
        self._CPRO = data['CPRO']
        self._provincia = data['provincia']
        self._CPROyMUN = data['CPROyMUN']
        self._geohash = data['geohash']
        self._izqS = data['izqS']
        self._derI = data['derI']

    def get_comarca_sg(self):
        return self._comarca_sg
    def set_comarca_sg(self, arg):
        self._comarca_sg = arg

    def get_com_sgsa_n(self):
        return self._com_sgsa_n
    def set_com_sgsa_n(self, arg):
        self._com_sgsa_n = arg

    def get_Longitud(self):
        return self._Longitud
    def set_Longitud(self, arg):
        self._Longitud = arg

    def get_CPRO(self):
        return self._CPRO
    def set_CPRO(self, arg):
        self._CPRO = arg

    def get_Latitud(self):
        return self._Latitud
    def set_Latitud(self, arg):
        self._Latitud = arg

    def get_provincia(self):
        return self._provincia
    def set_provincia(self, arg):
        self._provincia = arg

    def get_CPROyMUN(self):
        return self._CPROyMUN
    def set_CPROyMUN(self, arg):
        self._CPROyMUN = arg

    def get_geohash(self):
        return self._geohash
    def set_geohash(self, arg):
        self._geohash = arg

    def get_izqS(self):
        return self._izqS
    def set_izqS(self, arg):
        self._izqS = arg

    def get_derI(self):
        return self._derI
    def set_derI(self, arg):
        self._derI = arg