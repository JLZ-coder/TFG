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
    def runOfflineTool(self, dateM=None, weeks=0):
        if dateM == None:
            #Semana actual
            start = date.today() + timedelta(days = -date.today().weekday())
            this_many_weeks = 0
            start -= timedelta(weeks=this_many_weeks)
            end = start + timedelta(weeks = this_many_weeks)
        else:
            #Semana actual
            start = dateM + timedelta(days = -dateM.weekday())
            # Desde "weeks" semanas atras hasta esta semana
            this_many_weeks = weeks
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

        i = 0
        current_week = start
        current_week_end = current_week + timedelta(weeks=1)

        while (i <= this_many_weeks):
            print("Run model para semana " + str(current_week))
            # 12 semanas = 84 dias = aprox. 3 meses
            outbreakStart = current_week - timedelta(weeks = 12)
            # brotes_por_semana_aux no se usa
            comarca_brotes, brotes_esta_semana = self.dataFactory.createData("outbreak", outbreakStart, current_week - timedelta(weeks=1) , None)
            
            #Si está vacio añadimos todos los 3 primeros meses de brotes
            if len(brotes_por_semana) == 0:
                brotes_por_semana = brotes_esta_semana
            else: #Al diccionario con todos los brotes añadimos la de la última semana ya que el resto es igual
                brotes_por_semana[current_week - timedelta(weeks=2)] = brotes_esta_semana[current_week - timedelta(weeks=2)]

            #Temperature
            tMin = self.dataFactory.createData("temp",current_week, current_week_end, True)

            #DATA SENT TO MODEL
            data_to_model['comarca_brotes']= comarca_brotes
            data_to_model['tMin'] = tMin

            # RUN MODEL
            self.model.setData(data_to_model)
            alertas = self.model.run(current_week, current_week_end)

            alertas_list.append(alertas)

            for alerta in alertas["alertas"]:
                if current_week not in migrations_por_semana:
                    migrations_por_semana[current_week] = {}

                migrations_por_semana[current_week][alerta["comarca_sg"]] = comarca_brotes[alerta["comarca_sg"]]

            print(">>> Alertas total: " + str(len(alertas["alertas"])))

            # Rellenar el informe semanal
            # reportPDF = self.dataFactory.createData("report",current_week, current_week_end, alertas)

            #Actualizar current_week y current_week_end
            current_week = current_week_end
            current_week_end = current_week + timedelta(weeks = 1)
            i += 1

        if dateM == None:
            geojson_alerta = self.geojsonGen.update_alerta(alertas_list, lista_comarcas)
            geojson_outbreak = self.geojsonGen.update_outbreak(brotes_por_semana)
            geojson_migration = self.geojsonGen.update_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)
        else:
            geojson_alerta = self.geojsonGen.generate_alerta(alertas_list, lista_comarcas)
            geojson_outbreak = self.geojsonGen.generate_outbreak(brotes_por_semana)
            geojson_migration = self.geojsonGen.generate_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)


        return geojson_alerta

    def runOnlineTool(self, weeks=0):
        #Semana actual
        start = date.today() + timedelta(days = -date.today().weekday())
        # Desde "weeks" semanas atras hasta esta semana
        this_many_weeks = weeks
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

        i = 0
        current_week = start
        current_week_end = current_week + timedelta(weeks=1)

        while (i <= this_many_weeks):
            print("Run model para semana " + str(current_week))
            # 12 semanas = 84 dias = aprox. 3 meses
            outbreakStart = current_week - timedelta(weeks = 12)
            # brotes_por_semana_aux no se usa
            comarca_brotes, brotes_esta_semana = self.dataFactory.createData("outbreak", outbreakStart, current_week - timedelta(weeks=1) , None)
            
            #Si está vacio añadimos todos los 3 primeros meses de brotes
            if len(brotes_por_semana) == 0:
                brotes_por_semana = brotes_esta_semana
            else: #Al diccionario con todos los brotes añadimos la de la última semana ya que el resto es igual
                brotes_por_semana[current_week - timedelta(weeks=2)] = brotes_esta_semana[current_week - timedelta(weeks=2)]

            #Temperature
            tMin = self.dataFactory.createData("temp",current_week, current_week_end, True)

            #DATA SENT TO MODEL
            data_to_model['comarca_brotes']= comarca_brotes
            data_to_model['tMin'] = tMin

            # RUN MODEL
            self.model.setData(data_to_model)
            print(">>> Running model...")
            alertas = self.model.run(current_week, current_week_end)

            alertas_list.append(alertas)

            for alerta in alertas["alertas"]:
                if current_week not in migrations_por_semana:
                    migrations_por_semana[current_week] = {}

                migrations_por_semana[current_week][alerta["comarca_sg"]] = comarca_brotes[alerta["comarca_sg"]]

            print(">>> Alertas total: " + str(len(alertas["alertas"])))

            # Rellenar el informe semanal
            # reportPDF = self.dataFactory.createData("report",current_week, current_week_end, alertas)

            #Actualizar current_week y current_week_end
            current_week = current_week_end
            current_week_end = current_week + timedelta(weeks = 1)
            i += 1

        self.geojsonGen.store_old_geojson("/home/caballes/TFG/gripeA_2020/old_geojson/","/home/caballes/TFG/gripeA_2020/geojson/")
        if weeks == 0:
            geojson_alerta = self.geojsonGen.update_alerta(alertas_list, lista_comarcas)
            geojson_outbreak = self.geojsonGen.update_outbreak(brotes_por_semana)
            geojson_migration = self.geojsonGen.update_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)
        else:
            # geojson_alerta = self.geojsonGen.generate_alerta(alertas_list, lista_comarcas)
            # geojson_outbreak = self.geojsonGen.generate_outbreak(brotes_por_semana)
            geojson_migration = self.geojsonGen.generate_migration(migrations_por_semana, lista_comarcas, brotes_por_semana)

        # print("Escribiendo sobre alertas.geojson")
        # text_file = open("geojson/alertas.geojson", "w", encoding="utf-8")
        # n = text_file.write(json.dumps(geojson_alerta, ensure_ascii=False))
        # text_file.close()
        # print("Escribiendo sobre brotes.geojson")
        # text_file = open("geojson/brotes.geojson", "w", encoding="utf-8")
        # n = text_file.write(json.dumps(geojson_outbreak, ensure_ascii=False))
        # text_file.close()
        print("Escribiendo sobre rutas.geojson")
        text_file = open("geojson/rutas.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(geojson_migration, ensure_ascii=False))
        text_file.close()

        return 0



