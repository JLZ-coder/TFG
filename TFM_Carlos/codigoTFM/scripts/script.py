import requests
import re
#este sys me suobra mucho y habrá que quitarlo
import sys

import json
import pymongo
from pymongo import MongoClient
from datetime import datetime
import geohash
import pandas as pd

#GLOBALS

client= MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks

def extract_data( page ):
	out = ''
	p = re.compile('start of the event</td>[^>]+>(\d{1,2}/\d{1,2}/\d{4}).*?'
					'Outbreak Status</td>[^>]+>(\w+).*?'
					'resolution of the outbreak</td>[^>]+>(\d{1,2}/\d{1,2}/\d{4})?.*?'
					'ta_left">[^<]+</td>[^>]+>(\w+)?.*?'
					'ta_left">[^<]+</td>[^>]+>(\w+)?.*?'
					'ta_left">[^<]+</td>[^>]+>(\w+)?.*?'
					'Unit Type</td>[^>]+>(\w+).*?'
					'Location</td>[^>]+>(\w+).*?'
					'Latitude</td>[^>]+>(-?\d+\.\d+).*?'
					'Longitude</td>[^>]+>(-?\d+\.\d+).*?'
					'Description of Affected Population</td>[^>]+>(.*?)</td>',re.DOTALL & re.MULTILINE * re.IGNORECASE)

	m = p.findall(page)
	if len(m) > 0:
		out = m[0]
	else:
		out = ('','','','','','','','','','', '')
	p = re.compile('vacborder">([^<]*)?</td>.*?'
					'vacborder">(\d+)?</td>.*?'
					'vacborder">(\d+)?</td>.*?'
					'vacborder">(\d+)?</td>.*?'
					'vacborder(?: last)?">(\d+)?</td>.*?',re.DOTALL & re.MULTILINE * re.IGNORECASE)
	m = p.findall(page)
	return out,m


def get_ob_page(cty,id,lista, disease, year):
	global outbreaks
	url = 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary/outbreakreport'
	r = requests.post(url, data = {'reportid':id, 'summary_country':cty})
	#ob,anlist = extract_data(r.content.decode('latin1'))

	print("Getting more info for id {}".format(id))
	#print(r.text.encode('utf-8'))
	#dfs = pd.read_html(r.content.decode('latin1'),match='County', attrs = {'class' : 'Table27'} )
	dfs = pd.read_html(r.content.decode('latin1'), attrs = {'class' : 'Table27'}, index_col = 0)
	table = dfs[0]
	table.dropna(inplace=True,thresh=1)
	#if id == '1000059288':
	#	print(ob)
	#	print(anlist[0])

	#if ob[2] != "" and ob[0] != "":
	if 'Latitude' in table.index:
		#end = datetime.strptime(ob[2], "%d/%m/%Y")
		#start = datetime.strptime(ob[0], "%d/%m/%Y")
		start = datetime.strptime(table.loc['Date of start of the event'][1], "%d/%m/%Y")
		outbreak = {}
		outbreak["oieid"] = id
		outbreak["diseade_id"] = disease
		outbreak["country"] = cty
		outbreak["start"] = start
		outbreak["status"] = table.loc['Outbreak Status'][1]
		#outbreak["status"] = ob[1]
		if 'Date of resolution of the outbreak' in table.index:
			outbreak["end"] = datetime.strptime(table.loc['Date of resolution of the outbreak'][1], "%d/%m/%Y")
		else:
			outbreak["end"] = ""

		if 'Province' in table.index:
			outbreak["city"] = table.loc['Province'][1]
		else:
			outbreak["city"] = ""

		if 'District' in table.index:
			outbreak["district"] = table.loc['District'][1]
		else:
			outbreak["district"] = ""

		if 'Sub-district' in table.index:
			outbreak["subdistrict"] = table.loc['Sub-district'][1] 
		else:
			outbreak["subdistrict"] = ""
		
		if 'Epidemiological Unit Type' in table.index:
			outbreak["epiunit"] = table.loc['Epidemiological Unit Type'][1]
		else:
			outbreak["epiunit"] = ""
		
		if 'Location' in table.index:
			outbreak["location"] = table.loc['Location'][1]
		else:	
			outbreak["location"] = ""		
		outbreak["lat"] = table.loc['Latitude'][1]
		outbreak["long"] = table.loc['Longitude'][1] 
		
		if 'Description of Affected Population' in table.index:
			outbreak["affected_population"] = table.loc['Description of Affected Population'][1]
		else:
			outbreak["affected_population"] = "Unknown"
		hash = geohash.encode(float(outbreak["lat"]), float(outbreak["long"]))
		outbreak["geohash"] = hash
		outbreak["lastEntry"] = True
		#outbreak["city"] = ob[3]
		#outbreak["district"] = ob[4]
		#outbreak["subdistrict"] = ob[5]
		#outbreak["epiunit"] = ob[6]
		#outbreak["location"] = ob[7]
		#outbreak["lat"] = ob[8]
		#outbreak["long"] = ob[9]
		#outbreak["affected_population"] = ob[10]
		#if len(anlist)>0:
		if int(table.loc['Total Animals'][1])>0:
			#outbreak["species"] = anlist[0][0]
			#outbreak["at_risk"] = anlist[0][1]
			#outbreak["cases"] = anlist[0][2]
			#outbreak["deaths"] = anlist[0][3]
			#outbreak["preventive_killed"] = anlist[0][4]
			outbreak["species"] = "Birds"
			outbreak["at_risk"] = table.loc['Total Animals'][1]
			outbreak["cases"] = table.loc['Total Animals'][2]
			outbreak["deaths"] = table.loc['Total Animals'][3]
			outbreak["preventive_killed"] = table.loc['Total Animals'][4]


		else:
			outbreak["species"] = ""
			outbreak["at_risk"] = ""
			outbreak["cases"] = ""
			outbreak["deaths"] = ""
			outbreak["preventive_killed"] = ""

		print ("Writing id {} in database. lat {} long {} country {}".format(id,outbreak["lat"],outbreak["long"],outbreak["country"]))

		outbreaks.insert_one(outbreak)

