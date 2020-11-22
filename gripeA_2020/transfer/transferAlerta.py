
class transferAlerta:

    def __init__(self,comarca,risk,cases,start,end,especie,code_especie,common_name,fluSubtype):
        self._comarca = comarca
        self._risk = risk
        self._cases = cases
        self._start = start
        self._end = end
        self._especie = especie
        self._code_especie = code_especie
        self._common_name = common_name
        self._fluSubtype = fluSubtype

    def get_comarca(self):
        return self._comarca
    def set_comarca(self, arg):
        self._comarca = arg

    def get_risk(self):
        return self._risk
    def set_risk(self, arg):
        self._risk = arg

    def get_cases(self):
        return self._cases
    def set_cases(self, arg):
        self._cases = arg

    def get_end(self):
        return self._end
    def set_end(self, arg):
        self._end = arg

    def get_start(self):
        return self._start
    def set_start(self, arg):
        self._start = arg

    def get_especie(self):
        return self._especie
    def set_especie(self, arg):
        self._especie = arg

    def get_code_especie(self):
        return self._code_especie
    def set_code_especie(self, arg):
        self._code_especie = arg

    def get_common_name(self):
        return self._common_name
    def set_common_name(self, arg):
        self._common_name = arg

    def get_fluSubtype(self):
        return self._fluSubtype
    def set_fluSubtype(self, arg):
        self._fluSubtype = arg