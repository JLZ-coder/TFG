from pymongo import MongoClient
from .Builder import Builder
from dao.daoBrotes import daoBrotes
from neo4j import GraphDatabase
import json
from datetime import datetime, timedelta, date

class OutbreakBuilder(Builder):
    def __init__(self):
        super().__init__("outbreak")

    def create(self, start, end, parameters):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks

        neo4j_db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

        listaBrotes = brotes_db.find({"observation_date" : {"$gt" : start, "$lte" : end}})

        # - Con estos brotes miramos en el grafo de neo4j (version de 4 o 5 digitos) si hay nodos con estos geohashes.
        #     + Si hay un nodo, se miran todos los demas nodos asociados a este y lo guardamos si alguno de los nodos asociados esta en España

        tablaGeoComarca = json.load(open("data/tablaGeoComarca4.txt",  encoding='utf-8'))
        comarca_brotes = {}

        brotes_por_semana = dict()
        set_oieids = set()
        current_date = end - timedelta(weeks = 1)

        while current_date >= start:
            brotes_por_semana[current_date] = []
            current_date = current_date - timedelta(weeks=1)

        for brote in listaBrotes:
            #Con los nuevos brotes, no tenemos en cuenta esta comprobación
            #if brote["disease_id"] != "201":
            geo_del_brote = brote['geohash'][0:4]

            for semana in brotes_por_semana:
                if semana <= brote["observation_date"] and semana + timedelta(weeks=1) > brote["observation_date"]:
                    brotes_por_semana[semana].append(brote)

            response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie'.format(geo_del_brote)).values()

            # relacion
            # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
            # ej: ['sp0j', 1470]
            for relacion in response:
                if relacion[0] in tablaGeoComarca:
                    for comarca in tablaGeoComarca[relacion[0]]:
                        if comarca["peso"] > 0.8:
                            cod = comarca["cod_comarca"]
                            if cod not in comarca_brotes:
                                comarca_brotes[cod] = [{"peso" : comarca["peso"], "oieid" : brote["oieid"], "epiunit" : brote["epiunit"], "serotype": brote['serotype'], "casos": brote['cases'], "especie":relacion[1]}]
                            else:
                                comarca_brotes[cod].append({"peso" : comarca["peso"], "oieid" : brote["oieid"], "epiunit" : brote["epiunit"], "serotype": brote['serotype'], "casos": brote['cases'],"especie":relacion[1]})


        return comarca_brotes, brotes_por_semana