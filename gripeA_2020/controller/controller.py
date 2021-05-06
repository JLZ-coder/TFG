from datetime import datetime, timedelta, date
import pandas as pd
import os
import json
import copy
from model.gdriveUploader import gDriveUploader

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
    def runOfflineTool(self, dateM, weeks, temporaryWindow = None):

        #Semana actual
        start = None
        if dateM != None:
            start = dateM + timedelta(days = -dateM.weekday())
        else:
            start = date.today() + timedelta(days = -date.today().weekday())

        this_many_weeks = weeks
        #start -= timedelta(weeks=this_many_weeks)
        end = start + timedelta(weeks = this_many_weeks)

        #Convert to datetime
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())

        #DATA SENT TO MODEL

        #Outbreaks
        # brotes_por_semana
        # 2020/01/01 => list(brotes en esta semana)
        # 2020/01/08 => list(brotes en esta semana)
        # ...
        # ..
        # .
        # comarca_brotes
        # *Codigo de una comarca* => list(info de brotes que llegan a esta comarca)
        # ...
        # ..
        # .

        # 12 semanas = 84 dias = aprox. 3 meses
        # outbreakStart = start - timedelta(weeks = 12)
        # comarca_brotes, brotes_por_semana = self.dataFactory.createData("outbreak", outbreakStart, end , None)

        #Temperature
        #tMin = self.dataFactory.createData("temp",start, end, True)

        #Comarca
        lista_comarcas = self.dataFactory.createData("comarcas", None, None, None)

        #Probabilidad Migracion
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2)

        #DATA SENT TO MODEL
        data_to_model= dict()
        # data_to_model['comarca_brotes']= comarca_brotes
        # data_to_model['tMin'] = tMin
        data_to_model['matrizEspecies'] = matrizEspecies
        data_to_model['online'] = True

        #Geojson generator
        migrations_por_semana = dict()
        brotes_por_semana = dict()
        alertas_list = list()

        comarcas_en_riesgo = set()

        i = 0
        current_week = start
        current_week_end = current_week + timedelta(weeks=1)
        while (i <= this_many_weeks):
            print("Run model para semana " + str(current_week))
            # 12 semanas = 84 dias = aprox. 3 meses
            outbreakStart = current_week - timedelta(weeks = 12)
            # brotes_por_semana_aux no se usa
            comarca_brotes, brotes_esta_semana = self.dataFactory.createData("outbreak", outbreakStart, current_week_end , None)
            #brotes_por_semana[current_week] = brotes_esta_semana

            #Si está vacio añadimos todos los 3 primeros meses de brotes
            if len(brotes_por_semana) == 0:
                brotes_por_semana = brotes_esta_semana
            else: #Al diccionario con todos los brotes añadimos la de la última semana ya que el resto es igual
                brotes_por_semana[current_week] = brotes_esta_semana[current_week]

            #Temperature
            tMin = self.dataFactory.createData("temp",current_week, current_week_end, True)

            #DATA SENT TO MODEL
            data_to_model['comarca_brotes']= comarca_brotes
            data_to_model['tMin'] = tMin

            # RUN MODEL
            self.model.setData(data_to_model)
            alertas = self.model.run(current_week, current_week_end)

            alertas_esp = list(filter(lambda alerta: alerta["comarca_sg"] == "SP49108", alertas["alertas"]))
            alertas_list_esp = list()
            alertas_list_esp.append(alertas_esp)

            # Quitamos las alertas de riesgo 0
            alertas["alertas"] = list(filter(lambda alerta: alerta["risk"] != 0, alertas["alertas"]))

            alertas_list.append(alertas)

            # Para seleccionar solo las rutas de comarcas en riesgo > 0
            # -----------------------------------------------------------
            comarcas_en_riesgo.clear()
            for alerta in alertas["alertas"]:
                if current_week not in migrations_por_semana:
                    migrations_por_semana[current_week] = {}

                migrations_por_semana[current_week][alerta["comarca_sg"]] = comarca_brotes[alerta["comarca_sg"]]

            # for comarca in comarca_brotes:
            #     if comarca in comarcas_en_riesgo:
            #         if current_week not in migrations_por_semana:
            #             migrations_por_semana[current_week] = {}

            #         migrations_por_semana[current_week][comarca] = comarca_brotes[comarca]
            # -----------------------------------------------------------

            print(">>> Alertas total: " + str(len(alertas["alertas"])))
            for alertas in alertas_list_esp:
                for alerta in alertas:
                    print (alerta["comarca_sg"])

            # Rellenar el informe semanal
            # reportPDF = self.dataFactory.createData("report",current_week, current_week_end, alertas)

            #Actualizar current_week y current_week_end
            current_week = current_week_end
            current_week_end = current_week + timedelta(weeks = 1)
            i += 1

        geojson_alerta = self.geojsonGen.generate_alerta(alertas_list, lista_comarcas)
        geojson_outbreak = self.geojsonGen.generate_outbreak(brotes_por_semana)
        geojson_migration = self.geojsonGen.generate_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)


        return geojson_alerta

    def runOnlineTool(self):
        #Semana actual
        start = date.today() + timedelta(days = -date.today().weekday())
        #Fecha hace 364 dias, 52 semanas
        this_many_weeks = 0
        start -= timedelta(weeks=this_many_weeks)
        end = start + timedelta(weeks = this_many_weeks)

        #Convert to datetime
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())

        #DATA SENT TO MODEL

        #Outbreaks
        # brotes_por_semana
        # 2020/01/01 => list(brotes en esta semana)
        # 2020/01/08 => list(brotes en esta semana)
        # ...
        # ..
        # .
        # comarca_brotes
        # *Codigo de una comarca* => list(info de brotes que llegan a esta comarca)
        # ...
        # ..
        # .

        # 12 semanas = 84 dias = aprox. 3 meses
        # outbreakStart = start - timedelta(weeks = 12)
        # comarca_brotes, brotes_por_semana = self.dataFactory.createData("outbreak", outbreakStart, end , None)

        #Temperature
        #tMin = self.dataFactory.createData("temp",start, end, True)

        #Comarca
        lista_comarcas = self.dataFactory.createData("comarcas", None, None, None)

        #Probabilidad Migracion
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2)

        #DATA SENT TO MODEL
        data_to_model= dict()
        # data_to_model['comarca_brotes']= comarca_brotes
        # data_to_model['tMin'] = tMin
        data_to_model['matrizEspecies'] = matrizEspecies
        data_to_model['online'] = True

        #Geojson generator
        migrations_por_semana = dict()
        brotes_por_semana = dict()
        alertas_list = list()

        comarcas_en_riesgo = set()

        i = 0
        current_week = start
        current_week_end = current_week + timedelta(weeks=1)
        while (i <= this_many_weeks):
            print("Run model para semana " + str(current_week))
            # 12 semanas = 84 dias = aprox. 3 meses
            outbreakStart = current_week - timedelta(weeks = 12)
            # brotes_por_semana_aux no se usa
            comarca_brotes, brotes_esta_semana = self.dataFactory.createData("outbreak", outbreakStart, current_week_end , None)
            brotes_por_semana[current_week] = brotes_esta_semana

            #Temperature
            tMin = self.dataFactory.createData("temp",current_week, current_week_end, True)

            #DATA SENT TO MODEL
            data_to_model['comarca_brotes']= comarca_brotes
            data_to_model['tMin'] = tMin

            # RUN MODEL
            self.model.setData(data_to_model)
            alertas = self.model.run(current_week, current_week_end)

            # Quitamos las alertas de riesgo 0
            alertas["alertas"] = list(filter(lambda alerta: alerta["risk"] != 0, alertas["alertas"]))

            alertas_list.append(alertas)

            # Para seleccionar solo las rutas de comarcas en riesgo > 0
            # -----------------------------------------------------------
            comarcas_en_riesgo.clear()
            for alerta in alertas["alertas"]:
                if current_week not in migrations_por_semana:
                    migrations_por_semana[current_week] = {}

                migrations_por_semana[current_week][alerta["comarca_sg"]] = comarca_brotes[alerta["comarca_sg"]]

            # for comarca in comarca_brotes:
            #     if comarca in comarcas_en_riesgo:
            #         if current_week not in migrations_por_semana:
            #             migrations_por_semana[current_week] = {}

            #         migrations_por_semana[current_week][comarca] = comarca_brotes[comarca]
            # -----------------------------------------------------------

            print(">>> Alertas total: " + str(len(alertas["alertas"])))
            print(">>> Alertas con rutas en cuenta: " + str(len(comarcas_en_riesgo)))

            # Rellenar el informe semanal
            reportPDF = self.dataFactory.createData("report",current_week, current_week_end, alertas)

            #Actualizar current_week y current_week_end
            current_week = current_week_end
            current_week_end = current_week + timedelta(weeks = 1)
            i += 1

        geojson_alerta = self.geojsonGen.update_alerta(alertas_list, lista_comarcas)
        geojson_outbreak = self.geojsonGen.update_outbreak(brotes_por_semana)
        geojson_migration = self.geojsonGen.update_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)

        return 0

    def runOnlineTool_1year(self):
        #Semana actual
        start = date.today() + timedelta(days = -date.today().weekday())
        #Fecha hace 364 dias, 52 semanas
        this_many_weeks = 52
        start -= timedelta(weeks=this_many_weeks)
        end = start + timedelta(weeks = this_many_weeks)

        #Convert to datetime
        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())

        #DATA SENT TO MODEL

        #Outbreaks
        # brotes_por_semana
        # 2020/01/01 => list(brotes en esta semana)
        # 2020/01/08 => list(brotes en esta semana)
        # ...
        # ..
        # .
        # comarca_brotes
        # *Codigo de una comarca* => list(info de brotes que llegan a esta comarca)
        # ...
        # ..
        # .

        # 12 semanas = 84 dias = aprox. 3 meses
        # outbreakStart = start - timedelta(weeks = 12)
        # comarca_brotes, brotes_por_semana = self.dataFactory.createData("outbreak", outbreakStart, end , None)

        #Temperature
        #tMin = self.dataFactory.createData("temp",start, end, True)

        #Comarca
        lista_comarcas = self.dataFactory.createData("comarcas", None, None, None)

        #Probabilidad Migracion
        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2)

        #DATA SENT TO MODEL
        data_to_model= dict()
        # data_to_model['comarca_brotes']= comarca_brotes
        # data_to_model['tMin'] = tMin
        data_to_model['matrizEspecies'] = matrizEspecies
        data_to_model['online'] = True

        #Geojson generator
        migrations_por_semana = dict()
        brotes_por_semana = dict()
        alertas_list = list()

        comarcas_en_riesgo = set()

        i = 0
        current_week = start
        current_week_end = current_week + timedelta(weeks=1)
        while (i <= this_many_weeks):
            print("Run model para semana " + str(current_week))
            # 12 semanas = 84 dias = aprox. 3 meses
            outbreakStart = current_week - timedelta(weeks = 12)
            # brotes_por_semana_aux no se usa
            comarca_brotes, brotes_esta_semana = self.dataFactory.createData("outbreak", outbreakStart, current_week_end , None)
            brotes_por_semana[current_week] = brotes_esta_semana

            #Temperature
            tMin = self.dataFactory.createData("temp",current_week, current_week_end, True)

            #DATA SENT TO MODEL
            data_to_model['comarca_brotes']= comarca_brotes
            data_to_model['tMin'] = tMin

            # RUN MODEL
            self.model.setData(data_to_model)
            alertas = self.model.run(current_week, current_week_end)

            # Quitamos las alertas de riesgo 0
            alertas["alertas"] = list(filter(lambda alerta: alerta["risk"] != 0, alertas["alertas"]))

            alertas_list.append(alertas)

            # Para seleccionar solo las rutas de comarcas en riesgo > 0
            # -----------------------------------------------------------
            comarcas_en_riesgo.clear()
            for alerta in alertas["alertas"]:
                if current_week not in migrations_por_semana:
                    migrations_por_semana[current_week] = {}

                migrations_por_semana[current_week][alerta["comarca_sg"]] = comarca_brotes[alerta["comarca_sg"]]

            # for comarca in comarca_brotes:
            #     if comarca in comarcas_en_riesgo:
            #         if current_week not in migrations_por_semana:
            #             migrations_por_semana[current_week] = {}

            #         migrations_por_semana[current_week][comarca] = comarca_brotes[comarca]
            # -----------------------------------------------------------

            print(">>> Alertas total: " + str(len(alertas["alertas"])))

            # Rellenar el informe semanal
            reportPDF = self.dataFactory.createData("report",current_week, current_week_end, alertas)

            #Actualizar current_week y current_week_end
            current_week = current_week_end
            current_week_end = current_week + timedelta(weeks = 1)
            i += 1

        geojson_alerta = self.geojsonGen.generate_alerta(alertas_list, lista_comarcas)
        geojson_outbreak = self.geojsonGen.generate_outbreak(brotes_por_semana)
        geojson_migration = self.geojsonGen.generate_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)

        return 0



