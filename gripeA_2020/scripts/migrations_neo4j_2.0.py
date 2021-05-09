from pymongo import MongoClient
import os
from neo4j import GraphDatabase
from geopy.distance import geodesic
import sys
from datetime import datetime, time, timedelta, date

# Usa los datos de migraciones en mongo para hacer un grafo en neo4j

TAM_GEO = 4


# Nodos de todos los brotes, solo una vez al principio.
def reset_outbreaks(driver, outbreaks):
	print(">>> Reset Outbreaks")
	cursor = outbreaks.find({})

	outbreak_nodes_query = ""
	# (288337:Outbreak {oieid: 288337, lat: 54.47, long: -1.07})
	for outbreak in cursor:
		oieid = outbreak["oieid"]
		lat = outbreak["lat"]
		long = outbreak["long"]

		aux = '(:Outbreak {{ oieid:{}, lat:{}, long:{} }} ),\n'.format(oieid, lat, long)
		outbreak_nodes_query += aux

	response = ""
	if outbreak_nodes_query != "":
		outbreak_nodes_query = "CREATE " + outbreak_nodes_query[:-2]
		# Borra todo los brotes que hay en neo4j!!!!!
		driver.session().run("MATCH (n:Outbreak) DETACH DELETE n")
		response = driver.session().run(outbreak_nodes_query).value()

	return response, outbreak_nodes_query

# Nodos de los nuevos brotes
def update_outbreaks(driver, outbreaks):
	print(">>> Update Outbreaks")
	cursor = outbreaks.find({})

	response = driver.session().run('MATCH (x:Outbreak) RETURN x.oieid').values()

	existing_oieid = set()
	for oieid in response:
		existing_oieid.add(oieid[0])

	new_outbreaks = list(filter(lambda outbreak: outbreak["oieid"] not in existing_oieid, cursor))

	outbreak_nodes_query = ""
	# (ob_288337:Outbreak {oieid: 288337, lat: 54.47, long: -1.07})
	for outbreak in new_outbreaks:
		oieid = outbreak["oieid"]
		lat = outbreak["lat"]
		long = outbreak["long"]

		aux = '(:Outbreak {{ oieid:{}, lat:{}, long:{} }} ),\n'.format(oieid, lat, long)
		outbreak_nodes_query += aux

	response = ""
	if outbreak_nodes_query != "":
		outbreak_nodes_query = "CREATE " + outbreak_nodes_query[:-2]
		response = driver.session().run(outbreak_nodes_query).value()

	return response, outbreak_nodes_query

# Nodos de todas las comarcas, solo una vez al principio.
def reset_regions(driver, regions):
	print(">>> Reset Regions")
	cursor = regions.find({})

	region_nodes_query = ""
	# (SP49108:Region {comarca_sg: 'SP49108', lat: 54.47, long: -1.07})
	for region in cursor:
		comarca_sg = region["comarca_sg"]
		lat = region["Latitud"]
		long = region["Longitud"]

		aux = "(:Region {{ comarca_sg:'{}', lat:{}, long:{} }} ),\n".format(comarca_sg, lat, long)
		region_nodes_query += aux

	response = ""
	if region_nodes_query != "":
		region_nodes_query = "CREATE " + region_nodes_query[:-2]
		# Borra todo las comarcas que hay en neo4j!!!!!
		driver.session().run("MATCH (n:Region) DETACH DELETE n")
		response = driver.session().run(region_nodes_query).value()

	return response, region_nodes_query

# Nodos de los nuevos brotes
def update_regions(driver, migrations):
	print(">>> Update Regions")
	cursor = migrations.find({})

	response = driver.session().run('MATCH (x:Region) RETURN x.comarca_sg').values()

	existing_comarca_sg = set()
	for comarca_sg in response:
		existing_comarca_sg.add(comarca_sg[0])

	new_migrations = list(filter(lambda region: region["comarca_sg"] not in existing_comarca_sg, cursor))

	migrations_nodes_query = ""
	# (288337:Outbreak {comarca_sg: 288337, lat: 54.47, long: -1.07})
	for region in new_migrations:
		comarca_sg = region["comarca_sg"]
		lat = region["Latitud"]
		long = region["Longitud"]

		aux = "(:Region {{ comarca_sg:'{}', lat:{}, long:{} }} ),\n".format(comarca_sg, lat, long)
		migrations_nodes_query += aux

	response = ""
	if migrations_nodes_query != "":
		migrations_nodes_query = "CREATE " + migrations_nodes_query[:-2]
		response = driver.session().run(migrations_nodes_query).value()

	return response, migrations_nodes_query

