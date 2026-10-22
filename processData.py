import ast
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

    # Parse strings to lists of dicts (used in cast and crew)
    def parse_list(self, value, fields):
        try:
            items = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []

        if not isinstance(items, list):
            return []

        return [
            {field: item.get(field) for field in fields}
            for item in items
            if isinstance(item, dict)
        ]

    def set_columns(self, target, df, include=None):
        for column in include or []: 
            target[column] = df[column]

    def refine_movie_data(self, df):
        print("Rows before cleaning:", len(df))

        # Remove movies with invalid id
        df["id"] = pd.to_numeric(
            df["id"], errors="coerce"
        )

        print("Invalid IDs:", df["id"].isna().sum())
        df = df.dropna(subset=["id"])

        # Remove duplicate movies, here keeping highest vote count? Or should we do it different?
        print("Duplicate IDs:", df["id"].duplicated().sum())

        df["vote_count"] = pd.to_numeric(
            df["vote_count"], errors="coerce"
        )

        df = df.sort_values(
            "vote_count", ascending=False, kind="stable"
        )

        df = df.drop_duplicates(
            subset="id", keep="first"
        )

        df = df.reset_index(drop=True)

        print("Rows after cleaning:", len(df))

    def handle_missing_values(self, df):

        # Set title to a_title if title is missing
        df["title"] = df["title"].fillna(
            df["a_title"]
        )

        # Set emty text to an emty string
        text_columns = ["overview", "tagline"]

        for col in text_columns:
            df[col] = df[col].fillna("")

        # Replace missing arrays with empty arrays (as strings since the valid arrays are string)
        # Make it easier to work with arrays in MongoDB, shows that no genres or companies is registrered for the movie
        array_columns = [
            "genres",
            "production_companies",
            "production_countries"
        ]

        for col in array_columns:
            df[col] = df[col].fillna("[]")

        # Convert numeric fields
        numeric_columns = [
            "revenue",
            "runtime",
            "vote_average",
            "vote_count"
        ]

        for col in numeric_columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            )

        # Treat runtime = 0 as missing so it dont mess up calculations
        df.loc[
            df["runtime"] == 0, "runtime"
        ] = float("nan")

        # Convert release dates to datetime
        df["release_date"] = pd.to_datetime(
            df["release_date"], errors="coerce"
        )

        # Summary of remaining missing values
        required_columns = [
            "id",
            "title",
            "release_date",
            "revenue",
            "runtime",
            "vote_average",
            "vote_count",
            "original_language",
            "overview",
            "tagline",
            "genres",
            "production_companies",
            "production_countries",
            "belongs_to_collection"
        ]

        print("\nMissing values after cleaning:")
        print(df[required_columns].isna().sum())

        print("\nTotal movies:", len(df))

    def add_decade(self, df):
        df["decade"] = (
            df["release_date"].dt.year // 10 * 10
        ).astype("Int64")

    def add_cast(self, movies_df, credits_df):
        cast_fields = ["id", "name", "gender", "order"]

        cast_lookup = dict(zip(
            credits_df["id"],
            credits_df["cast"].apply(self.parse_list, fields=cast_fields)
        ))

        # Map movie ids from credits and movies
        movies_df["cast"] = movies_df["id"].map(
            lambda movie_id: cast_lookup.get(movie_id, [])
        )

    def add_crew(self, movies_df, credits_df):
        crew_fields = ["id", "name", "job"]

        crew_lookup = dict(zip(
            credits_df["id"],
            credits_df["crew"].apply(
                lambda value: [
                    member for member in self.parse_list(value, crew_fields)
                    if member["job"] == "Director"
                ]
            )
        ))

        # Map movie ids from credits and movies
        movies_df["crew"] = movies_df["id"].map(
            lambda movie_id: crew_lookup.get(movie_id, [])
        )

    def run(self):
        #TODO:
            # Refine links, credits and ratings 
             
        # Links
        self.set_columns(self.links_dict, self.df_links, ["movieId", "tmdbId"])
        
        # Credits
        self.set_columns(self.credits_dict, self.df_credits, ["cast", "crew"])
        
        # Ratings
        self.set_columns(self.ratings_dict, self.df_ratings, ["userId", "movieId", "rating"])
        
        # Movies 
        # 1. refine data and handle missing values first:
        self.refine_movie_data(self.df_movies)
        self.handle_missing_values(self.df_movies)

        # 2. add decade, cast and crew
        self.add_decade(self.df_movies)
        self.add_cast(self.df_movies, self.df_credits)
        self.add_crew(self.df_movies, self.df_credits)

        self.set_columns(self.movies_dict, self.df_movies, [
            "id",
            "title",
            "release_date",
            "revenue",
            "runtime",
            "vote_average",
            "vote_count",
            "original_language",
            "overview",
            "tagline",
            "genres",
            "production_companies",
            "production_countries",
            "belongs_to_collection",
            "decade",
            "cast",
            "crew"
        ])

def main():
    p = ProcessData()
    p.run()

    pprint(p.links_dict)

if __name__ ==  "__main__":
    main()