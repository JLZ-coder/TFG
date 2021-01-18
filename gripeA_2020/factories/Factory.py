

class Factory:
    def __init__(self, builders):
        self.builders = builders

    def createData(self, dataType):
        datos = None

        for builder in self.builders:
            datos = builder.createData(dataType)
            if datos != None:
                break;

        return datos