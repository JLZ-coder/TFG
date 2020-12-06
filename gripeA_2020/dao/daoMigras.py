from dao.daoMongo import daoMongo
from transfer.transferMigra import transferMigra

class daoMigras(daoMongo):

    def __init__(self):
        super()
        self._doc = self._collection.migrations

    def read(self, ident = []):
        ret = []
        query = {}
        if len(ident) > 0:
            query['index'] = {'$in' : ident}

        cursor = self._doc.find(query)
        for it in cursor:
            t = transferMigra(it)
            ret.append(t)

        return ret

    def create(self):
        raise Exception("Create de daoMigras")

    def update(self):
        raise Exception("Update de daoMigras")

    def delete(self, ident = []):
        # ret = []
        # query = {}
        # if len(ident) > 0:
        #     query['oieid'] = {'$in' : ident}
        #     delet = self._doc.delete_many(query)
        #     return delet.deleted_count()
        # else:
        #     return 0
        raise Exception("Delete de daoMigras")

    def delete_all(self):
        delet = self._doc.delete_many({})
        return delet.deleted_count()