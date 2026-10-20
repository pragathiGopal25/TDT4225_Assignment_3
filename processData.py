import pandas as pd
from pprint import pprint


class ProcessData:

    def __init__(self):
        self.ratings_dict = {}
        self.movies_dict = {}
        self.credits_dict = {}
        self.links_dict = {}
        self.parse_files()
    
    # Method to parse all files
    def parse_files(self):
        self.df_ratings = pd.read_csv("ratings.csv")
        self.df_credits = pd.read_csv("credits.csv")
        self.df_links = pd.read_csv("links.csv")
        self.df_movies = pd.read_csv("movies_metadata.csv", low_memory=False)

    def set_columns(self, target, df, include=None):
        for column in include or []: 
            target[column] = df[column]

    def run(self):
        # Links
        self.set_columns(self.links_dict, self.df_links, ["movieId", "tmdbId"])
        
        # Credits
        self.set_columns(self.credits_dict, self.df_credits, ["cast", "crew"])
        
        # Ratings
        self.set_columns(self.ratings_dict, self.df_ratings, ["userId", "movieId", "rating"])
        
        # Movies 
        self.set_columns(self.movies_dict, self.df_movies, ["belongs_to_collection", "genres", "id", 
        "original_language", "overview", "vote_count", "production_companies", "release_date", "revenue", "runtime", "tagline", "title", "vote_average"])


def main():
    p = ProcessData()
    p.run()

    pprint(p.links_dict)

if __name__ ==  "__main__":
    main()