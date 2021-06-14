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

    def prob_week_days(self, week_start):
        # Pasamos la fecha al lunes de la semana, por si lo era
        week_start += timedelta(days = -week_start.weekday())

        current_date = week_start

        #Calculamos la columna con la probabildad de migracion de esta semana
        current_week = 4 * ( int(current_date.strftime("%m")) - 1 )
        extra_days = int( ( (int(current_date.strftime("%d")) - 1) / 7 ) + 1)
        if extra_days > 4:
            extra_days = 4
        # Columna de esta semana
        current_week += extra_days

        # Cuantos dias corresponden a esta semana y cuantos a la siguiente
        current_week_days = 0
        next_week = current_week
        #Hasta que no hayamos cambiado de semana o si despues de 7 dias no hemos cambiado de semana
        while next_week == current_week and current_week_days < 7:
            #Aumento en 1 el dia
            current_date += timedelta(days=1)

            #Recalculo la semana para ver si ha cambiado
            next_week = 4 * (int(current_date.strftime("%m")) - 1)
            extra_days = int( ( (int(current_date.strftime("%d")) - 1) / 7 ) + 1)
            if extra_days > 4:
                extra_days = 4
            next_week += extra_days

            #Contador
            current_week_days +=1

        next_week_days = 7 - current_week_days

        return current_week, current_week_days, next_week, next_week_days


    #data[comarca_brotes, matrizEspecies, tMin]
    def run(self, start, end, data, parameters):

        # Según los datos calcular las comarcaBrotes
        #comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(comarca_brotes[k]), reverse=True)
        alertas = dict()
        alertas["start"] = start
        alertas["end"] = end
        alertas["alertas"] = []
        alertas["nBrotes"] = 0

        semana = start.isocalendar()[1]-1
        #Calculamos la probabildad de migracion de la semana anterior
        thisWeek, thisWeek_days, nextWeek, nextWeek_days = self.prob_week_days(start)

        #Listas para pdf
        broteEspecie = dict()
        casosTotales = 0
        #Modelo
        nAlerta = 0
        #Csv
        totalMov = 0
        #Numero de brotes por comarca
        brote_por_comarca = set()
        # Para cada comarca
        for comarca, brotes in data['comarca_brotes'].items():
            nAlerta = 0

            broteEspecie.clear()
            casosTotales = 0
            totalMov = 0
            brote_por_comarca.clear()
            # Se recorren los brotes asociados a la comarca, se hace el sumatorio de los resultados de la formula (probMigra/100) * probType
            # probMigra, la probabilidad de que migra la especie de la ruta asociada a un brote
            # probType, la probabilidad asociada al tipo de brote (wild, captive, domestic)
            for brote in brotes:  #Calculamos el nivel de Alerta de cada comarca segun los brotes asociados
                contrBrote = 0

                probMigra = (data['matrizEspecies'][thisWeek][brote["especie"]] * thisWeek_days + data['matrizEspecies'][nextWeek][brote["especie"]] * nextWeek_days) / 7

                probType = 0

                if brote['epiunit']== "Domestic":
                    probType = self.domestic
                elif brote['epiunit']== "Captive":
                    probType = self.captive
                else:
                    probType = self.wild

                contrBrote = probMigra * probType
                nAlerta += contrBrote
                ruta = {"cientifico" : data['matrizEspecies']['Nombre científico'][brote["especie"]] ,
                "especie": data['matrizEspecies']['Especie'][brote["especie"]], "codigoE": brote["especie"], 
                "probEspecie": probMigra, "probType": probType, "riesgoBrote": contrBrote}

                if brote["oieid"] not in broteEspecie:
                    broteEspecie[brote["oieid"]] = [ruta]
                else:
                    broteEspecie[brote["oieid"]].append(ruta)

                brote_por_comarca.add(brote["oieid"])


                totalMov += brote["nMov"]
                if brote['casos'] != "":
                    casosTotales += brote['casos']



            temperaturaM = "No data"
            # Calculamos temperaturaM de la semana actual, resultado de la formula -7.82 * logneperiano(temp) + 29.94
            # temp, temperatura media minima de la semana para la comarca
            try:
                if data["online"] == False:
                    weekTemp = start.isocalendar()[1]-1
                    temperaturaM = 66 if (data['tMin'][comarca][str(start.year)][weekTemp] <= 0.0) else (-7.82* ln(data['tMin'][comarca][str(start.year)][weekTemp])) + 29.94
                else: #Si es online cogemos la prediccion
                    temperaturaM = 66 if (data['tMin'][comarca] <= 0.0) else (-7.82* ln(data['tMin'][comarca])) + 29.94

                # Saturamos a 66
                if temperaturaM > 66:
                    temperaturaM = 66

                riesgo = int(nAlerta * temperaturaM)
                valor_riesgo = nAlerta * temperaturaM
            except:
                data['tMin'][comarca] = "No data"
                riesgo = int(nAlerta)
                valor_riesgo = nAlerta
                print("No hay temperatura en la semana {} para la comarca {}".format(semana, comarca))

            alertas["alertas"].append({
                "comarca_sg" : comarca, 
                "risk" : riesgo,
                "valorRiesgo" : valor_riesgo, 
                "temperatura": data['tMin'][comarca],  
                "super": temperaturaM, 
                "brotes": broteEspecie.copy(),
                "movRiesgo": totalMov })
            alertas["nBrotes"] += len(brote_por_comarca)
        
        return alertas
