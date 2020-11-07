import pymongo
from pymongo import MongoClient

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
migrations = db.migrations

especies = [1340, 1610]

for especie in especies:
	nodos = []
	query = "CREATE "
	data_migrations = migrations.find({"Especie": especie})
	for migration in data_migrations:
		nodos.append(migration['geohash'][:4])
		nodos.append(migration['geohashR'][:4])
	# Borramos los nodos repetidos.
	nodos2 = list(set(nodos))
	for nodo in nodos2:
		query += "({}:".format(nodo)
		query += "Region{location:"
		query += "'{}'".format(nodo)
		query += "}), \n"

	valores = {}
	lista = []

	data_migrations = migrations.find({"Especie": especie})
	for migration in data_migrations:
		stringAux = "{}-{}".format(migration['geohash'][:4], migration['geohashR'][:4])
		if stringAux not in lista:
			lista.append(stringAux)
			valores[stringAux]=1
		else:
			valores[stringAux]+=1

	for element in lista :
		regiones = element.split('-')
		query += "({}) -[:MIGRA{}".format(regiones[0], especie)
		query += "{valor:"
		query += "{}".format(valores[element])
		query += "}]-> "
		query += "({}), \n".format(regiones[1])
		

	print(query)