from pymongo import MongoClient
from .Builder import Builder
from neo4j import GraphDatabase
import json
from datetime import datetime, time, timedelta, date
from geolib import geohash
from geopy.distance import geodesic

class OutbreakBuilder(Builder):
    def __init__(self):
        super().__init__("outbreak")


    def create(self, start, end, parameters):

        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks
        migration_db = db.migrations
        neo4j_db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

        listaBrotes = list(brotes_db.find({"observation_date" : {"$gte" : start, "$lt" : end}}))

        tablaGeoComarca = json.load(open("data/tablaGeoComarca4.txt",  encoding='utf-8'))

        comarca_brotes = dict()
        brotes_por_semana = dict()


        outbreak_date = start

        #Preparamos un diccionario con la fecha de los lunes de cada semana como clave y una lista vacia como valor
        # 2020/01/01 => list
        # 2020/01/08 => list
        # ...
        # ..
        # .
        while outbreak_date < end:
            brotes_por_semana[outbreak_date] = []
            outbreak_date = outbreak_date + timedelta(weeks=1)


        #Recorremos los brotes para almacenarlos en brotes_por_semana, segun la semana en la que haya ocurrido el brote
        #Tambien se mira si el brote puede llegar a españa por alguna ruta y si lo hace, en comarca_brotes se guarda la informacion
        #necesaria
        # brotes_por_semana
        # 2020/01/01 => list(brotes en esta semana)
        # 2020/01/08 => list(brotes en esta semana)
        # ...
        # ..
        # .
        outbreak_date = start
        outbreak_week = outbreak_date + timedelta(days = -outbreak_date.weekday())
        for brote in listaBrotes:
            outbreak_date = brote["observation_date"]
            outbreak_week = outbreak_date + timedelta(days = -outbreak_date.weekday())
            brotes_por_semana[outbreak_week].append(brote)

            # # USANDO LA ESTRUCTURA ORIGINAL DE NEO4J 1.0, cada nodo representa una zona de geohash y hay rutas entre estas zonas 
            # geohash_del_brote = brote['geohash'][0:4]
            # #Rutas del brote, puede que no haya ninguna que conecte con España
            # response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie, r.valor'.format(geohash_del_brote)).values()
            # #relacion:
            # # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
            # # ej: ['sp0j', 1470]
            # for relacion in response:
            #     #Si el geohash destino esta en España
            #     if relacion[0] in tablaGeoComarca:
            #         #Recorremos las comarcas con los que solapa el geohash
            #         for comarca in tablaGeoComarca[relacion[0]]:
            #             #Si solapa al menos un 80% de su recuadro con el recuadro del geohash
            #             if comarca["peso"] >= 0.5:
            #                 cod = comarca["cod_comarca"]
            #                 valor = {"peso" : comarca["peso"],
            #                     "oieid" : brote["oieid"],
            #                     "epiunit" : brote["epiunit"],
            #                     "serotype": brote['serotype'],
            #                     "casos": brote['cases'],
            #                     "especie":relacion[1],
            #                     "nMov": relacion[2]
            #                 }
            #                 if cod not in comarca_brotes:
            #                     comarca_brotes[cod] = [valor]
            #                 else:
            #                     comarca_brotes[cod].append(valor)

            # # USANDO SOLO LAS RUTAS DE MONGO. Para cada brote se buscan sus rutas comparando el geohash del brote con el de las rutas
            # geohash_del_brote = brote['geohash'][0:4]
            # response = list(migration_db.find({"geohash": { "$regex":"^{}".format(geohash_del_brote)}}))
            # for it in response:
            #     cod = it['COMARCA_SG'] 
            #     valor = {"peso" : "",
            #         "oieid" : brote["oieid"],
            #         "epiunit" : brote["epiunit"],
            #         "serotype": brote['serotype'],
            #         "casos": brote['cases'],
            #         "especie":it['Especie'],
            #         "nMov": 1
            #     }
            #     if cod not in comarca_brotes:
            #         comarca_brotes[cod] = [valor]
            #     else:
            #        comarca_brotes[cod].append(valor)

            # # USANDO LA ESTRUCTURA DE NEO4J 2.0, cada brote es un nodo y cada comarca tambien, hay relaciones entre estos dos tipos
            # # de nodo que hacen de ruta
            # oieid_del_brote = brote['oieid']
            # response = neo4j_db.session().run('MATCH (x:Outbreak)-[r]->(y:Region) WHERE x.oieid={} RETURN y.comarca_sg, r.especie, r.id'.format(oieid_del_brote)).values()
            # for relacion in response:
            #     #Si el geohash destino esta en España
            #     cod = relacion[0]
            #     # if cod=="SP49108":
            #     #     print("fawer")
            #     valor = {"oieid" : brote["oieid"],
            #         "epiunit" : brote["epiunit"],
            #         "serotype": brote['serotype'],
            #         "casos": brote['cases'],
            #         "especie":relacion[1],
            #         "nMov": 1
            #     }
            #     if cod not in comarca_brotes:
            #         comarca_brotes[cod] = [valor]
            #     else:
            #         comarca_brotes[cod].append(valor)

            # USANDO LA ESTRUCTURA DE NEO4J 3.0, combinando nodos que representan una zona de geohash de Europa y nodos representando comarcas,
            # con relaciones entre ellos a modo de rutas
            geohash_del_brote = brote['geohash'][0:4]
            #Rutas del brote, puede que no haya ninguna que conecte con España
            response = neo4j_db.session().run(f"MATCH (x:geoRegion)-[r]->(y:Region) WHERE x.region_geohash starts with '{geohash_del_brote}' RETURN y.comarca_sg, r.especie, r.lat, r.long").values()
            # relacion = ['SP49108', 70, 56.233, 4.24354]
            for relacion in response:
                #Si el geohash destino esta en España
                outbreak_coord = (brote["lat"], brote["long"])
                route_coord = (relacion[2], relacion[3])
                if geodesic(outbreak_coord, route_coord).km < 25:
                    cod = relacion[0]
                    valor = {"oieid" : brote["oieid"],
                            "epiunit" : brote["epiunit"],
                            "serotype": brote['serotype'],
                            "casos": brote['cases'],
                            "especie":relacion[1],
                            "nMov": 1,
                            "lat": brote["lat"],
                            "long": brote["long"]
                        }
                    if cod not in comarca_brotes:
                        comarca_brotes[cod] = [valor]
                    else:
                        comarca_brotes[cod].append(valor)

            geohashes_around = geohash.neighbours(geohash_del_brote)
            for geohash_around in geohashes_around:
                #Rutas del brote, puede que no haya ninguna que conecte con España
                response = neo4j_db.session().run(f"MATCH (x:geoRegion)-[r]->(y:Region) WHERE x.region_geohash starts with '{geohash_around}' RETURN y.comarca_sg, r.especie, r.lat, r.long").values()
                # relacion = ['SP49108', 70, 56.233, 4.24354]
                for relacion in response:
                    #Si el geohash destino esta en España
                    outbreak_coord = (brote["lat"], brote["long"])
                    route_coord = (relacion[2], relacion[3])
                    if geodesic(outbreak_coord, route_coord).km < 25:
                        cod = relacion[0]
                        valor = {"oieid" : brote["oieid"],
                                "epiunit" : brote["epiunit"],
                                "serotype": brote['serotype'],
                                "casos": brote['cases'],
                                "especie":relacion[1],
                                "nMov": 1,
                                "lat": brote["lat"],
                                "long": brote["long"]
                            }
                        if cod not in comarca_brotes:
                            comarca_brotes[cod] = [valor]
                        else:
                            comarca_brotes[cod].append(valor)


        neo4j_db.close()
        client.close()

        return comarca_brotes, brotes_por_semana