class Builder:
    def __init__(self, tag):
        self.tag = tag

    def createData(self, dataType, start, end, parameters):
        data = None
        if (self.tag == dataType):
            data = self.create(start, end, parameters)

        return data

    def create(self):
        pass