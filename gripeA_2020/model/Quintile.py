import math
from datetime import datetime, timedelta, date

class Quintile:
    def __init__(self, dataFactory):
        self.dataFactory = dataFactory

    def run(self, start, end):
        outbreakStart = start - timedelta(days = 90)
        comarca_brotes = self.dataFactory.createData("outbreak", outbreakStart, start)
        # Según los datos calcular las comarcaBrotes
        comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(comarca_brotes[k]), reverse=True)
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
