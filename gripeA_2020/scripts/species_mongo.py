import pandas as pd
import pymongo
from pymongo import MongoClient

file = "data/Datos especies1.xlsx"
#df = pd.read_excel(file, 'Especies_equivalencias')
#df1 = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2 )
df1 = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0)

#df1 = df1.drop([0,1,2],axis=0)

df1 = df1.fillna("")
#forma de acceder a la prob de movimiento segun el codigo de anilla index
#print(df1[3][70])

print(df1.index)
df_mongo = pd.DataFrame({'Nombre cientifico': df1['Nombre científico'], 'Especie': df1['Especie'], 'codigo anilla': df1['codigo anilla']})


client= MongoClient('mongodb://localhost:27017/')
db = client.lv
#Especies
especie = db.especies
records = df_mongo.to_dict(orient='records')  # Here's our added param..

# Borra todo
especie.delete_many({})
#records = json.loads(df.T.to_bson()).values()
especie.insert_many(records)
