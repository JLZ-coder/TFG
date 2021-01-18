class Quintile:
    def __init__(self, dataFactory)
        self.dataFactory = dataFactory

    def run(self):
        comarca_brotes = self.dataFactory.createData("outbreak")
        # Según los datos calcular las comarcaBrotes
        comarca_brotes_sorted = sorted(comarca_brotes, key=lambda k: len(comarca_brotes[k]), reverse=True)
        alertas = dict()

        # Cuartiles
        alertaMax = 5
        porcentaje = 0.2
        percentil = math.ceil(len(comarca_brotes_sorted) * porcentaje)
        cont = 1
        for comarca in comarca_brotes_sorted:
            alertas[comarca] = {"start" : semana_inicio, "end" : semana_fin, "nivel" : alertaMax}

            if cont == percentil:
                alertaMax -= 1
                porcentaje += 0.2
                percentil = math.ceil(len(comarca_brotes_sorted) * porcentaje)

            cont += 1

        return alertas
