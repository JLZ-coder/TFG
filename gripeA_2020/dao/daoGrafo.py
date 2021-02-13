from dao.daoNeo4j import daoNeo4j

class daoGrafo(daoNeo4j):

    def __init__(self):
        super()

    def read(self, match = "", where = "", withNeo="", ret = ""):
        m = "MATCH " + match
        w = " WHERE " + where
        wi = " starts with {}".format(withNeo)
        r = " RETURN " + ret

        if match == "":
            m = ""
        if where == "":
            w = ""
        if withNeo == None:
            wi = ""
        if ret == "":
            r = ""

        query = m + w + wi + r

        response = self._session.run(query).values()

        ret = []

        for r in response:
            ret.append([r[0], r[1]])

        return ret

    def create(self, create):
        crea = "CREATE "
        query = crea + create

        return self._session.run(query)

    def update(self, match = "", where = "", se = "", ret = ""):
        m = " MATCH " + match
        w = " WHERE " + where
        s = " SET " + se
        r = " RETURN " + ret

        if match == "":
            m = ""
        if where == "":
            w = ""
        if se == "":
            s = ""
        if ret == "":
            r = ""

        query = m + w + s + r

        return self._session.run(query)

    def delete(self, match = "", where = "", ret = ""):
        m = " MATCH " + match
        w = " WHERE " + where
        r = " DETACH DELETE " + ret

        if match == "":
            m = ""
        if where == "":
            w = ""
        if ret == "":
            r = ""

        query = m + w + r

        return self._session.run(query)