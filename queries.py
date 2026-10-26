
from DbConnector import DbConnector


class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def question_1(self):
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 1: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")

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
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 3: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")

        
    def question_4a(self):
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 4a: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")
        
    def question_4b(self):
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 4b: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")


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
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 6: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")
    
    def question_7(self):
        query =   """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 7: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")

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
        query =  """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 9: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")

    def question_10(self):
        query =  """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 10: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")

if __name__ == "__main__":
    program = Queries()

    # program.question_1()
    # program.question_2()
    # program.question_3()
    # program.question_4a()
    # program.question_4b()
    # program.question_5()
    # program.question_6() 
    # program.question_7()
    # program.question_8()
    # program.question_9()
    # program.question_10()