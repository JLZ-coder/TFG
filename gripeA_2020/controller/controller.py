from datetime import datetime, timedelta, date
import pandas as pd
import os
import json
import copy

class Controller:
    def __init__(self, model,dataFactory, geojsonGen):
        self.model = model
        self.dataFactory = dataFactory
        self.geojsonGen = geojsonGen        
        
    def changeProb(self, prob):
        self.model.changeProb(prob)
    
    #DateM -> fecha referente
    #weeks -> semanas para generar alertas
    #temporaryWindow -> ventana temporal para busqueda de brotes por defecto 3 Meses/12 semanas/ 90 dias
    def run(self, dateM, weeks, temporaryWindow):

        if dateM != None:#Fecha Herramienta offline
            start = dateM + timedelta(days = -dateM.weekday())
            end = start + timedelta(weeks = 1)
        else: #Fecha actual
            today = date.today()
            start = today + timedelta(days = -today.weekday())
            end = start + timedelta(weeks = 1)

        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())

        #Parameters
        outbreakStart = start - timedelta(weeks = temporaryWindow)
        comarca_brotes, lista_brotes = self.dataFactory.createData("outbreak", outbreakStart, start,None)
        tMin = self.dataFactory.createData("temp",start, end, comarca_brotes)
        lista_comarcas = self.dataFactory.createData("comarcas", None, None, None)
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2)

        parameters= dict()
        parameters['comarca_brotes']= comarca_brotes
        parameters['tMin'] = tMin
        parameters['matrizEspecies'] = matrizEspecies


        brotes_por_semana = dict()
        brotes_por_semana = lista_brotes.copy()
        migrations_por_semana = dict()
        migrations_por_semana[start] = comarca_brotes

        alertas_list = list()

        self.model.setParameters(parameters)

        if dateM == None:
            alertas = self.model.run(start,end)
            alertas_list.append(alertas)
        else:
            i = 0
            while (i < weeks):
                alertas = self.model.run(start,end)
                alertas_list.append(alertas)
                start = end
                end = start + timedelta(weeks = 1)

                outbreakStart = start - timedelta(weeks = temporaryWindow)
                comarca_brotes, lista_brotes = self.dataFactory.createData("outbreak", outbreakStart, start,None)
                #tMin = self.dataFactory.createData("temp",start, end, comarca_brotes)
                lista_comarcas = self.dataFactory.createData("comarcas", None, None, None)

                parameters['comarca_brotes']= comarca_brotes
                #parameters['tMin'] = tMin
                parameters['matrizEspecies'] = matrizEspecies

                migrations_por_semana[start] = comarca_brotes
                brotes_por_semana[start - timedelta(weeks=1)] = lista_brotes[start - timedelta(weeks=1)].copy()

                i += 1

        geojson_alerta = self.geojsonGen.generate_comarca(alertas_list, lista_comarcas)
        geojson_outbreak = self.geojsonGen.generate_outbreak(brotes_por_semana)
        geojson_migration = self.geojsonGen.generate_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)

        return geojson_alerta



