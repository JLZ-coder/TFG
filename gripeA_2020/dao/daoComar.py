from dao.daoMongo import daoMongo
from transfer.transferComar import transferComar

class daoComar(daoMongo):

    def __init__(self):
        super()
        self._doc = self._collection.comarcas

    def read(self, ident = []):
        ret = []
        query = {}
        if len(ident) > 0:
            query['comarca_sg'] = {'$in' : ident}

        cursor = self._doc.find(query)
        for it in cursor:
            t = transferComar(it)
            ret.append(t)

        return ret

    def create(self):
        raise Exception("Create de daoBrotes")

    def update(self):
        raise Exception("Update de daoBrotes")

    def delete(self, ident = []):
        # ret = []
        # query = {}
        # if len(ident) > 0:
        #     query['oieid'] = {'$in' : ident}
        #     delet = self._doc.delete_many(query)
        #     return delet.deleted_count()
        # else:
        #     return 0
        raise Exception("Delete de daoBrotes")

    def delete_all(self):
        delet = self._doc.delete_many({})
        return delet.deleted_count()