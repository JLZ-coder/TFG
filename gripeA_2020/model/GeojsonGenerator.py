import math
from datetime import datetime, timedelta, date

class GeojsonGenerator:
    def __init__(self):
        pass

    def generate_comarca(self, alertList, comarcasDict):
        feat_col_alertas = {
            "type": "FeatureCollection",
            "features": []
        }

        for alertas in alertList:
            start = alertas["start"]
            end = alertas["end"]

            for it in alertas["alertas"]:

                cod_comarca = it['comarca_sg']
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
                        "startDate": start.timestamp() * 1000,
                        "endDate": end.timestamp() * 1000,
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

        return feat_col_alertas

    def generate_migration(self, outbreakComarca, comarcasDict):
        feat_col_migracion = {
            "type": "FeatureCollection",
            "features": []
        }

        for cod_comarca in outbreakComarca:
            outbreakComarca[cod_comarca] = 

        for it in listaMigraciones:

            comarca_long = listaMigraciones[it]["long"]
            comarca_lat = listaMigraciones[it]["lat"]
            for brote in listaMigraciones[it]["brotes"]:

                aux = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [float(comarca_long), float(comarca_lat), float(brote['long']), float(brote['lat'])]
                        },
                        "properties": {
                            "idBrote": brote['oieid'],
                            "idAlerta": it,
                            "idComarca": it
                        }
                    }

                feat_col_migracion['features'].append(aux)

        return feat_col_migracion

    def generate_outbreak(self, outbreaklist):
        feat_col_brote = {
            "type": "FeatureCollection",
            "features": []
        }

        if type(outbreaklist) is dict:
            outbreaklist = list(outbreaklist.values())

        for it in outbreaklist:
            aux = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(it['long']), float(it['lat'])]
                    },
                    "properties": {
                        "id": it['oieid'],
                        "disease": diseases[it['disease_id']],
                        "country": it['country'],
                        "start": math.floor(it['start'].timestamp() * 1000),
                        # "end": "" if it['end'] == "" else math.floor(it['end'].timestamp() * 1000),
                        "city": it['city'],
                        # "species": it['species'],
                        # "at_risk": int(it['at_risk']),
                        # "cases": int(it['cases']),
                        # "deaths": int(it['deaths']),
                        # "preventive_killed": int(it['preventive_killed'])
                        "serotipo": it['serotype'],
                        "moreInfo": it['urlFR'],
                        "epiUnit": it['epiunit'],
                        "reportDate": math.floor(it['report_date'].timestamp() * 1000)
                    }
                }

            feat_col_brote['features'].append(aux)

        return feat_col_brote