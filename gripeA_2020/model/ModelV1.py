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
        alertas["alertas"] = []

        #Modelo
        nAlerta = 0
        for comarca, brotes in parameters['comarca_brotes'].items():
            nAlerta = 0 
            for brote in brotes:  #Calculamos el nivel de Alerta de cada comarca segun los brotes asociados
                contrBrote = 0

                #Calculamos la probabildad de migracion de la semana anterior
                weekA = start - timedelta(weeks=1)
                #week = weekA.isocalendar()[1]-1
                week = int(((weekA - datetime(weekA.year,1,1)).days / 7) + 1)
                i = 0
                nextWeek = week
                while nextWeek == week:
                    #Aumento en 1 el dia
                    weekA = weekA + timedelta(days=1)
                    #Recalculo la semana
                    nextWeek = int(((weekA - datetime(weekA.year,1,1)).days / 7) + 1)
                    #Contador
                    i+=1            

                probMigra = (parameters['matrizEspecies'][week][brote["especie"]] * i + parameters['matrizEspecies'][nextWeek][brote["especie"]] * (7-i)) / 7
                
                probType = 0

                if brote['epiunit']== "Farm":
                    probType = 0.1
                elif brote['epiunit']== "Backyard":
                    probType = 0.3
                else:
                    probType = 1
                
                contrBrote = (probMigra/100)*probType
                nAlerta += contrBrote

            #Calculamos la semana actual
            try:
                week = start.isocalendar()[1]-1
                temperaturaM = 66 if (parameters['tMin'][comarca][str(start.year)][week] <= 0.0) else (-7.82* ln(parameters['tMin'][comarca][str(start.year)][week])) + 29.94
                #alertas["alertas"].append({"comarca_sg" : comarca, "risk" : nAlerta * temperaturaM})
                alertas["alertas"].append({"comarca_sg" : comarca, "risk" : nAlerta})
            except: 
                print("No hay temperatura para la comarca: " + comarca) 
           
        return alertas
