from pymongo import MongoClient
import os
from neo4j import GraphDatabase
from geopy.distance import geodesic
import sys
from geolib import geohash

# Usa los datos de migraciones en mongo para hacer un grafo en neo4j

TAM_GEO = 4

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
def update_regions(driver, regions):
	print(">>> Update Regions")
	cursor = regions.find({})

	response = driver.session().run('MATCH (x:Region) RETURN x.comarca_sg').values()

	existing_comarca_sg = set()
	for comarca_sg in response:
		existing_comarca_sg.add(comarca_sg[0])

	new_regions = list(filter(lambda region: region["comarca_sg"] not in existing_comarca_sg, cursor))

	regions_nodes_query = ""
	# (288337:Outbreak {comarca_sg: 288337, lat: 54.47, long: -1.07})
	for region in new_regions:
		comarca_sg = region["comarca_sg"]
		lat = region["Latitud"]
		long = region["Longitud"]

		aux = "(:Region {{ comarca_sg:'{}', lat:{}, long:{} }} ),\n".format(comarca_sg, lat, long)
		regions_nodes_query += aux

	response = ""
	if regions_nodes_query != "":
		regions_nodes_query = "CREATE " + regions_nodes_query[:-2]
		response = driver.session().run(regions_nodes_query).value()

	return response, regions_nodes_query

# Nodos de todas las comarcas, solo una vez al principio.
def reset_routes(driver, routes):
	print(">>> Reset Routes")
	cursor = routes.find({}, no_cursor_timeout=True)

	# Borra todo las comarcas que hay en neo4j!!!!!
	driver.session().run("MATCH ()-[n:Route]->() DETACH DELETE n")

	route_nodes_query = ""
	# MATCH (a:Outbreak), (b:Region)
   	# WHERE a.oieid = 288337 AND b.comarca_sg = SP24108
	# CREATE (a)-[:Route {id: 56356, especie: 70, lat: 54.47, long: -1.07, latR: 54.47, longR: -1.07 }]->(b)
	total_ctr = 0
	for route in cursor:
		route_geohash = route["geohash"][:TAM_GEO]
		route_species = route["Especie"]
		route_lat = route["Lat"]
		route_long = route["Long"]
		route_latR = route["LatR"]
		route_longR = route["LongR"]
		route_region = route["COMARCA_SG"]

		aux = ("MATCH (a:geoRegion), (b:Region)  WHERE a.region_geohash = '{}' AND b.comarca_sg = '{}' "
			"CREATE (a)-[:Route {{especie: {}, lat: {}, long: {}, latR: {}, longR: {} }}]->(b);\n").format(
				route_geohash, route_region,
				route_species, route_lat, route_long, route_latR, route_longR)

		response = driver.session().run(aux).value()
		route_nodes_query += aux
		total_ctr += 1
	cursor.close()

	print(">>> {} routes found IN  TOTAL".format(total_ctr))
	return response, route_nodes_query

# Nodos de los nuevos brotes
def update_routes(driver, routes):
	print(">>> Update Routes")
	cursor = routes.find({}, no_cursor_timeout=True)

	response = driver.session().run('MATCH (:geoRegion)-[x:Route]->(:Region) RETURN x.especie, x.lat, x.long, x.latR, x.longR').values()

	existing_routes = set()
	for route in response:
		existing_routes.add(route)

	new_routes = list(filter(lambda route: [route["Especie"], route["Lat"], route["Long"], route["LatR"], route["LongR"]] not in existing_routes, cursor))

	route_nodes_query = ""
	# MATCH (a:Outbreak), (b:Region)
   	# WHERE a.oieid = 288337 AND b.comarca_sg = SP24108
	# CREATE (a)-[:Route {id: 56356, especie: 70, lat: 54.47, long: -1.07, latR: 54.47, longR: -1.07 }]->(b)
	total_ctr = 0
	for route in new_routes:
		route_geohash = route["geohash"][:TAM_GEO]
		route_species = route["Especie"]
		route_lat = route["Lat"]
		route_long = route["Long"]
		route_latR = route["LatR"]
		route_longR = route["LongR"]
		route_region = route["COMARCA_SG"]

		aux = ("MATCH (a:geoRegion), (b:Region)  WHERE a.region_geohash = '{}' AND b.comarca_sg = '{}' "
			"CREATE (a)-[:Route {{especie: {}, lat: {}, long: {}, latR: {}, longR: {} }}]->(b);\n").format(
				route_geohash, route_region,
				route_species, route_lat, route_long, route_latR, route_longR)

		response = driver.session().run(aux).value()
		route_nodes_query += aux
		total_ctr += 1
	cursor.close()

	print(">>> {} routes found IN  TOTAL".format(total_ctr))
	return response, route_nodes_query

# Nodos de todas las comarcas, solo una vez al principio.
def reset_geoRegion(driver, routes):
	print(">>> Reset geoRegion")
	cursor = routes.find({})

	geoRegion_nodes_query = ""
	# (SP49108:route {comarca_sg: 'SP49108', lat: 54.47, long: -1.07})
	geohash_set = set()
	for route in cursor:
		region_geohash = route["geohash"][:TAM_GEO]
		lat, long = geohash.decode(region_geohash)
		
		if region_geohash not in geohash_set:
			aux = "(:geoRegion {{ region_geohash:'{}', lat:{}, long:{} }} ),\n".format(region_geohash, lat, long)
			geoRegion_nodes_query += aux
			geohash_set.add(region_geohash)

	response = ""
	if geoRegion_nodes_query != "":
		geoRegion_nodes_query = "CREATE " + geoRegion_nodes_query[:-2]
		# Borra todo las comarcas que hay en neo4j!!!!!
		driver.session().run("MATCH (n:geoRegion) DETACH DELETE n")
		response = driver.session().run(geoRegion_nodes_query).value()

	return response, geoRegion_nodes_query

# Nodos de los nuevos brotes
def update_geoRegion(driver, routes):
	print(">>> Update geoRegion")
	cursor = routes.find({})

	response = driver.session().run('MATCH (x:geoRegion) RETURN x.region_geohash').values()

	existing_region_geohash = set()
	for region_geohash in response:
		existing_region_geohash.add(region_geohash[0])

	new_geoRegions = list(filter(lambda route: route["geohash"] not in existing_region_geohash, cursor))

	geoRegion_nodes_query = ""
	# (288337:Outbreak {comarca_sg: 288337, lat: 54.47, long: -1.07})
	for route in new_geoRegions:
		region_geohash = route["geohash"][:TAM_GEO]
		lat, long = geohash.decode(region_geohash)

		aux = "(:geoRegion {{ region_geohash:'{}', lat:{}, long:{} }} ),\n".format(region_geohash, lat, long)
		geoRegion_nodes_query += aux

	response = ""
	if geoRegion_nodes_query != "":
		geoRegion_nodes_query = "CREATE " + geoRegion_nodes_query[:-2]
		response = driver.session().run(geoRegion_nodes_query).value()

	return response, geoRegion_nodes_query

def delete_all(driver):
	# Borra todo las comarcas que hay en neo4j!!!!!
	return driver.session().run("MATCH (n) DETACH DELETE n")

def main(argv):
	client= MongoClient('mongodb://localhost:27017/')
	db = client.lv
	routes = db.migrations
	regions = db.comarcas
	driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

	reset_regions(driver, regions)
	reset_geoRegion(driver, routes)
	reset_routes(driver, routes)

	driver.close()
	client.close()

	return

if __name__ == '__main__':
    main(sys.argv[1:])