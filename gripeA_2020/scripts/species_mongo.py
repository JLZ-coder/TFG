import pandas as pd
import pymongo
from pymongo import MongoClient

file = "data/Datos especies1.xlsx"
df = pd.read_excel(file, 'Especies_equivalencias')
df1 = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0)

#df1 = df1.drop([0,1,2],axis=0)

df1 = df1.fillna("")
print(df1)

#Especies
especie = db.especies
records = df_especies.to_dict(orient='records')  # Here's our added param..

# Borra todo
especie.delete_many({})
#records = json.loads(df.T.to_bson()).values()
especie.insert_many(records)
