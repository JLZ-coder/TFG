import requests
import re
#este sys me suobra mucho y habrá que quitarlo
import sys

import json
import pymongo
from pymongo import MongoClient
from datetime import datetime


#GLOBALS

# NACHO: NO DB INTERACT
#client= MongoClient('mongodb://localhost:27017/')
#db = client.lv
#outbreaks = db.outbreaks

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
	#global outbreaks
	url = 'https://www.oie.int/wahis_2/public/wahid.php/Diseaseinformation/Immsummary/outbreakreport'
	
	r = requests.post(url, data = {'reportid':id, 'summary_country':cty})
	ob,anlist = extract_data(r.content.decode('latin1'))


	if id == '1000059288':
		print(ob)
		print(anlist[0])

	if ob[2] != "" and ob[0] != "":
		end = datetime.strptime(ob[2], "%d/%m/%Y")
		start = datetime.strptime(ob[0], "%d/%m/%Y")

		outbreak = {}
		outbreak["oieid"] = id
		outbreak["diseade_id"] = disease
		outbreak["country"] = cty
		outbreak["start"] = start
		outbreak["status"] = ob[1]
		outbreak["end"] = end
		outbreak["city"] = ob[3]
		outbreak["district"] = ob[4]
		outbreak["subdistrict"] = ob[5]
		outbreak["epiunit"] = ob[6]
		outbreak["location"] = ob[7]
		outbreak["lat"] = ob[8]
		outbreak["long"] = ob[9]
		outbreak["affected_population"] = ob[10]
		if len(anlist)>0:
			outbreak["species"] = anlist[0][0]
			outbreak["at_risk"] = anlist[0][1]
			outbreak["cases"] = anlist[0][2]
			outbreak["deaths"] = anlist[0][3]
			outbreak["preventive_killed"] = anlist[0][4]
		else:
			outbreak["species"] = ""
			outbreak["at_risk"] = ""
			outbreak["cases"] = ""
			outbreak["deaths"] = ""
			outbreak["preventive_killed"] = ""

		print ("Writing {} in database...".format(id))

		#outbreaks.insert_one(outbreak)

def get_cty_obs(code,id,disease, year):
	global ob_ids
	global db
	#global outbreaks

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
		#if outbreaks.find({'oieid':id}).count() == 0:
		print("Getting data of (ID {})          ".format(id))
		get_ob_page(cty,id,lista, disease, year)
		#else:
		#	print ("ID {} Ignored, already in database".format(id))

def main(argv):
	# 15 - Highli Path Avian influenza
	# 201 - Lowi Path Avian influenza
	# 1164 - Highly pathogenic influenza A viruses (infection with) (non-poultry including wild birds) (2017 -) 
	#diseases = ['15', '201', '1164']
	diseases = ['15']
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

	disease_type_hidden = 1 # Terrestrial
	disease_id_hidden = 1 # FMD
	
	for disease_id in diseases:	
		oblist = []
		disease = disease_id
		counter = 0
		for year in range(start_year, finish_year+1):
			#r = requests.post(url, data = {'year':year, 'disease_type_hidden':1, 'disease_id_hidden':disease_id})
			payload = {'year':year, 
			'disease_type':0, 
			'disease_id_terrestrial':15, 
			'disease_type_hidden':0, 
			'disease_id_hidden':15,
			'selected_disease_name_hidden':'h', 
			'disease_id_aquatic':-999}
			#payload = {'year':year, 'disease_type':0, 'disease_id_terrestrial':15, 'disease_type_hidden':'null', 'disease_id_hidden':'null','selected_disease_name_hidden':'null', 'disease_id_aquatic':-999}
			#headers = {'Content-Type': 'application/x-www-form-urlencoded'}
			#r = requests.post(url, data=json.dumps(payload), headers=headers)
			r = requests.post(url, data=payload)
			#r = requests.post(url, data="disease_type_hidden=0&disease_id_hidden=15&selected_disease_name_hidden='h'&disease_type=0&disease_id_terrestrial=15&disease_id_aquatic=-999&year=2020", headers=headers)
			#r = requests.post(url, json=payload)
			print(r.text.encode('utf-8'))
			p = re.compile("outbreak_country\">[ \t\r\n]+([A-Za-z \-.']+)[^(]*\('([A-Z]{3})',([0-9]+)\);",re.DOTALL & re.MULTILINE)
			m = p.findall(r.content.decode('latin1'))
			oblist = oblist + m
		for obs in oblist:
			
			cty, code, id = obs
			print("Outbreak {} of {}".format(counter, len(oblist)))
			print("\rGetting Outbreaks in {}".format(cty))
			if(code in asian_countries) or (code in european_countries):
				print("Getting Outbreaks in {}".format(cty))
				get_cty_obs(code,id, disease, year)
			counter += 1


if __name__ == "__main__":
	main(sys.argv[1:])

