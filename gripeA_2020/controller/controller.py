from datetime import datetime, timedelta, date
import pandas as pd

class Controller:
    def __init__(self, model,dataFactory):
        self.model = model
        self.dataFactory = dataFactory

    def run(self, dateM, weeks):

        if dateM != None:#Fecha Herramienta offline
            start = dateM + timedelta(days = -dateM.weekday()) - timedelta(weeks = weeks)
            end = start + timedelta(weeks = 1)
        else: #Fecha actual
            today = date.today()
            start = today + timedelta(days = -today.weekday()) - timedelta(weeks = weeks)
            end = start + timedelta(weeks = 1)

        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())


        #Parameters
        outbreakStart = start - timedelta(days = 90)
        comarca_brotes = self.dataFactory.createData("outbreak", outbreakStart, start)
        tMin = self.dataFactory.createData("temp",start, end)
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2 )

        parameters= dict()
        parameters['comarca_brotes']= comarca_brotes
        parameters['tMin'] = tMin
        parameters['matrizEspecies'] = matrizEspecies


        alertas = self.model.run(start,end, parameters)
        
        '''
        i = 0

        while(i < weeks):
            alerta = self.model.run(start, end)
            alertas.append(alerta)
            start = end
            end = start + timedelta(weeks =1)
            i += 1

        '''
        return alertas
