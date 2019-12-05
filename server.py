from pymongo import MongoClient


class Db():
    def __init__(self, host, port, dbname):
        try:
            self.mongodb_host = host
            self.mongodb_port = port
            self.db_name = dbname
            self.connection = MongoClient(self.mongodb_host, self.mongodb_port)[self.db_name]
        except Exception as e:
            print(e)

    def build_collection(self, collection_name):
        try:
            return self.connection[collection_name]
        except Exception as e:
            print(e)