import math
from datetime import datetime
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
                semana = int(((end - datetime(end.year,1,1)).days / 7) + 1)
                probMigra = parameters['matrizEspecies'][semana-1][brote["especie"]]
                
                probTipo = 0

                if brote['datos']['epiunit']== "Farm":
                    probTipo = 0.1
                elif brote['datos']['epiunit']== "Backyard":
                    probTipo = 0.3
                else:
                    probTipo = 1
                
                contrBrote = (probMigra/100)*probTipo
                nAlerta += contrBrote

            temperaturaM = parameters['tMin']
            alertas[comarca] = nAlerta * temperaturaM

            

        return alertas
