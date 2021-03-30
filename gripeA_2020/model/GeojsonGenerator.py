import math
from datetime import datetime, timedelta, date
import json

class GeojsonGenerator:
    def __init__(self):
        pass

    def generate_comarca(self, alertList, comarcasDict):
        feat_col_alertas = {
            "type": "FeatureCollection",
            "features": []
        }

        comarcas_de_alertlist = set()
        it = dict()

        for alertas in alertList:
            start = alertas["start"]
            end = alertas["end"]
            comarcas_de_alertlist.clear()

            for it in alertas["alertas"]:

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
                        "id": cod_comarca, #Será el id de comarca
                        "riskLevel": it['risk'],
                        "number_of_cases": 0,
                        "reportDate": start.timestamp() * 1000,
                        #"endDate": end.timestamp() * 1000,
                        # "codeSpecies": 1840,
                        # "species": "Anas crecca",
                        # "commonName": "Pato cuchara",
                        # "fluSubtype": "H5",
                        "idComarca": cod_comarca,
                        "comarca": it['com_sgsa_n'],
                        "CPRO": it['CPRO'],
                        "province": it['provincia'],
                        "CPROyMUN": it['CPROyMUN'],
                        "serotypes": it['serotipos'],
                        "species": it['especies']
                    }
                }
                feat_col_alertas["features"].append(aux)

            it.clear()

            '''for cod_comarca in comarcasDict:
                if comarcasDict[cod_comarca]['comarca_sg'] not in comarcas_de_alertlist:

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
                            "id": cod_comarca, #Será el id de comarca
                            "riskLevel": 0,
                            "number_of_cases": 0,
                            "reportDate": start.timestamp() * 1000,
                            #"endDate": end.timestamp() * 1000,
                            # "codeSpecies": 1840,
                            # "species": "Anas crecca",
                            # "commonName": "Pato cuchara",
                            # "fluSubtype": "H5",
                            "idComarca": cod_comarca,
                            "comarca": it['com_sgsa_n'],
                            "CPRO": it['CPRO'],
                            "province": it['provincia'],
                            "CPROyMUN": it['CPROyMUN']
                        }
                    }
                    feat_col_alertas["features"].append(aux)
            '''

        text_file = open("geojson/alertas.geojson", "w")
        n = text_file.write(json.dumps(feat_col_alertas))
        text_file.close()

        return feat_col_alertas

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
                                "idAlerta": cod_comarca,
                                "idComarca": cod_comarca,
                                "especie": migration_dict[cod_comarca]["oieids"][oieid]
                            }
                        }

                    feat_col_migracion['features'].append(aux)

        text_file = open("geojson/rutas.geojson", "w")
        n = text_file.write(json.dumps(feat_col_migracion))
        text_file.close()

        return feat_col_migracion

    def generate_outbreak(self, outbreaklist):
        feat_col_brote = {
            "type": "FeatureCollection",
            "features": []
        }

        diseases = {
            '15' : "Highly Path Avian influenza",
            '201' : "Low Path Avian influenza",
            '1164' : "Highly pathogenic influenza A viruses"
        }

        for semana in outbreaklist:
            for it in outbreaklist[semana]:
                aux = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(it['long']), float(it['lat'])]
                        },
                        "properties": {
                            "id": it['oieid'],
                            #"disease": diseases[it['disease_id']],
                            "disease": it['disease'],
                            "country": it['country'],
                            "observationDate": math.floor(it['observation_date'].timestamp() * 1000),
                            # "end": "" if it['end'] == "" else math.floor(it['end'].timestamp() * 1000),
                            "city": it['city'],
                            "species": it['species'],
                            # "at_risk": int(it['at_risk']),
                            "cases": "" if it['cases']== "" else int(it['cases']),
                            "deaths": "" if it['deaths']== "" else int(it['deaths']),
                            # "preventive_killed": int(it['preventive_killed'])
                            "serotipo": it['serotype'],
                            "moreInfo": it['urlFR'],
                            "epiUnit": it['epiunit'],
                            "reportDate": math.floor(it['report_date'].timestamp() * 1000)
                        }
                    }

                feat_col_brote['features'].append(aux)

        text_file = open("geojson/brotes.geojson", "w")
        n = text_file.write(json.dumps(feat_col_brote))
        text_file.close()

        return feat_col_brote