import pymongo
from pymongo import MongoClient
import pandas as pd
import os

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
migrations = db.migrations

#Leemos el archivo de todas las especies
file="Especies.xlsx"

df = pd.read_excel(file)

#Borramos columna de nombres
#df.drop(['Nombre científico', 'Nombre común'], axis='columns', inplace=True)
especies = df['codigo anilla']

# os.remove("sample.txt")
text_file = open("sample.txt", "a")

nodos = []
for especie in especies:
	if migrations.find({"Especie": especie}).count() > 0:
		data_migrations = migrations.find({"Especie": especie})
		for migration in data_migrations:
			nodos.append(migration['geohash'][:4])
			nodos.append(migration['geohashR'][:4])

query = "CREATE "
# Borramos los nodos repetidos.
nodos2 = list(set(nodos))
for nodo in nodos2:
	query += "({}:".format(nodo)
	query += "Region{location:"
	query += "'{}'".format(nodo)
	query += "}),\n"

query = query[:-2]
query += "\n"
n = text_file.write(query)
text_file.close()

for especie in especies:
	if migrations.find({"Especie": especie}).count() > 0:
		query = "CREATE "
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
			query += "({}),\n".format(regiones[1])

		query = query[:-2]
		query += "\n"
		n = text_file.write(query)
	# print(query)
text_file.close()