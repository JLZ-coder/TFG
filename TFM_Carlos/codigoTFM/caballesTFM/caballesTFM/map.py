import geohash
import pymongo
from pymongo import MongoClient
import folium
import sys
import dateparser
import pandas as pd
from datetime import datetime
import math
import geohash


client= MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
migrations = db.migrations

european_countries = ['ALB', 'DEU', 'AND', 'AUT', 'BEL', 'BLR', 'BIH', 'BGR', 'CYP', 'HRV', 'DNK', 'SVK', 'SVN', 'ESP', 'EST',
                      'FIN', 'FRA', 'GRC', 'HUN', 'IRL', 'ISL', 'ITA', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO', 
                      'MNE', 'NOR', 'NLD', 'POL', 'PRT', 'GBR', 'CZE', 'ROU', 'RUS', 'SMR', 'SRB', 'SWE', 'CHE', 'UKR', 'VAT']


def map_generate(start, end, specie):
    
    mapcolors={
       1340: '#04B404',
       1610: '#FE2E64',
    }
    
    mapdiseases = {
        '15': "Highli Path Avian influenza",
        '201': "Lowi Path Avian influenza",
        '1164': "Highly pathogenic influenza A viruses (infection with)",
    }

    map = folium.Map(location=[40.416906, -3.7056721],
                     tiles='Stamen Terrain',
                     zoom_start=5)

    start = dateparser.parse(str(start))
    end = dateparser.parse(str(end))

    geohashes = []
    for country in european_countries:
        data_outbreaks = outbreaks.find({"country": country, "start":{"$gte": start, "$lte":end }})
        for data in data_outbreaks:
            if data['lat'] == None or data['end'] == None or data['start'] == None:
                continue
            if data['cases'] == "" or data['cases' ]== "0":
                if data['deaths'] == "" or data['deaths'] == '0':
                    continue
                try:
                    radio = math.log(int(data['deaths'])) * 1000 
                except:
                    print("No se puede representar este brote: {}".format(data))
            else:
                try:
                    radio = math.log(int(data['cases'])) * 1000
                except:
                    print("No se puede representar este brote: {}".format(data))
                
            start_date = data['start'].strftime("%Y/%m/%d")	 		
            if data['end'] != "":
                end_date = data['end'].strftime("%Y/%m/%d")
            else:
                end_date = "Continue"
            message="<b>Start:</b> {} <br> <b>Status:</b> {} <br> <b>End:</b> {}".format(start_date,data['status'],
                                                                                         end_date)
            
            popup_message = """
            <p><b>Disease:</b> {}<br>
            <b>Start:</b> {}<br>
            <b>End:</b> {}<br>
            <b>Status:</b> {}<br>
            <b>Cases:</b> {}<br>
            <b>Deaths:</b> {}<br>
            <b>More Information:</b> {}<br>
            </p> 
            """.format(mapdiseases[data["diseade_id"]], data["start"], data["end"],
                      data["status"], data["cases"], data["deaths"], data["affected_population"])
            
            folium.Circle(
                location=[float(data['lat']), float(data['long'])],
                radius = radio,
                fill = True,
                popup=folium.Popup(popup_message, max_width=400),
                tooltip=message
                ).add_to(map)
            geohashes.append(data['geohash'][:4])


    if specie == 0:
      migrations_data = migrations.find({ "$or": [{"Especie": 1610}, {"Especie": 1340}] , 
                                   "FechaAnillamiento": {"$gte": start, "$lte":end }, 
                                   "FechaRecuperacion": {"$gte": start, "$lte":end }},
                                 )
    else:
      migrations_data = migrations.find({"Especie": specie, 
                                       "FechaAnillamiento": {"$gte": start, "$lte":end }, 
                                       "FechaRecuperacion": {"$gte": start, "$lte":end }},
                                     )

    for migration in migrations_data:
        if migration["geohash"][:4] in geohashes or migration["geohashR"][:4] in geohashes:
            new_coordinates= [(float(migration["Lat"]),float(migration["Long"])),
                              (float(migration["LatR"]),float(migration["LongR"]))]
            
            popup_message = """
            <p><b>Origin Date:</b> {}<br>
            <b>Origin location:</b> {}<br>  
            <b>Origin municipality:</b> {}<br>
            <b>Origin province:</b> {}<br> 
            <b>Destiny Date:</b> {}<br> 
            <b>Destiny location:</b> {}<br> 
            <b>Destiny municipality:</b> {}<br> 
            <b>Destiny province:</b> {}</p>
            """.format(migration["FechaAnillamiento"], migration["Localidad"], 
                       migration["Municipio"], migration["Provincia"],
                       migration["FechaRecuperacion"], migration["LocalidadR"], 
                       migration["MunicipioR"], migration["ProvinciaR"])

            folium.PolyLine(
                        locations=new_coordinates,
                        color=mapcolors[int(migration["Especie"])],
                        weight=1.5,
                        tooltip='From {} ({}) to {} ({})'.format(migration["Localidad"], migration["Provincia"],
                                                                 migration["LocalidadR"], migration["ProvinciaR"]),
                        popup=folium.Popup(popup_message, max_width=300),
                        ).add_to(map) 
            
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 140px; height: 100px; 
     border:2px solid grey; z-index:9999; font-size:12px;
     ">&nbsp; <b>Legend</b> <br>
     &nbsp; Outbreak &nbsp; <i class="fa fa-circle fa-2x"
                  style="color:#339af0"></i><br>
     &nbsp; Ciconia Migration &nbsp; <i class="fa fa-minus fa-2x" style="color:#04B404"></i><br>
     &nbsp; Anser Migration &nbsp; <i class="fa fa-minus fa-2x"
                  style="color:#FE2E64"></i><br>
      </div>
     '''

    map.get_root().html.add_child(folium.Element(legend_html))

    map.save('caballesTFM/templates/public/folium_map.html')

if __name__ == "__main__":
	map_generate("01/01/2020","01/03/2020",0)


