import neo4j
from neo4j import GraphDatabase

class daoNeo4j:

    _instance = None

    def __new__(cls):
        if cls._instance is None:

            cls._instance = super(daoNeo4j, cls).__new__(cls)
            cls._driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))
            cls._session = cls._driver.session()

        return cls._instance

    def close(self):
        self._driver.close()
        self._instance = None