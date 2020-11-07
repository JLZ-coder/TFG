import geohash

import pymongo
from pymongo import MongoClient

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
migrations = db.migrations

data_outbreaks = outbreaks.find({})

for data in data_outbreaks:
	print (data['oieid'])

	if (data['lat'] != "") and (data['long'] != ""):
		hash = geohash.encode(float(data['lat']), float(data['long']))
		result = outbreaks.update_one( 
			{ '_id': data["_id"]},
  			{'$set' : {'geohash' : hash}}
  		)
	

data_migrations = migrations.find({})
for data in data_migrations:
	hash = geohash.encode(float(data['Lat']), float(data['Long']))
	hashR = geohash.encode(float(data['LatR']), float(data['LongR']))
	result = migrations.update_one( 
		{ '_id': data["_id"]},
  		{'$set' : {'geohash' : hash, 'geohashR' : hashR}}
  	) 

