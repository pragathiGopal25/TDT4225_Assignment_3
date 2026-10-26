import json
from processData import ProcessData
from DbConnector import DbConnector

class LoadData:
    
    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def create_coll(self, collection_name):
        if collection_name in self.db.list_collection_names():
            self.db[collection_name].drop()
        collection = self.db.create_collection(collection_name)    
        print('Created collection: ', collection)

    def insert_documents(self, collection_name, docs):
        collection = self.db[collection_name]
        collection.insert_many(docs)
    
    def show_coll(self):
        collections = self.client['movies_db'].list_collection_names()
        print(collections)

def main():
    p = ProcessData()
    p.run()

    movies_dict = p.get_movies_dict()
    ratings_dict = p.get_ratings_dict()

    movies_docs = []
    ratings_docs = []

    # Creating movie JSON document
    # Creating movie documents
    for movie_values in zip(*movies_dict.values()):
        movie = dict(zip(movies_dict.keys(), movie_values))
        movies_docs.append(movie)

    # Creating rating documents
    for rating_values in zip(*ratings_dict.values()):
        rating = dict(zip(ratings_dict.keys(), rating_values))
        ratings_docs.append(rating)


    program = None
    try:
        # Creating movies collection
        program = LoadData()
        program.create_coll(collection_name="Movies")
        program.show_coll()
        program.insert_documents(collection_name="Movies", docs=movies_docs)
        
        # Creating ratings collection
        program.create_coll(collection_name="Ratings")
        program.show_coll()
        program.insert_documents(collection_name="Ratings", docs=ratings_docs)
        
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()



if __name__ == "__main__":
    main()