# Nodos de todas las comarcas, solo una vez al principio.
def reset_routes(driver, routes, outbreaks, start):
	print(">>> Reset Routes")
	cursor = routes.find({})

	last_outbreaks = outbreaks.find({"observation_date" : {"$gte" : start}}, {"oieid" : 1})
	last_oieid = set()
	for outbreak in last_outbreaks:
		last_oieid.add(outbreak["oieid"])
	response_outbreaks = driver.session().run('MATCH (x:Outbreak) RETURN x.oieid, x.lat, x.long').values()
	response_outbreaks = list(filter(lambda outbreak: outbreak[0] in last_oieid, response_outbreaks))

	# response_regions = driver.session().run('MATCH (x:Region) RETURN x.comarca_sg, x.lat, x.long').values()
	# existing_comarca_sg = set()
	# for comarca_sg in response_regions:
	# 	existing_comarca_sg.add(comarca_sg[0])

	# Borra todo las comarcas que hay en neo4j!!!!!
	driver.session().run("MATCH ()-[n:Route]->() DETACH DELETE n")

	route_nodes_query = ""
	# MATCH (a:Outbreak), (b:Region)
   	# WHERE a.oieid = 288337 AND b.comarca_sg = SP24108
	# CREATE (a)-[:Route {id: 56356, especie: 70, lat: 54.47, long: -1.07, latR: 54.47, longR: -1.07 }]->(b)
	total_ctr = 0
	for outbreak in response_outbreaks:
		oieid = outbreak[0]
		lat = outbreak[1]
		long = outbreak[2]
		ctr = 0
		print(">> Outbreak: {}".format(oieid))
		for route in cursor:
			route_id = route["Id"]
			route_species = route["Especie"]
			route_lat = route["Lat"]
			route_long = route["Long"]
			route_latR = route["LatR"]
			route_longR = route["LongR"]
			route_region = route["COMARCA_SG"]

			outbreak_coord = (lat, long)
			route_coord = (route_lat, route_long)

			if geodesic(outbreak_coord, route_coord).kilometers < 25:
				aux = ("MATCH (a:Outbreak), (b:Region)  WHERE a.oieid = {} AND b.comarca_sg = '{}' "
					"CREATE (a)-[:Route {{id: {}, especie: {}, lat: {}, long: {}, latR: {}, longR: {} }}]->(b);\n").format(
						oieid, route_region,
						route_id, route_species, route_lat, route_long, route_latR, route_longR)

				response = driver.session().run(aux).value()
				route_nodes_query += aux
				ctr += 1

		print("> {} routes found".format(ctr))
		total_ctr += ctr
		cursor.rewind()

	print(">>> {} routes found IN  TOTAL".format(total_ctr))
	return response, route_nodes_query

# Nodos de los nuevos brotes
def update_routes(driver, routes, outbreaks, start):
	print(">>> Update Routes")
	cursor = routes.find({})

	last_outbreaks = outbreaks.find({"observation_date" : {"$gte" : start}}, {"oieid" : 1})
	last_oieid = set()
	for outbreak in last_outbreaks:
		last_oieid.add(outbreak["oieid"])
	response_outbreaks = driver.session().run('MATCH (x:Outbreak) RETURN x.oieid, x.lat, x.long').values()
	response_outbreaks = list(filter(lambda outbreak: outbreak[0] in last_oieid, response_outbreaks))

	response = driver.session().run('MATCH (:Outbreak)-[x:Route]->(:Region) RETURN x.id').values()

	existing_routes = set()
	for routes in response:
		existing_routes.add(routes[0])

	new_routes = list(filter(lambda routes: routes["Id"] not in existing_routes, cursor))

	route_nodes_query = ""
	# MATCH (a:Outbreak), (b:Region)
   	# WHERE a.oieid = 288337 AND b.comarca_sg = SP24108
	# CREATE (a)-[:Route {id: 56356, especie: 70, lat: 54.47, long: -1.07, latR: 54.47, longR: -1.07 }]->(b)
	total_ctr = 0
	for outbreak in response_outbreaks:
		oieid = outbreak[0]
		lat = outbreak[1]
		long = outbreak[2]
		ctr = 0
		print(">> Outbreak: {}".format(oieid))
		for route in new_routes:
			route_id = route["Id"]
			route_species = route["Especie"]
			route_lat = route["Lat"]
			route_long = route["Long"]
			route_latR = route["LatR"]
			route_longR = route["LongR"]
			route_region = route["COMARCA_SG"]

			outbreak_coord = (lat, long)
			route_coord = (route_lat, route_long)

			if geodesic(outbreak_coord, route_coord).kilometers <= 25:
				aux = ("MATCH (a:Outbreak), (b:Region)  WHERE a.oieid = {} AND b.comarca_sg = '{}' "
					"CREATE (a)-[:Route {{id: {}, especie: {}, lat: {}, long: {}, latR: {}, longR: {} }}]->(b);\n").format(
						oieid, route_region,
						route_id, route_species, route_lat, route_long, route_latR, route_longR)

				response = driver.session().run(aux).value()
				route_nodes_query += aux
				ctr += 1

		print("> {} routes found".format(ctr))
		total_ctr += ctr
		cursor.rewind()

	print(">>> {} routes found IN  TOTAL".format(total_ctr))
	return response, route_nodes_query

def main(argv):
	client= MongoClient('mongodb://localhost:27017/')
	db = client.lv
	routes = db.migrations
	outbreaks = db.outbreaks
	regions = db.comarcas
	driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

	start = date.today() + timedelta(days = -date.today().weekday())
	#52 (un anio) + 12 (3 meses) semanas
	this_many_weeks = 64
	start -= timedelta(weeks=this_many_weeks)
	#Convert to datetime
	start = datetime.combine(start, datetime.min.time())

	reset_outbreaks(driver, outbreaks)
	reset_regions(driver, regions)
	reset_routes(driver, routes, outbreaks, start)

	driver.close()
	client.close()

	return

if __name__ == '__main__':
    main(sys.argv[1:])