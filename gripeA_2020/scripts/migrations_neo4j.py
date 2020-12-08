from pymongo import MongoClient
import os
from neo4j import GraphDatabase

# Usa los datos de migraciones en mongo para hacer un grafo en neo4j

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
migrations = db.migrations
TAM_GEO = 4

all_migrations = migrations.find({})

nodos = set()
migration_dict = {}

# Recuerda, entras, coges los geohash de anillamiento y recuperacion, la especie y te vas.

for migration in all_migrations:
	geo = migration['geohash'][:TAM_GEO]
	geoR = migration['geohashR'][:TAM_GEO]

	if (geo != geoR):
		nodos.add(geo)
		nodos.add(geoR)
		aux_id_migra = "{}-{}-{}".format(geo, migration['Especie'], geoR)
		aux_id_migra_reverse = "{}-{}-{}".format(geoR, migration['Especie'], geo)

		if aux_id_migra not in migration_dict and aux_id_migra_reverse not in migration_dict:
			migration_dict[aux_id_migra] = 1
		elif aux_id_migra in migration_dict:
			migration_dict[aux_id_migra] += 1
		elif aux_id_migra_reverse in migration_dict:
			migration_dict[aux_id_migra_reverse] += 1



nodos_query = ""
# (ezw4:Region{location:'ezw4'})
for nodo in nodos:
	aux = "({}:Region{{location:'{}'}}),\n".format(nodo, nodo)
	nodos_query += aux

nodos_query = "CREATE " + nodos_query[:-2]



migrations_query = ""
# (ezhh) -[:MIGRA1340{valor:1}]-> (ezhc)
for migration in migration_dict:

	geo, especie, geoR = migration.split("-")

	aux = "({})-[:MIGRA{}{{valor:".format(geo, especie) + "{}}}]->({}),\n".format(migration_dict[migration], geoR)
	migrations_query += aux

migrations_query = "CREATE " + migrations_query[:-2]

query = "//PARTE DE NODOS\n" + nodos_query + "\n//PARTE DE MIGRACIONES\n" + migrations_query


driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))
# Borra todo lo que hay en neo4j!!!!!
driver.session().run("MATCH (n) DETACH DELETE n")
response = driver.session().run(query).value()
driver.close()


# text_file = open("migras_neo4j.txt", "w")
# n = text_file.write(query)
# text_file.close()