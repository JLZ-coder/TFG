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
text_file = open("sample.txt", "w")

nodos = []
migra = ""
for especie in especies:
	if migrations.find({"Especie": especie}).count() > 0:
		# data_migrations = migrations.find({"Especie": especie})
		# for migration in data_migrations:
		# 	nodos.append(migration['geohash'][:4])
		# 	nodos.append(migration['geohashR'][:4])

		aux_migra = "CREATE "
		valores = {}
		lista = []
		data_migrations = migrations.find({"Especie": especie})
		for migration in data_migrations:
			nodos.append(migration['geohash'][:4])
			nodos.append(migration['geohashR'][:4])
			if migration['geohash'][:4] != migration['geohashR'][:4]:
				stringAux = "{}-{}".format(migration['geohash'][:4], migration['geohashR'][:4])
				if stringAux not in lista:
					lista.append(stringAux)
					valores[stringAux]=1
				else:
					valores[stringAux]+=1

		for element in lista :
			regiones = element.split('-')
			aux_migra += "({}) -[:MIGRA{}".format(regiones[0], especie)
			aux_migra += "{valor:"
			aux_migra += "{}".format(valores[element])
			aux_migra += "}]-> "
			aux_migra += "({}),\n".format(regiones[1])

		aux_migra = aux_migra[:-2]
		aux_migra += "\n"
		migra += aux_migra

crea = "CREATE "
# Borramos los nodos repetidos.
nodos2 = list(set(nodos))
for nodo in nodos2:
	crea += "({}:".format(nodo)
	crea += "Region{location:"
	crea += "'{}'".format(nodo)
	crea += "}),\n"

crea = crea[:-2]
crea += "\n"
query = crea + migra
n = text_file.write(query)
text_file.close()