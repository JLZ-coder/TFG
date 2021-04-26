from pymongo import MongoClient
from .Builder import Builder
from neo4j import GraphDatabase
import json
from datetime import datetime, time, timedelta, date

class TempBuilder(Builder):
    def __init__(self):
        super().__init__("temp")

    def create(self, start, end, parameters):
        client = MongoClient('mongodb://localhost:27017/')
        db = client.lv
        temperatura = db.temperatura

        #  tempMin {
            #  idcomarca => temperatura,
            #  idcomarca => temperatura,
            #  idcomarca => temperatura,
            #  ...
            #  ..
            #  .
        # }
        tempMin = {}

        #Semana actual
        this_week = date.today() + timedelta(days = -date.today().weekday())

        if this_week == start:
            cursor = temperatura.find({},{'_id':False, 'comarca_sg':True,'prediccion':True})
            for comarca in cursor:
                tempMin[comarca['comarca_sg']] = comarca['prediccion']

        else:
            this_year = start.year
            days_this_year = start - datetime(this_year-1, 12, 31)
            current_week = int(days_this_year.days / 7)

            cursor = temperatura.find({},{'_id':False, 'comarca_sg':True,'historicoFinal':True})
            for comarca in cursor:
                temp = comarca['historicoFinal'][str(this_year)][current_week]

                if temp != None:
                    tempMin[comarca['comarca_sg']] = temp

                else:
                    i = 0
                    while this_year >= 2017 and temp == None:
                        temp = comarca['historicoFinal'][str(this_year - i)][current_week]
                        i += 1

                    if temp == None:
                        tempMin[comarca['comarca_sg']] = None
                    else:
                        tempMin[comarca['comarca_sg']] = temp

        return tempMin