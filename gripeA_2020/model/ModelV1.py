import math
from datetime import datetime, timedelta
from numpy import log as ln
import math

class ModelV1():
    def __init__(self):
        self.tag = "modelv1"

    def create(self, tag):
        if (tag == self.tag):
            return self

    #Parameters[comarca_brotes, matrizEspecies, tMin]
    def run(self, start, end, parameters):

        # Según los datos calcular las comarcaBrotes
        #comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(comarca_brotes[k]), reverse=True)
        alertas = dict()
        alertas["start"] = start
        alertas["end"] = end

        #Modelo
        nAlerta = 0
        for comarca, brotes in parameters['comarca_brotes'].items():
            nAlerta = 0 
            for brote in brotes:  #Calculamos el nivel de Alerta de cada comarca segun los brotes asociados
                contrBrote = 0
                semanaA = start - timedelta(days=1)
                semana = semanaA.isocalendar()[1]-1

                probMigra = parameters['matrizEspecies'][semana][brote["especie"]]
                
                probTipo = 0

                if brote['epiunit']== "Farm":
                    probTipo = 0.1
                elif brote['epiunit']== "Backyard":
                    probTipo = 0.3
                else:
                    probTipo = 1
                
                contrBrote = (probMigra/100)*probTipo
                nAlerta += contrBrote

            print(math.log(parameters['tMin'][comarca]))
            temperaturaM = (-7.82* ln(parameters['tMin'][comarca])) + 29.94
            alertas[comarca] = nAlerta * temperaturaM

        return alertas
