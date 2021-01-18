class Builder:
    def __init__(self, tag):
        self.tag = tag

    def createData(self, dataType, start, end):
        data = None
        if (self.tag == dataType):
            data = self.create(start, end)

        return data

    def create(self):
        pass