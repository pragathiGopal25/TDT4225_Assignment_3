class Queries:
    def __init__(self):
        self.connection = DbConnector()
        self.cursor = self.connection.cursor
        
    def question_1(self):
        query = """ """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(f"""Question 1: \n\n{tabulate(rows, headers=self.cursor.column_names)}\n""")
        
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