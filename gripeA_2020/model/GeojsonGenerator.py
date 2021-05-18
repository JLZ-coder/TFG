import math
from datetime import datetime, timedelta, date
import json
from model.gdriveUploader import gDriveUploader
import os

class GeojsonGenerator:
    def __init__(self):
        pass

    def store_old_geojson(self, old_geojson_folder, geojson_folder):
        print("Guardando antiguos geojson")
        if os.path.exists(geojson_folder):
            copia_a_destino = f"cp -r {geojson_folder} {old_geojson_folder}"
            os.system(copia_a_destino)
        else:
            print("La carpeta de geojson no existe")

    def generate_alerta(self, alertList, comarcasDict):
        print("Generar alertas.geojson")

        feat_col_alertas = {
            "type": "FeatureCollection",
            "features": []
        }

        comarcas_de_alertlist = set()
        it = dict()
        
        for alertas in alertList:
            start = alertas["start"]
            end = alertas["end"]
            start = start.replace(hour=1)
            end = end.replace(hour=1)
            comarcas_de_alertlist.clear()

            #Ruta informe
            uploader = gDriveUploader()
            ruta = uploader.get_url_from("InformeSemanal_{}.pdf".format(start.strftime("%d-%m-%Y")))

            if len(ruta) == 0:
                ruta.append("No hay url")
            
            for it in alertas["alertas"]:
                if it['risk'] > 5:
                    it['risk'] = 5

                if it['risk'] != 0:
                    comarcas_de_alertlist.add(it['comarca_sg'])
                    cod_comarca = it['comarca_sg']
                    it['Longitud'] = comarcasDict[cod_comarca]['Longitud']
                    it['Latitud'] = comarcasDict[cod_comarca]['Latitud']
                    it['com_sgsa_n'] = comarcasDict[cod_comarca]['com_sgsa_n']
                    it['CPRO'] = comarcasDict[cod_comarca]['CPRO']
                    it['provincia'] = comarcasDict[cod_comarca]['provincia']
                    it['CPROyMUN'] = comarcasDict[cod_comarca]['CPROyMUN']

                    aux={
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(it['Longitud']), float(it['Latitud'])]
                        },
                        "properties": {
                            "idAlerta": it['comarca_sg'] + "_" + str(start.timestamp() * 1000),
                            "Riesgo": it['risk'],
                            "reportDate": start.timestamp() * 1000,
                            "comarca": it['com_sgsa_n'],
                            "informe": ruta[0]
                        }
                    }
                    feat_col_alertas["features"].append(aux)

        return feat_col_alertas

    def update_alerta(self, alertList, comarcasDict):
        print("Update alertas.geojson")
        if len(alertList) == 0:
            return 0

        f = open("geojson/alertas.geojson")
        json_alertas = json.load(f)

        most_recent_date = 0

        for alertas in alertList:
            start = alertas["start"]
            end = alertas["end"]
            start = start.replace(hour=1)
            end = end.replace(hour=1)

            #Ruta informe
            uploader = gDriveUploader()
            ruta = uploader.get_url_from("InformeSemanal_{}.pdf".format(start.strftime("%d-%m-%Y")))

            if len(ruta) == 0:
                ruta.append("No hay url")

            if start.timestamp() * 1000 > most_recent_date:
                most_recent_date = start.timestamp() * 1000
            
            for it in alertas["alertas"]:
                if it['risk'] > 5:
                    it['risk'] = 5

                if it['risk'] != 0:
                    cod_comarca = it['comarca_sg']
                    it['Longitud'] = comarcasDict[cod_comarca]['Longitud']
                    it['Latitud'] = comarcasDict[cod_comarca]['Latitud']
                    it['com_sgsa_n'] = comarcasDict[cod_comarca]['com_sgsa_n']
                    aux={
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(it['Longitud']), float(it['Latitud'])]
                        },
                        "properties": {
                            "idAlerta": it['comarca_sg'] + "_" + str(start.timestamp() * 1000),
                            "Riesgo": it['risk'],
                            "reportDate": start.timestamp() * 1000,
                            "comarca": it['com_sgsa_n'],
                            "informe": ruta[0]
                        }
                    }
                    json_alertas["features"].append(aux)
        
        # Borramos las entradas antiguas de mas de un año y las entradas posteriores a la ejecucion para que no se superpongan
        last_year_alerts = list(filter(lambda alerta: most_recent_date - alerta["properties"]["reportDate"] <= 31556926000, json_alertas["features"]))
        last_year_alerts = list(filter(lambda alerta: most_recent_date - alerta["properties"]["reportDate"] >= 0, last_year_alerts))

        json_alertas["features"] = last_year_alerts

        return json_alertas

    def generate_migration(self, outbreakComarca, comarcasDict, brotesDict):
        print("Generar rutas.geojson")
        feat_col_migracion = {
            "type": "FeatureCollection",
            "features": []
        }

        for semana in outbreakComarca:
            aux_semana = semana.replace(hour=1)
            reportDate = aux_semana.timestamp() * 1000
            oieid_set = set()

            for cod_comarca in outbreakComarca[semana]:

                comarca_lat = comarcasDict[cod_comarca]["Latitud"]
                comarca_long = comarcasDict[cod_comarca]["Longitud"]

                oieid_set.clear()

                for brote in outbreakComarca[semana][cod_comarca]:
                    oieid = brote["oieid"]
                    if oieid not in oieid_set:
                        oieid_set.add(oieid)
                        aux = {
                                "type": "Feature",
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": [
                                        [float(comarca_long), float(comarca_lat)],
                                        [float(brote['long']), float(brote['lat'])]
                                    ]
                                },
                                "properties": {
                                    "idBrote": oieid,
                                    "idAlerta": cod_comarca + "_" + str(reportDate),
                                    "idComarca": cod_comarca
                                }
                            }
                        feat_col_migracion['features'].append(aux)

        return feat_col_migracion

    def update_migration(self, outbreakComarca, comarcasDict, brotesDict):
        print("Update rutas.geojson")

        if len(outbreakComarca) == 0:
            return 0

        f = open("geojson/rutas.geojson")
        json_rutas = json.load(f)

        most_recent_date = 0
        for semana in outbreakComarca:
            if semana.timestamp() * 1000 > most_recent_date:
                most_recent_date = semana.timestamp() * 1000

            aux_semana = semana.replace(hour=1)
            reportDate = aux_semana.timestamp() * 1000

            oieid_set = set()

            for cod_comarca in outbreakComarca[semana]:

                comarca_lat = comarcasDict[cod_comarca]["Latitud"]
                comarca_long = comarcasDict[cod_comarca]["Longitud"]

                oieid_set.clear()

                for brote in outbreakComarca[semana][cod_comarca]:
                    oieid = brote["oieid"]
                    if oieid not in oieid_set:
                        oieid_set.add(oieid)
                        aux = {
                                "type": "Feature",
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": [
                                        [float(comarca_long), float(comarca_lat)],
                                        [float(brote['long']), float(brote['lat'])]
                                    ]
                                },
                                "properties": {
                                    "idBrote": oieid,
                                    "idAlerta": cod_comarca + "_" + str(reportDate),
                                    "idComarca": cod_comarca
                                }
                            }
                        json_rutas["features"].append(aux)


        # Borramos las entradas antiguas de mas de un año
        last_year_routes = list(filter(lambda route: most_recent_date - float(route["properties"]["idAlerta"].split("_")[1])<= 31556926000, json_rutas["features"]))
        last_year_routes = list(filter(lambda route: most_recent_date - float(route["properties"]["idAlerta"].split("_")[1]) >= 0, last_year_routes))
        json_rutas["features"] = last_year_routes

        return json_rutas

    def generate_outbreak(self, outbreaklist):
        print("Generar brotes.geojson")

        feat_col_brote = {
            "type": "FeatureCollection",
            "features": []
        }

        set_oieid = set()

        for semana in outbreaklist:
            for it in outbreaklist[semana]:
                
                if ('city' not in it):
                    it['city'] = "No especificado"

                set_oieid.add(it['oieid'])

                aux = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(it['long']), float(it['lat'])]
                        },
                        "properties": {
                            "id": it['oieid'],
                            #"disease": it['disease'],
                            "country": it['country'],
                            "observationDate": math.floor(it['observation_date'].timestamp() * 1000),
                            "city": it['city'],
                            "species": it['species'],
                            "cases": "" if it['cases']== "" else int(it['cases']),
                            #"deaths": "" if it['deaths']== "" else int(it['deaths']),
                            "serotipo": it['serotype'],
                            #"epiUnit": it['epiunit']
                        }
                    }

                feat_col_brote['features'].append(aux)

        return feat_col_brote

    def update_outbreak(self, outbreaklist):
        print("Update brotes.geojson")
        if len(outbreaklist) == 0:
            return 0

        f = open("geojson/brotes.geojson")
        json_brotes = json.load(f)

        most_recent_date = 0

        for semana in outbreaklist:
            if semana.timestamp() * 1000 > most_recent_date:
                most_recent_date = semana.timestamp() * 1000
            
            for it in outbreaklist[semana]:
                
                if ('city' not in it):
                    it['city'] = "No especificado"

                aux = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(it['long']), float(it['lat'])]
                        },
                        "properties": {
                            "id": it['oieid'],
                            #"disease": it['disease'],
                            "country": it['country'],
                            "observationDate": math.floor(it['observation_date'].timestamp() * 1000),
                            "city": it['city'],
                            "species": it['species'],
                            "cases": "" if it['cases']== "" else int(it['cases']),
                            #"deaths": "" if it['deaths']== "" else int(it['deaths']),
                            "serotipo": it['serotype'],
                            #"epiUnit": it['epiunit']
                        }
                    }

                json_brotes['features'].append(aux)

        # Borramos las entradas antiguas de mas de un año + 3 meses
        last_year_outbreaks = list(filter(lambda brote: most_recent_date - brote["properties"]["observationDate"] <= (31556926 + 3 * 2629743) * 1000, json_brotes["features"]))
        last_year_outbreaks = list(filter(lambda brote: most_recent_date - brote["properties"]["observationDate"] >= 0, last_year_outbreaks))
        json_brotes["features"] = last_year_outbreaks

        return json_brotes