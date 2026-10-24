from DbConnector import DbConnector

class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.db = self.connection.db

    def question_1(self):
        query = """ """
        self.db.execute(query)
        rows = self.db.fetchall()
        print(f"""Question 1: \n\n{tabulate(rows, headers=self.db.column_names)}\n""")
        
    def question_2(self):
        query = """ """
        self.db.execute(query)
        rows = self.db.fetchall()
        print(f"""Question 2: \n\n{tabulate(rows, headers=self.db.column_names)}\n""")
    
    def question_3(self):
        print("\nQuestion 3: \n")
        pipeline = [
            {"$unwind": "$cast"},
            {"$unwind": "$genres"},
            {
                "$group": {
                    "_id": "$cast.id",
                    "name": {"$first": "$cast.name"},
                    "genres": {"$addToSet": "$genres.name"},
                    "movies": {"$addToSet": "$id"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "credited_movies": {"$size": "$movies"},
                    "distinct_genres": {"$size": "$genres"},
                    "example_5": {"$slice": ["$genres", 5]}
                }
            },
            {"$match": {"credited_movies": {"$gte": 10}}},
            {"$sort": {"distinct_genres": -1}},
            {"$limit": 10}
        ]

        rows = list(self.db.Movies.aggregate(pipeline))

        for row in rows:
            print(row)
    
    def question_4(self):

        print("\nQuestion 4: \n")
        pipeline = [
            {
                "$match": {
                    "belongs_to_collection.name": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$belongs_to_collection.id",
                    "name": {"$first": "$belongs_to_collection.name"},
                    "movies": {"$addToSet": "$movie_id"},
                    "total_revenue": {"$sum": "$revenue"},
                    "median_vote_average": {
                        "$median": {
                            "input": "$vote_average",
                            "method": "approximate"
                        }
                    },
                    "earliest_release": {"$min": "$release_date"},
                    "latest_release": {"$max": "$release_date"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "movie_count": {"$size": "$movies"},
                    "total_revenue": 1,
                    "median_vote_average": 1,
                    "earliest_release": 1,
                    "latest_release": 1
                }
            },
            {"$match": {"movie_count": {"$gte": 3}}},
            {"$sort": {"total_revenue": -1}},
            {"$limit": 10}
        ]

        rows = list(self.db.Movies.aggregate(pipeline))

        for row in rows:
            print(row)
        
    def question_5(self):
        query = """ """
        self.db.execute(query)
        rows = self.db.fetchall()
        print(f"""Question 5: \n\n{tabulate(rows, headers=self.db.column_names)}\n""")
    
    def question_6(self):
        query = """ """
        self.db.execute(query)
        rows = self.db.fetchall()
        print(f"""Question 6: \n\n{tabulate(rows, headers=self.db.column_names)}\n""")
    
    def question_7(self):
        query =   """ """
        self.db.execute(query)
        rows = self.db.fetchall()
        print(f"""Question 7: \n\n{tabulate(rows, headers=self.db.column_names)}\n""")

    def question_8(self):
        query =  """ """
        self.db.execute(query)
        rows = self.db.fetchall()
        print(f"""Question 8: \n\n {tabulate(rows, headers=self.db.column_names)}\n""")
    
    def question_9(self):
        print("\nQuestion 9: \n")
        pipeline = [
            {
               "$match": {
                    "original_language": {"$ne": "en"},
                    "$or": [
                        {"production_countries.country_code": "US"}
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$original_language",
                    "movie_count": {"$sum": 1},
                    "example_title":{"$first": "$title"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "language": "$_id",
                    "movie_count": 1,
                    "example_title": 1
                }
            },
            {"$sort": {"movie_count": -1}},
            {"$limit": 10}
        ]

        rows = list(self.db.Movies.aggregate(pipeline))

        for row in rows:
            print(row)

    #TODO
    # 10.For each user, what is their ratings count, population variance of ratings, and
    # number of distinct genres rated?
    # List the top 10 most genre-diverse users, and separately the top 10
    # highest-variance users (only users with ≥ 20 ratings).
    def question_10(self):
        # Creating an index so it is easier to iterate through movie_ids.
        self.db.Movies.create_index("movie_id")

        print("\nQuestion 10: \n")

        print("Top 10 most genre-diverse users. \n")
        pipeline_base= [
            {
                "$lookup": {
                    "from": "Movies",
                    "localField": "movieId",
                    "foreignField": "movie_id",
                    "as": "movies"
                }
            },
            {"$unwind": "$movies"},
            {"$unwind": "$movies.genres"},

            {
                "$group": {
                    "_id": "$userId",
                    "genres": {"$addToSet": "$movies.genres.name"},
                    "rated": {"$addToSet": {"id": "$_id", "rating": "$rating"}},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "user_id": "$_id",
                    "distinct_genres": {"$size": "$genres"},
                    "ratings_count": {"$size": "$rated"},
                    "population_variance": {
                        "$pow": [{"$stdDevPop": "$rated.rating"}, 2]
                    },
                }
            },
        ]

        pipeline_first = pipeline_base + [
            {"$sort": {"distinct_genres": -1}},  
            {"$limit": 10},
        ]

        rows = list(self.db.Ratings.aggregate(pipeline_first))

        for row in rows:
            print(row)


        print("\nTop 10 highest-variance users (only users with ≥ 20 ratings). \n")
        
        pipeline_second = pipeline_base + [
            {"$match":{"ratings_count": {"$gte": 20}}},
            {"$sort": {"population_variance": -1}},
            {"$limit": 10}
        ]

        rows = list(self.db.Ratings.aggregate(pipeline_second))

        for row in rows:
            print(row)

if __name__ == "__main__":
    program = Queries()

    # program.question_1()
    # program.question_2()
    program.question_3()
    program.question_4()
    # program.question_5()
    # program.question_6() 
    # program.question_7()
    # program.question_8()
    program.question_9()
    program.question_10()