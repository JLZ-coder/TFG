from .Builder import Builder
import pandas as pd
from datetime import datetime, timedelta, date

class MigrationProbBuilder(Builder):
    def __init__(self):
        super().__init__("migration_prob")

    def create(self, start, end, parameters):

        file = "data/Datos especies1.xlsx"
        matrizEspecies = pd.read_excel(file, 'Prob_migracion', skiprows=3, usecols='A:AY', header=0, index_col=2)

        current_date = start

        #Calculamos la columna con la probabildad de migracion de esta semana
        current_week = 4 * ( int(current_date.strftime("%m")) - 1 )
        extra_days = int( ( (int(current_date.strftime("%d")) - 1) / 7 ) + 1)
        if extra_days > 4:
            extra_days = 4
        current_week += extra_days

        ret_week = current_week

        current_week_days = 0
        next_week = current_week + 1
        #Hasta que no hayamos cambiado al siguiente numero de columna o si despues de 7 dias no hemos cambiado
        while next_week != current_week and current_week_days < 7:
            #Aumento en 1 el dia
            current_date = current_date + timedelta(days=1)

            #Recalculo la semana para ver si es diferente
            current_week = 4 * (int(current_date.strftime("%m")) - 1)
            extra_days = int( ( (int(current_date.strftime("%d")) - 1) / 7 ) + 1)
            if extra_days > 4:
                extra_days = 4
            current_week += extra_days

            #Contador
            current_week_days +=1

        col_number_and_days = dict()
        col_number_and_days = {
            "current_week" : ret_week,
            "next_week" : ret_week + 1,
            "current_week_days" : current_week_days
        }

        return col_number_and_days