from tabulate import tabulate
from DbConnector import DbConnector


class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.cursor = self.connection.cursor
        
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
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 2: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")
        
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
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 5: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")
    
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
        query =  """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 8: \n\n {tabulate(rows, headers=self.cursor.column_names)}\n""")
    
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

    program.question_1()
    # program.question_2()
    # program.question_3()
    # program.question_4a()
    # program.question_4b()
    # program.question_5()
    program.question_6()
    program.question_7()
    # program.question_8()
    # program.question_9()
    # program.question_10()