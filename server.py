from pymongo import MongoClient


class Db:
    def __init__(self, host, port, dbname):
        try:
            self.mongodb_host = host
            self.mongodb_port = port
            self.db_name = dbname
            self.connection = MongoClient(self.mongodb_host, self.mongodb_port)[self.db_name]
        except Exception as e:
            print(e)

    def getCollectionsNames(self):
        """ Returns all collections available in the database """
        return self.connection.collection_names(include_system_collections=False)

    def build_collection(self, collection_name):
        """ Access a particular collection given its name """
        try:
            return self.connection[collection_name]
        except Exception as e:
            print(e)

    def initialize_collections(self):
        """ Function to initialize mongodb collections. Return a dictionary w/ each collection. """
        COLLECTIONS = self.getCollectionsNames()

        try:
            collections_dict = {}
            for collection in COLLECTIONS:
                collections_dict[collection] = self.build_collection(collection)
            return collections_dict
        except Exception as e:
            print(e)

