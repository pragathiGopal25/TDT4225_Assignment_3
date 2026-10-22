class LoadData:
    
    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor

    # TODO
    def create_coll(self, collection_name):
        collection = self.db.create_collection(collection_name)    
        print('Created collection: ', collection)

    #TODO
    def insert_documents(self, collection_name, docs):
        collection = self.db[collection_name]
        collection.insert_many(docs)
        
    #TODO 
    def drop_coll(self, collection_name):
        collection = self.db[collection_name]
        collection.drop() 

def main():
    p = ProcessData()
    p.run()

    l = LoadData()

if __name__ == "__main__":
    main()