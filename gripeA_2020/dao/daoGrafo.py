import neo4j
from neo4j import GraphDatabase
from daoNeo4j import daoNeo4j

class daoGrafo(daoNeo4j):

    def __init__(self):
        super()

    def find(self, match = "", where = "", ret = ""):
        m = " MATCH " + match
        w = " WHERE " + where
        r = " RETURN " + ret

        if match == "":
            m = ""
        if where == "":
            w = ""
        if ret == "":
            r = ""

        query = m + w + r

        return self._session.run(query)

    def insert(self, create):
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