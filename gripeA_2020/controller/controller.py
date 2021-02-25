from datetime import datetime, timedelta, date
import pandas as pd
import os

class Controller:
    def __init__(self, model,dataFactory, geojsonGen):
        self.model = model
        self.dataFactory = dataFactory
        self.geojsonGen = geojsonGen

    def run(self, dateM, weeks):

        if dateM != None:#Fecha Herramienta offline
            start = dateM + timedelta(days = -dateM.weekday()) - timedelta(weeks = weeks)
            end = start + timedelta(weeks = 1)
        else: #Fecha actual
            today = date.today()
            start = today + timedelta(days = -today.weekday())
            end = start + timedelta(weeks = 1)

        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())

        #Parameters
        outbreakStart = start - timedelta(days = 90)
        comarca_brotes = self.dataFactory.createData("outbreak", outbreakStart, start,None)
        tMin = self.dataFactory.createData("temp",start, end, comarca_brotes)
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2 )

        parameters= dict()
        parameters['comarca_brotes']= comarca_brotes
        parameters['tMin'] = tMin
        parameters['matrizEspecies'] = matrizEspecies

        alertas_collect = list()

        i = 0
        while (i < weeks):
            self.model.setParameters(parameters)
            alertas = self.model.run(start,end)
            alertas_collect.append(alertas)
            start = end
            end = start + timedelta(weeks = 1)
            i += 1

        geojson_alerta = self.geojsonGen.generate_comarca(alertas_collect)
        geojson_outbreak = self.geojsonGen.generate_outbreak(comarca_brotes)
        geojson_migration = self.geojsonGen.generate_migration(comarca_brotes)

        text_file = open("brotes.geojson", "w")
        n = text_file.write(json.dumps(geojson_outbreak))
        text_file.close()
        text_file = open("migras.geojson", "w")
        n = text_file.write(json.dumps(geojson_migration))
        text_file.close()
        text_file = open("alertas.geojson", "w")
        n = text_file.write(json.dumps(geojson_alerta))
        text_file.close()
