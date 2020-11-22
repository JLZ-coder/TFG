
class transferBrote:

    def __init__(self,oieid,disease_id,serotype,report_date,end_date,urlFR,country,city,cases,epiunit, long, lat, geohash):
        self._oieid = oieid
        self._disease_id = disease_id
        self._serotype = serotype
        self._report_date = report_date
        self._end_date = end_date
        self._urlFR = urlFR
        self._country = country
        self._city = city
        self._cases = cases
        self._epiunit = epiunit
        self._long = long
        self._lat = lat
        self._geohash = geohash

    def get_oieid(self):
        return self._oieid
    def set_oieid(self, arg):
        self._oieid = arg

    def get_disease_id(self):
        return self._disease_id
    def set_disease_id(self, arg):
        self._disease_id = arg

    def get_serotype(self):
        return self._serotype
    def set_serotype(self, arg):
        self._serotype = arg

    def get_urlFR(self):
        return self._urlFR
    def set_urlFR(self, arg):
        self._urlFR = arg

    def get_report_date(self):
        return self._report_date
    def set_report_date(self, arg):
        self._report_date = arg

    def get_end_date(self):
        return self._end_date
    def set_end_date(self, arg):
        self._end_date = arg

    def get_country(self):
        return self._country
    def set_country(self, arg):
        self._country = arg

    def get_city(self):
        return self._city
    def set_city(self, arg):
        self._city = arg

    def get_cases(self):
        return self._cases
    def set_cases(self, arg):
        self._cases = arg

    def get_epiunit(self):
        return self._epiunit
    def set_epiunit(self, arg):
        self._epiunit = arg

    def get_long(self):
        return self._long
    def set_long(self, arg):
        self._long = arg

    def get_lat(self):
        return self._lat
    def set_lat(self, arg):
        self._lat = arg

    def get_geohash(self):
        return self._geohash
    def set_geohash(self, arg):
        self._geohash = arg