from datetime import datetime, timedelta, date

class Controller:
    def __init__(self, model):
        self.model = model

    def run(self):
        today = date.today()
        start = today + timedelta(days = -today.weekday()) - timedelta(weeks = 12)
        end = start + timedelta(weeks = 1)

        start = datetime.combine(start, datetime.min.time())
        end = datetime.combine(end, datetime.min.time())

        alertas = list()
        i = 0
        while(i < 12):
            alerta = self.model.run(start, end)
            alertas.append(alerta)
            start = end
            end = start + timedelta(weeks =1)
            i += 1

        return alertas
