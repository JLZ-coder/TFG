
class transferComar:

    def __init__(self,comarca_sg,com_sgsa_n,long,lat,cpro,provincia,cproymun,geohash,izqS,derI):
        self._comarca_sg = comarca_sg
        self._com_sgsa_n = com_sgsa_n
        self._long = long
        self._lat = lat
        self._cpro = cpro
        self._provincia = provincia
        self._cproymun = cproymun
        self._geohash = geohash
        self._izqS = izqS
        self._derI = derI

    def get_comarca_sg(self):
        return self._comarca_sg
    def set_comarca_sg(self, arg):
        self._comarca_sg = arg

    def get_com_sgsa_n(self):
        return self._com_sgsa_n
    def set_com_sgsa_n(self, arg):
        self._com_sgsa_n = arg

    def get_long(self):
        return self._long
    def set_long(self, arg):
        self._long = arg

    def get_cpro(self):
        return self._cpro
    def set_cpro(self, arg):
        self._cpro = arg

    def get_lat(self):
        return self._lat
    def set_lat(self, arg):
        self._lat = arg

    def get_provincia(self):
        return self._provincia
    def set_provincia(self, arg):
        self._provincia = arg

    def get_cproymun(self):
        return self._cproymun
    def set_cproymun(self, arg):
        self._cproymun = arg

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