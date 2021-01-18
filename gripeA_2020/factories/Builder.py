class Builder:
    def __init__(self, tag):
        self.tag = tag

    def createData(self, dataType):
        data = None
        if (self.tag == dataType):
            data = self.create()

        return data

    def create(self):
        pass