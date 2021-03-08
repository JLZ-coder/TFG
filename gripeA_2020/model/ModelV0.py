import math
from datetime import datetime, timedelta, date

class ModelV0():
    def __init__(self):
        self.tag = "modelv0"

    def create(self, tag):
        if (tag == self.tag):
            return self

    def changeProb(self, prob):
        return self

    def run(self, start, end, parameters):
        # Según los datos calcular las comarcaBrotes
        comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(parameters['comarca_brotes'][k]), reverse=True)
        alertas = dict()
        alertas["start"] = start
        alertas["end"] = end

        # Cuartiles
        alertaMax = 5
        porcentaje = 0.2
        percentil = math.ceil(len(comarca_brotes_sorted) * porcentaje)
        cont = 1
        for comarca in comarca_brotes_sorted:
            alertas[comarca] = {"nivel" : alertaMax}

            if cont == percentil:
                alertaMax -= 1
                porcentaje += 0.2
                percentil = math.ceil(len(comarca_brotes_sorted) * porcentaje)

            cont += 1

        return alertas
