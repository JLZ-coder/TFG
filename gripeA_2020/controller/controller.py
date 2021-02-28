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
        comarca_brotes, lista_brotes = self.dataFactory.createData("outbreak", outbreakStart, start,None)
        #tMin = self.dataFactory.createData("temp",start, end, comarca_brotes)
        comarcas_dict = self.dataFactory.createData("comarcas", None, None, None)
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2)

        parameters= dict()
        parameters['comarca_brotes']= comarca_brotes
        #parameters['tMin'] = tMin
        parameters['matrizEspecies'] = matrizEspecies

        alertas_list = list()

        self.model.setParameters(parameters)

        if dateM != None:
            alertas = self.model.run(start,end)
            alertas_list.append(alertas)
        else:
            i = 0
            while (i < weeks):
                alertas = self.model.run(start,end)
                alertas_list.append(alertas)
                start = end
                end = start + timedelta(weeks = 1)
                i += 1

        geojson_alerta = self.geojsonGen.generate_comarca(alertas_list, comarcas_dict)
        geojson_outbreak = self.geojsonGen.generate_outbreak(lista_brotes)
        geojson_migration = self.geojsonGen.generate_migration(comarca_brotes, comarcas_dict)

        text_file = open("brotes.geojson", "w")
        n = text_file.write(json.dumps(geojson_outbreak))
        text_file.close()
        text_file = open("migras.geojson", "w")
        n = text_file.write(json.dumps(geojson_migration))
        text_file.close()
        text_file = open("alertas.geojson", "w")
        n = text_file.write(json.dumps(geojson_alerta))
        text_file.close()

        return 0
