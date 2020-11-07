import geohash
import pymongo
from pymongo import MongoClient
import folium
from datetime import datetime
from datetime import timedelta
from py2neo import Graph
import math

graph = Graph("bolt://localhost:7687", auth=("neo4j", "ed4r;bnf"))
client= MongoClient('mongodb://localhost:27017/')
db = client.lv
outbreaks = db.outbreaks
migrations = db.migrations


european_countries = ['ALB', 'DEU', 'AND', 'AUT', 'BEL', 'BLR', 'BIH', 'BGR', 'CYP', 'HRV', 'DNK', 'SVK', 'SVN', 'ESP', 'EST',
                      'FIN', 'FRA', 'GRC', 'HUN', 'IRL', 'ISL', 'ITA', 'LVA', 'LIE', 'LTU', 'LUX', 'MKD', 'MLT', 'MDA', 'MCO', 
                      'MNE', 'NOR', 'NLD', 'POL', 'PRT', 'GBR', 'CZE', 'ROU', 'RUS', 'SMR', 'SRB', 'SWE', 'CHE', 'UKR', 'VAT']



def map_alerts(days):
    mapdiseases = {
        '15': "Highli Path Avian influenza",
        '201': "Lowi Path Avian influenza",
        '1164': "Highly pathogenic influenza A viruses (infection with)",
    }
    
    map = folium.Map(location=[47.9600202, 9.9153559],
                     tiles='Stamen Terrain',
                     zoom_start=5)
    
    mapcolors={
       'MIGRA1340': '#04B404',
       'MIGRA1610': '#FE2E64',
    }
    #datetime (2017, 1, 1, 0, 0, 0)
    end = datetime.now()
    delta = timedelta(days = int(days))
    start = end - delta

    for country in european_countries:
        data_outbreaks = outbreaks.find({"country": country, "start":{"$gte": start, "$lte":end }})
        for data in data_outbreaks:
            if data['lat'] == None or data['end'] == None or data['start'] == None:
                continue
            if data['cases'] == "" or data['cases' ]== "0":
                if data['deaths'] == "" or data['deaths'] == '0':
                    continue
                try:
                    radio = math.log(int(data['deaths'])) * 5000 
                except:
                    print("No se puede representar este brote: {}".format(data))
            else:
                try:
                    radio = math.log(int(data['cases'])) * 5000
                except:
                    print("No se puede representar este brote: {}".format(data))
                
            start_date = data['start'].strftime("%Y/%m/%d")
            end_date = data['end'].strftime("%Y/%m/%d")
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
            
            query = "MATCH p=(a:Region{location:"
            query += "'{}'".format(data['geohash'][:4])
            query += "})-[r]->(b) RETURN r.valor, b.location, b.localidad, b.municipio, b.provincia, type(r)"

            migrations = graph.run(query).data()
            origin_coordinates_f = [0, 0]
            destiny_coordinates_f = [0, 0]
            
            for migration in migrations:
                origin_coordinates = geohash.decode(data['geohash'])
                origin_coordinates_f[0] = float(origin_coordinates[0])
                origin_coordinates_f[1] = float(origin_coordinates[1])
                
                destiny_coordinates = geohash.decode(migration["b.location"])
                destiny_coordinates_f[0] = float(destiny_coordinates[0])
                destiny_coordinates_f[1] = float(destiny_coordinates[1])
                coordinates= (origin_coordinates_f,destiny_coordinates_f)
                folium.PolyLine(
                    locations=coordinates,
                    color= mapcolors[migration['type(r)']],
                    weight= 1,
                    ).add_to(map) 
                popup_message = """
                    <b>Destiny location:</b> {}<br> 
                    <b>Destiny municipality:</b> {}<br> 
                    <b>Destiny province:</b> {}<br> 
                    <b>Sightings:</b> {} <br> 
                    """.format(migration["b.localidad"], migration["b.municipio"], 
                               migration["b.provincia"], migration["r.valor"])
                folium.Circle(
                    location= destiny_coordinates_f,
                    radius = 25000,
                    fill=True, # Set fill to True
                    fill_color='orange',
                    color = 'orange',
                    popup=folium.Popup(popup_message, max_width=400),
                    fill_opacity=math.log(migration["r.valor"]),
                    ).add_to(map)


    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 140px; height: 130px; 
     border:2px solid grey; z-index:9999; font-size:12px;
     ">&nbsp; <b>Legend</b> <br>
     &nbsp; Outbreak &nbsp; <i class="fa fa-circle fa-2x"
                  style="color:#339af0"></i><br>
     &nbsp; Alert &nbsp; <i class="fa fa-circle fa-2x"
                  style="color:orange"></i><br>
     &nbsp; Ciconia Migration &nbsp; <i class="fa fa-minus fa-2x" style="color:#04B404"></i><br>
     &nbsp; Anser Migration &nbsp; <i class="fa fa-minus fa-2x"
                  style="color:#FE2E64"></i><br>
      </div>
     '''

    map.get_root().html.add_child(folium.Element(legend_html))
                   
    map.save('caballesTFM/templates/public/folium_alert_map.html')
        