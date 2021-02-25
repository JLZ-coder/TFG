

class Factory:
    def __init__(self, builders):
        self.builders = builders

    def createData(self, dataType, start, end, parameters):
        datos = None

        for builder in self.builders:
            datos = builder.createData(dataType, start, end, parameters)
            if datos != None:
                break

        return datos