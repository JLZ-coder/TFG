from .ModelV0 import ModelV0
from .ModelV1 import ModelV1

class ModelSelector:
    def __init__(self):
        self.parameters = dict()
        self.data = dict()
        self._init()

    def _init(self):
        self.models = list()
        self.models.append(ModelV0())
        self.models.append(ModelV1())
        self.currentModel = self.models[1]

    def setModel(self, modelTag):
        modelo = None

        for model in self.models:
            modelo = model.create(modelTag)
            if modelo != None:
                break

        if (modelo != None):
            self.currentModel = modelo

    def getParameters(self):
        return self.parameters

    def setParameters(self, parameters):
        self.parameters = parameters

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def run(self, start, end):
        return self.currentModel.run(start, end, self.data, self.parameters)