def get_cty_obs(code,id,disease, year):
	global ob_ids
	global db
	global outbreaks

	lista = []
	url = 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary/listoutbreak'
	r = requests.post(url, data = {'reportid':id, 'summary_country':code})
	p = re.compile('outbreak_report\("([A-Z]{3})",([0-9]+)\)',re.DOTALL & re.MULTILINE * re.IGNORECASE)
	ob_list = p.findall(r.content.decode('latin1'))
	print('Getting data for outbreak of disease {} in country {}\n'.format(id, code))
	total = len(ob_list)
	count = 1
	for ob in ob_list:
		cty,id = ob
		#miramos si está en la bbdd y si no está la leemos
		if outbreaks.find({'oieid':id}).count() == 0:
			print("Getting data of (ID {})          ".format(id))
			get_ob_page(cty,id,lista, disease, year)
		else:
			print ("ID {} Ignored, already in database".format(id))

def main(argv):
	# 15 - Highli Path Avian influenza
	# 201 - Lowi Path Avian influenza
	# 1164 - Highly pathogenic influenza A viruses (infection with) (non-poultry including wild birds) (2017 -) 
	diseases = ['15', '201', '1164']
	global lista
	global disease;
	asian_countries = ['AFG', 'ARM', 'AZE', 'BHR', 'BGD', 'BTN', 'CHN', 'CYP', 'KHM', 'TWN', 'GEO', 'HKG', 'IND', 'IDN', 'IRN', 
					   'IRQ', 'ISR', 'JPN', 'JOR', 'KAZ', 'KOR', 'KWT', 'KGZ', 'LAO', 'LBN', 'MYS', 'MNG', 'MDV', 'MMR', 'PAK', 
					   'NPL', 'OMN', 'PRK', 'PSE', 'PHL', 'QAT', 'RUS', 'SAU', 'SGP', 'LKA', 'SYR', 'TJK', 'TLS', 
					   'THA', 'TUR', 'TKM', 'ARE', 'UZB', 'VNM', 'YEM']

	european_countries = ['ALB', 'DEU', 'AND', 'AUT', 'BEL', 'BLR', 'BIH', 'BGR', 'CYP', 'HRV', 'DNK', 'SVK', 'SVN', 'ESP', 'EST',
						  'FIN', 'FRA', 'GRC', 'HUN', 'IRL', 'ISL', 'ITA', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO', 
						  'MNE', 'NOR', 'NLD', 'POL', 'PRT', 'GBR', 'CZE', 'ROU', 'RUS', 'SMR', 'SRB', 'SWE', 'CHE', 'UKR', 'VAT']

	url= 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary'

	start_year = 2020
	finish_year = 2020

	disease_type_hidden = 0 # Terrestrial
	#disease_id_hidden = 1 # FMD
	
	for disease_id in diseases:	
		oblist = []
		disease = disease_id
		disease_id_terrestrial = disease_id
		disease_type = 0
		counter = 0
		for year in range(start_year, finish_year+1):
			#r = requests.post(url, data = {'year':year, 'disease_type_hidden':1, 'disease_id_hidden':disease_id})
			payload = {'year':year,
				   'disease_type_hidden':disease_type_hidden, 
				   'disease_id_hidden':disease_id,
				    'selected_disease_name_hidden':'h',
				    'disease_type': disease_type, 
				    'disease_id_terrestrial':disease_id_terrestrial,
				    'disease_id_aquatic':-999
				  }
	
			r = requests.post(url, data =payload)
			# The re line below was only parsing the first outbreak per country
			#p = re.compile("outbreak_country\">[ \t\r\n]+([A-Za-z \-.'\(\)]+)[^(]*\('([A-Z]{3})',([0-9]+)\);",re.DOTALL & re.MULTILINE)
			p = re.compile("outbreaklist\('([A-Z]{3})',([0-9]+)\);",re.DOTALL & re.MULTILINE)
			m = p.findall(r.content.decode('latin1'))
			oblist = oblist + m
			
			#display_html(r.content.decode('latin1'), raw=True)
			# NACHO. try html_read
			#dfs = pd.read_html(r.content.decode('latin1'),match='Country name',header=0, attrs = {'class' : 'Table27'}, flavor='html5lib', converters={'Number of outbreaks' : str})
			#table = dfs[0]
			#table.dropna(subset = ['Status'], inplace=True)
			#print(table.head(5))	
			#print(r.text.encode('utf-8'))
			#return 

		for obs in oblist:
			
			#cty, code, id = obs
			code, id = obs
			print("Outbreak {} of {}. Disease {} Year {}".format(counter, len(oblist), disease_id, year))
			print("\rGetting Outbreaks with code {} id {}".format(code, id))
			if(code in asian_countries) or (code in european_countries):
				print("Country code is relevant. Getting more info")
				get_cty_obs(code,id, disease, year)
			counter += 1


if __name__ == "__main__":
	main(sys.argv[1:])

