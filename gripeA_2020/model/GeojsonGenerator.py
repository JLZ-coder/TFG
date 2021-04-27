import math
from datetime import datetime, timedelta, date
import json
from model.gdriveUploader import gDriveUploader

class GeojsonGenerator:
    def __init__(self):
        pass

    def generate_alerta(self, alertList, comarcasDict):
        feat_col_alertas = {
            "type": "FeatureCollection",
            "features": []
        }

        comarcas_de_alertlist = set()
        it = dict()
        
        for alertas in alertList:
            start = alertas["start"]
            end = alertas["end"]
            start.replace(hour=1)
            end.replace(hour=1)
            comarcas_de_alertlist.clear()

            #Ruta informe
            uploader = gDriveUploader()
            ruta = uploader.get_url_from("InformeSemanal_{}.pdf".format(start.strftime("%d-%m-%Y")))
            for it in alertas["alertas"]:
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
                            "idAlerta": it['comarca_sg'] + "_" + start.strftime("%d-%m-%Y"),
                            "Riesgo": it['risk'],
                            "reportDate": start.timestamp() * 1000,
                            "comarca": it['com_sgsa_n'],
                            "informe": ruta[0]
                        }
                    }
                    feat_col_alertas["features"].append(aux)

              
        text_file = open("geojson/alertas.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(feat_col_alertas, ensure_ascii=False))
        text_file.close()

        return feat_col_alertas

    def update_alerta(self, alertList, comarcasDict):
        feat_col_alertas = {
            "type": "FeatureCollection",
            "features": []
        }

        f = open("geojson/alertas.geojson")
        json_alertas = json.load(f)

        # # Quitamos las alertas de riesgo 0
        # json_alertas["features"] = list(filter(lambda alerta: alerta["properties"]["reportDate"] > 0, alertas["alertas"]))

        latest_date = 0
        for alerta in json_alertas["features"]:
            if alerta["properties"]["reportDate"] > latest_date:
                latest_date = alerta["properties"]["reportDate"]


        comarcas_de_alertlist = set()
        it = dict()

        for alertas in alertList:
            start = alertas["start"]
            if start.timestamp() * 1000 > latest_date:
                end = alertas["end"]
                start.replace(hour=1)
                end.replace(hour=1)
                comarcas_de_alertlist.clear()

                for it in alertas["alertas"]:
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
                                "idAlerta": it['comarca_sg'] + "_" + start.strftime("%d-%m-%Y"),
                                "Riesgo": it['risk'],
                                "reportDate": start.timestamp() * 1000,
                                "comarca": it['com_sgsa_n'],
                                "informe": ""
                            }
                        }
                        feat_col_alertas["features"].append(aux)

        json_alertas["features"].extend(feat_col_alertas["features"])

        text_file = open("geojson/alertas.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(json_alertas, ensure_ascii=False))
        text_file.close()

        return json_alertas

    def generate_migration(self, outbreakComarca, comarcasDict, brotesDict):
        feat_col_migracion = {
            "type": "FeatureCollection",
            "features": []
        }

        for semana in outbreakComarca:

            migration_dict = dict()

            for cod_comarca in outbreakComarca[semana]:

                migration_dict[cod_comarca] = dict()
                migration_dict[cod_comarca]["oieids"] = dict()
                dict_oieid = migration_dict[cod_comarca]["oieids"]
                migration_dict[cod_comarca]["lat"] = comarcasDict[cod_comarca]["Latitud"]
                migration_dict[cod_comarca]["long"] = comarcasDict[cod_comarca]["Longitud"]

                for brote in outbreakComarca[semana][cod_comarca]:

                    if brote["oieid"] not in dict_oieid:
                        dict_oieid[brote["oieid"]] = brote["especie"]


            for cod_comarca in migration_dict:

                comarca_long = migration_dict[cod_comarca]["long"]
                comarca_lat = migration_dict[cod_comarca]["lat"]

                for oieid in migration_dict[cod_comarca]["oieids"]:

                    for semana in brotesDict:
                        for brote in brotesDict[semana]:
                            if brote["oieid"] == oieid:
                                current_brote = brote
                                break

                    aux = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [float(comarca_long), float(comarca_lat)],
                                    [float(current_brote['long']), float(current_brote['lat'])]
                                ]
                            },
                            "properties": {
                                "idBrote": oieid,
                                "idAlerta": cod_comarca + "_" + semana.strftime("%d-%m-%Y"),
                                "idComarca": cod_comarca
                            }
                        }

                    feat_col_migracion['features'].append(aux)

        text_file = open("geojson/rutas.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(feat_col_migracion, ensure_ascii=False))
        text_file.close()

        return feat_col_migracion

    def update_migration(self, outbreakComarca, comarcasDict, brotesDict):
        feat_col_migracion = {
            "type": "FeatureCollection",
            "features": []
        }

        f = open("geojson/rutas.geojson")
        json_rutas = json.load(f)

        for semana in outbreakComarca:

            migration_dict = dict()

            for cod_comarca in outbreakComarca[semana]:

                migration_dict[cod_comarca] = dict()
                migration_dict[cod_comarca]["oieids"] = dict()
                dict_oieid = migration_dict[cod_comarca]["oieids"]
                migration_dict[cod_comarca]["lat"] = comarcasDict[cod_comarca]["Latitud"]
                migration_dict[cod_comarca]["long"] = comarcasDict[cod_comarca]["Longitud"]

                for brote in outbreakComarca[semana][cod_comarca]:

                    if brote["oieid"] not in dict_oieid:
                        dict_oieid[brote["oieid"]] = brote["especie"]


            for cod_comarca in migration_dict:

                comarca_long = migration_dict[cod_comarca]["long"]
                comarca_lat = migration_dict[cod_comarca]["lat"]

                for oieid in migration_dict[cod_comarca]["oieids"]:

                    for semana in brotesDict:
                        for brote in brotesDict[semana]:
                            if brote["oieid"] == oieid:
                                current_brote = brote
                                break

                    aux = {
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [float(comarca_long), float(comarca_lat)],
                                    [float(current_brote['long']), float(current_brote['lat'])]
                                ]
                            },
                            "properties": {
                                "idBrote": oieid,
                                "idAlerta": cod_comarca + " " + semana.strftime("%d-%m-%Y"),
                                "idComarca": cod_comarca
                            }
                        }

                    feat_col_migracion['features'].append(aux)

        json_rutas["features"].extend(feat_col_migracion["features"])

        text_file = open("geojson/rutas.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(json_rutas, ensure_ascii=False))
        text_file.close()

        return json_rutas

    def generate_outbreak(self, outbreaklist):
        feat_col_brote = {
            "type": "FeatureCollection",
            "features": []
        }

        set_oieid = set()

        for semana in outbreaklist:
            for it in outbreaklist[semana]:
                if it['oieid'] in set_oieid:
                    continue

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
                            "disease": it['disease'],
                            "country": it['country'],
                            "observationDate": math.floor(it['observation_date'].timestamp() * 1000),
                            "city": it['city'],
                            "species": it['species'],
                            "cases": "" if it['cases']== "" else int(it['cases']),
                            "deaths": "" if it['deaths']== "" else int(it['deaths']),
                            "serotipo": it['serotype'],
                            "epiUnit": it['epiunit']
                        }
                    }

                feat_col_brote['features'].append(aux)

        text_file = open("geojson/brotes.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(feat_col_brote, ensure_ascii=False))
        text_file.close()

        return feat_col_brote

    def update_outbreak(self, outbreaklist):
        feat_col_brote = {
            "type": "FeatureCollection",
            "features": []
        }

        f = open("geojson/brotes.geojson")
        json_brotes = json.load(f)

        set_oieid = set()

        for brote in json_brotes["features"]:
            set_oieid.add(brote["properties"]["id"]) 

        for semana in outbreaklist:
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
                            "disease": it['disease'],
                            "country": it['country'],
                            "observationDate": math.floor(it['observation_date'].timestamp() * 1000),
                            "city": it['city'],
                            "species": it['species'],
                            "cases": "" if it['cases']== "" else int(it['cases']),
                            "deaths": "" if it['deaths']== "" else int(it['deaths']),
                            "serotipo": it['serotype'],
                            "epiUnit": it['epiunit']
                        }
                    }

                feat_col_brote['features'].append(aux)

        for brote in feat_col_brote["features"]:
            if brote["properties"]["id"] not in set_oieid:
                json_brotes["features"].append(brote)

        text_file = open("geojson/brotes.geojson", "w", encoding="utf-8")
        n = text_file.write(json.dumps(json_brotes, ensure_ascii=False))
        text_file.close()

        return json_brotes