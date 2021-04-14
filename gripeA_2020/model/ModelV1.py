import math
from datetime import datetime, timedelta
from numpy import log as ln
import math

class ModelV1():
    def __init__(self):
        self.tag = "modelv1"
        self.domestic = 0.1
        self.captive = 0.3
        self.wild = 1

    def create(self, tag):
        if (tag == self.tag):
            return self

    def changeProb(self, prob):
        self.domestic = prob[0]
        self.captive = prob[1]
        self.wild = prob[2]

    #data[comarca_brotes, matrizEspecies, tMin]
    def run(self, start, end, data, parameters):

        # Según los datos calcular las comarcaBrotes
        #comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(comarca_brotes[k]), reverse=True)
        alertas = dict()
        alertas["start"] = start
        alertas["end"] = end
        alertas["alertas"] = []
        alertas["nBrotes"] = 0

        #Calculamos la probabildad de migracion de la semana anterior
        weekA = start
        #week = weekA.isocalendar()[1]-1
        #week = int(((weekA - datetime(weekA.year,1,1)).days / 7) + 1)

        week = 4 * (int(weekA.strftime("%m")) - 1)
        days = int( ((int(weekA.strftime("%d")) - 1) / 7) + 1)
        if days > 4:
            days = 4
        week += days

        i = 0
        nextWeek = week
        while nextWeek == week and i < 7:
            #Aumento en 1 el dia
            weekA = weekA + timedelta(days=1)
            #Recalculo la semana
            #nextWeek = int(((weekA - datetime(weekA.year,1,1)).days / 7) + 1)
            nextWeek = 4 * (int(weekA.strftime("%m")) - 1)
            days = int( (int(weekA.strftime("%d")) - 1) / 7 + 1)
            if days > 4:
                days = 4
            nextWeek += days
            #Contador
            i+=1

        #Listas para pdf
        broteEspecie = dict()
        casosTotales = 0
        #Modelo
        nAlerta = 0
        for comarca, brotes in data['comarca_brotes'].items():
            nAlerta = 0 

            broteEspecie.clear()
            casosTotales = 0
            for brote in brotes:  #Calculamos el nivel de Alerta de cada comarca segun los brotes asociados
                contrBrote = 0

                probMigra = (data['matrizEspecies'][week][brote["especie"]] * i + data['matrizEspecies'][nextWeek][brote["especie"]] * (7-i)) / 7
                
                probType = 0

                if brote['epiunit']== "Domestic":
                    probType = self.domestic
                elif brote['epiunit']== "Captive":
                    probType = self.captive
                else:
                    probType = self.wild
                
                contrBrote = (probMigra/100)*probType
                nAlerta += contrBrote
                broteEspecie[brote["oieid"]] = {"cientifico" : data['matrizEspecies']['Nombre científico'][brote["especie"]] ,"especie": data['matrizEspecies']['Especie'][brote["especie"]], "codigoE": brote["especie"], "probEspecie": probMigra}

                if brote['casos'] != "":
                    casosTotales += brote['casos']

            temperaturaM = "No data"
            #Calculamos la semana actual
            try:
                if data["online"] == False:
                    weekTemp = start.isocalendar()[1]-1
                    temperaturaM = 66 if (data['tMin'][comarca][str(start.year)][weekTemp] <= 0.0) else (-7.82* ln(data['tMin'][comarca][str(start.year)][weekTemp])) + 29.94
                else: #Si es online cogemos la prediccion
                    temperaturaM = 66 if (data['tMin'][comarca] <= 0.0) else (-7.82* ln(data['tMin'][comarca])) + 29.94
                
                riesgo = int(nAlerta * temperaturaM)
            except: 
                riesgo = int(nAlerta)
                print("No hay temperatura para la comarca: " + comarca) 
           
            alertas["alertas"].append({"comarca_sg" : comarca, "risk" : riesgo, "temperatura": temperaturaM, "brotes": broteEspecie })
            alertas["nBrotes"] += len(broteEspecie)
        
        return alertas
