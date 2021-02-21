

class ModelSelector:
    def __init__(self, dataFactory):
        self.dataFactory = dataFactory
        self.parameters = dict()
        _init()

    def _init(self):
        self.models = list()
        models.append(ModelV0(self.dataFactory))
        models.append(ModelV1(self.dataFactory))
        self.currentModel = models[0]

    def setModel(self, modelTag):
        modelo = None

        for model in self.models:
            modelo = model.create(modelTag)
            if modelo != None:
                break

        if (modelo != None):
            self.currentModel = modelo

    def setParameters(self, parameters):
        self.parameters = parameters

    def run(self, start, end):
        self.currentModel.run(start, end, self.parameters)
