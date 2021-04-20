from pymongo import MongoClient
from .Builder import Builder
from dao.daoBrotes import daoBrotes
from neo4j import GraphDatabase
import json
from datetime import datetime, time, timedelta, date

#Revised: 13/4/21
class OutbreakBuilder(Builder):
    def __init__(self):
        super().__init__("outbreak")


    def create(self, start, end, parameters):

        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        brotes_db = db.outbreaks

        neo4j_db = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

        listaBrotes = brotes_db.find({"observation_date" : {"$gt" : start, "$lte" : end}})

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
        while outbreak_date <= end:
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
        for brote in listaBrotes:
            #Con los nuevos brotes, no tenemos en cuenta esta comprobación
            #if brote["disease_id"] != "201":
            outbreak_date = brote["observation_date"]
            outbreak_week = outbreak_date + timedelta(days = -outbreak_date.weekday())
            brotes_por_semana[outbreak_week].append(brote)

            geohash_del_brote = brote['geohash'][0:4]

            #Rutas del brote, puede que no haya ninguna que conecte con España
            response = neo4j_db.session().run('MATCH (x:Region)-[r]-(y:Region) WHERE x.location starts with "{}" RETURN y.location, r.especie'.format(geohash_del_brote)).values()

            #relacion:
            # pareja de geohash y especie, el geohash pertenece a un nodo destino de uno perteneciente a un brote
            # ej: ['sp0j', 1470]
            for relacion in response:
                #Si el geohash destino esta en España
                if relacion[0] in tablaGeoComarca:
                    #Recorremos las comarcas con los que solapa el geohash
                    for comarca in tablaGeoComarca[relacion[0]]:
                        #Si solapa al menos un 80% de su recuadro con el recuadro del geohash
                        if comarca["peso"] >= 0.8:
                            cod = comarca["cod_comarca"]
                            valor = {"peso" : comarca["peso"], "oieid" : brote["oieid"], "epiunit" : brote["epiunit"], "serotype": brote['serotype'], "casos": brote['cases'], "especie":relacion[1]}
                            if cod not in comarca_brotes:
                                comarca_brotes[cod] = [valor]
                            else:
                                comarca_brotes[cod].append(valor)

        return comarca_brotes, brotes_por_semana