from tabulate import tabulate

from DbConnector import DbConnector


class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.db = self.connection.db
        
    def question_1(self):
        pipeline = [
            {"$match": {"revenue": {"$gt": 0}}},
            {"$unwind": "$crew"},
            {"$group": {
                "_id": "$crew.id",
                "director": {"$first": "$crew.name"},
                "movie_count": {"$sum": 1},
                "median_revenue": {"$median": {"input": "$revenue", "method": "approximate"}},
                "mean_vote_average": {"$avg": "$vote_average"},
            }},
            {"$match": {"movie_count": {"$gte": 5}}},
            {"$sort": {"median_revenue": -1}},
            {"$limit": 10},
            {"$project": {
                "_id": 0,
                "director": 1,
                "movie_count": 1,
                "median_revenue": 1,
                "mean_vote_average": {"$round": ["$mean_vote_average", 2]},
            }},
        ]
        rows = list(self.db["Movies"].aggregate(pipeline))
        print(f"""Question 1: \n\n{tabulate(rows, headers="keys", floatfmt=",.2f")}\n""")
        
    def question_2(self):
        pipeline = [
            {
                "$match": {
                    "cast.1": {"$exists": True}
                }
            },
            {
                "$set": {"full_cast": "$cast"}
            },
            {
                "$unwind": {
                    "path": "$cast",
                    "includeArrayIndex": "cast_index"
                }
            },
            {
                "$project": {
                    "vote_average": 1,
                    "actor1": "$cast",
                    "later_cast": {
                        "$slice": [
                            "$full_cast",
                            {"$add": ["$cast_index", 1]},
                            {"$size": "$full_cast"}
                        ]
                    }
                }
            },
            {
                "$unwind": "$later_cast"
            },
            {
                "$match": {
                    "actor1.id": {"$exists": True, "$ne": None},
                    "later_cast.id": {"$exists": True, "$ne": None},
                    "$expr": {
                        "$ne": [
                            "$actor1.id",
                            "$later_cast.id"
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "actor1": {
                            "$min": [
                                "$actor1.id",
                                "$later_cast.id"
                            ]
                        },
                        "actor2": {
                            "$max": [
                                "$actor1.id",
                                "$later_cast.id"
                            ]
                        }
                    },
                    "actor1_name": {
                        "$first": {
                            "$cond": [
                                {
                                    "$lte": [
                                        "$actor1.id",
                                        "$later_cast.id"
                                    ]
                                },
                                "$actor1.name",
                                "$later_cast.name"
                            ]
                        }
                    },
                    "actor2_name": {
                        "$first": {
                            "$cond": [
                                {
                                    "$lte": [
                                        "$actor1.id",
                                        "$later_cast.id"
                                    ]
                                },
                                "$later_cast.name",
                                "$actor1.name"
                            ]
                        }
                    },
                    "co_appearances": {"$sum": 1},
                    "average_vote": {"$avg": "$vote_average"}
                }
            },
            {
                "$match": {
                    "co_appearances": {"$gte": 3}
                }
            },
            {
                "$sort": {
                    "co_appearances": -1,
                    "_id.actor1": 1,
                    "_id.actor2": 1
                }
            }
        ]

        results = self.db["Movies"].aggregate(
            pipeline,
            allowDiskUse=True
        )

        print("Question 2:\n")

        for row in results:
            print(row)
            
   
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
        pipeline = [
            {
                "$match": {
                    "decade": {
                        "$type": "number",
                        "$gte": 0 #evt. endre loadData til å kovertere manglende decade til None i loadData
                    },
                    "genres.0": {"$exists": True}
                }
            },
            {
                "$group": {
                    "_id": {
                        "decade": "$decade",
                        "primary_genre": {
                            "$arrayElemAt": ["$genres.name", 0]
                        }
                    },
                    "median_runtime": {
                        "$median": {
                            "input": {
                                "$cond": [
                                    {"$gt": ["$runtime", 0]}, #sjekker om det er et gyldig postivit tall, ikke bare 0, men er det vits å gjøre runtime om til NaN da i processData?
                                    "$runtime",
                                    None
                                ]
                            },
                            "method": "approximate"
                        }
                    },
                    "movie_count": {"$sum": 1}
                }
            },
            {
                "$sort": {
                    "_id.decade": 1,
                    "median_runtime": -1
                }
            }
        ]

        results = self.db["Movies"].aggregate(pipeline + [{"$limit": 40}])

        print("Question 5:\n")
        for row in results:
            print(row)

    def question_6(self):
        pipeline = [
            {"$match": {"decade": {"$ne": float("nan")}, "cast": {"$ne": []}}},
            # movie top-5 billed cast
            {"$project": {
                "decade": 1,
                "known_cast": {"$filter": {
                    "input": {"$slice": [{"$sortArray": {"input": "$cast", "sortBy": {"order": 1}}}, 5]},
                    "cond": {"$in": ["$$this.gender", [1, 2]]},
                }},
            }},
            {"$match": {"known_cast": {"$ne": []}}},
            {"$project": {
                "decade": 1,
                "female_proportion": {"$divide": [
                    {"$size": {"$filter": {"input": "$known_cast", "cond": {"$eq": ["$$this.gender", 1]}}}},
                    {"$size": "$known_cast"},
                ]},
            }},
            {"$group": {
                "_id": "$decade",
                "avg_female_proportion": {"$avg": "$female_proportion"},
                "movie_count": {"$sum": 1},
            }},
            {"$sort": {"avg_female_proportion": -1}},
            {"$project": {
                "_id": 0,
                "decade": {"$concat": [{"$toString": {"$toInt": "$_id"}}, "s"]},
                "avg_female_proportion": {"$round": ["$avg_female_proportion", 3]},
                "movie_count": 1,
            }},
        ]
        rows = list(self.db["Movies"].aggregate(pipeline))
        print(f"""Question 6: \n\n{tabulate(rows, headers="keys")}\n""")

    def question_7(self):
        self.db["Movies"].create_index([("overview", "text"), ("tagline", "text")])
        pipeline = [
            {"$match": {
                "$text": {"$search": "noir"},
                "vote_count": {"$gte": 50},
            }},
            {"$sort": {"vote_average": -1, "vote_count": -1}},
            {"$limit": 20},
            {"$project": {
                "_id": 0,
                "title": 1,
                "year": {"$substrCP": ["$release_date", 0, 4]},
                "vote_average": 1,
                "vote_count": {"$toInt": "$vote_count"},
            }},
        ]
        rows = list(self.db["Movies"].aggregate(pipeline))
        print(f"""Question 7: \n\n{tabulate(rows, headers="keys")}\n""")

    def question_8(self):
        pipeline = [
            {
                "$match": {
                    "vote_count": {"$gte": 100},
                    "cast.0": {"$exists": True},
                    "crew": {
                        "$elemMatch": {"job": "Director"}
                    }
                }
            },
            {
                "$project": {
                    "vote_average": 1,
                    "revenue": 1,
                    "cast": 1,
                    "directors": {
                        "$filter": {
                            "input": "$crew",
                            "as": "person",
                            "cond": {
                                "$eq": ["$$person.job", "Director"]
                            }
                        }
                    }
                }
            },
            {
                "$unwind": "$directors"
            },
            {
                "$unwind": "$cast"
            },
            {
                "$group": {
                    "_id": {
                        "director": "$directors.id",
                        "actor": "$cast.id"
                    },
                    "director_name": {
                        "$first": "$directors.name"
                    },
                    "actor_name": {
                        "$first": "$cast.name"
                    },
                    "films_count": {
                        "$sum": 1
                    },
                    "average_vote": {
                        "$avg": "$vote_average"
                    },
                    "mean_revenue": {
                        "$avg": "$revenue"
                    }
                }
            },
            {
                "$match": {
                    "films_count": {"$gte": 3}
                }
            },
            {
                "$sort": {
                    "average_vote": -1,
                    "films_count": -1,
                    "_id.director": 1,
                    "_id.actor": 1
                }
            },
            {
                "$limit": 20
            }
        ]

        results = self.db["Movies"].aggregate(
            pipeline,
            allowDiskUse=True
        )

        print("Question 8:\n")

        for row in results:
            print(row)
    
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