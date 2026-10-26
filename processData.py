import ast
import pandas as pd


class ProcessData:

    def __init__(self):
        self.ratings_dict = {}
        self.movies_dict = {}
        self.credits_dict = {}
        self.links_dict = {}
        self.parse_files()

    # Read all four CSV files
    def parse_files(self):
        self.df_movies = pd.read_csv(
            "archive/movies_metadata.csv", low_memory=False
        )
        self.df_links = pd.read_csv(
            "archive/links.csv", low_memory=False
        )
        self.df_ratings = pd.read_csv(
            "archive/ratings_small.csv", low_memory=False
        )
        self.df_credits = pd.read_csv(
            "archive/credits.csv", low_memory=False
        )

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

    # Store selected columns in dictionaries
    def set_columns(self, target, df, include=None):
        for column in include or []:
            target[column] = df[column]

    # Clean Movies
    def refine_movies_data(self):
        print("\n--- CLEANING MOVIES ---")
        print("Rows before:", len(self.df_movies))

        # Remove movies with invalid id
        self.df_movies["id"] = pd.to_numeric(
            self.df_movies["id"], errors="coerce"
        )
        self.df_movies = self.df_movies.dropna(subset=["id"])

        # Remove duplicate movies, keeping highest vote count. Or do different?
        self.df_movies["vote_count"] = pd.to_numeric(
            self.df_movies["vote_count"], errors="coerce"
        )

        self.df_movies = (
            self.df_movies.sort_values(
                "vote_count", ascending=False, kind="stable"
            )
            .drop_duplicates(subset="id", keep="first")
            .reset_index(drop=True)
        )

        print("Rows after:", len(self.df_movies))

    # Handle missing values in Movies
    def handle_missing_values(self):

        # Set title to original_title if title is missing
        self.df_movies["title"] = self.df_movies["title"].fillna(
            self.df_movies["original_title"]
        )

        # Set missing text to an empty string
        text_columns = ["overview", "tagline"]

        for col in text_columns:
            self.df_movies[col] = self.df_movies[col].fillna("")

        # Replace missing arrays with empty arrays as strings
        array_columns = [
            "genres",
            "production_companies",
            "production_countries"
        ]

        for col in array_columns:
            self.df_movies[col] = self.df_movies[col].fillna("[]")
            
        # Convert numeric fields
        numeric_columns = [
            "revenue",
            "runtime",
            "vote_average",
            "vote_count"
        ]

        for col in numeric_columns:
            self.df_movies[col] = pd.to_numeric(
                self.df_movies[col], errors="coerce"
            )

        # Treat runtime = 0 as missing
        self.df_movies.loc[
            self.df_movies["runtime"] == 0, "runtime"
        ] = float("nan")

        # Convert release dates to datetime
        self.df_movies["release_date"] = pd.to_datetime(
            self.df_movies["release_date"], errors="coerce"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Clean Links
    def refine_links_data(self):
        print("\n--- CLEANING LINKS ---")
        print("Rows before:", len(self.df_links))

        # Convert IDs to numeric values
        for col in ["movieId", "tmdbId"]:
            self.df_links[col] = pd.to_numeric(
                self.df_links[col], errors="coerce"
            )

        # Remove rows without valid movieId
        self.df_links = self.df_links.dropna(subset=["movieId"])

        # Remove completely identical rows
        self.df_links = self.df_links.drop_duplicates()

        # Keep movieId unique
        self.df_links = (
            self.df_links.drop_duplicates(
                subset="movieId", keep="first"
            )
            .reset_index(drop=True)
        )

    # Remove incorrect Links mappings
    def remove_incorrect_links(self):

        self.df_links["imdbId"] = pd.to_numeric(
            self.df_links["imdbId"], errors="coerce"
        )

        movies_imdb = pd.to_numeric(
            self.df_movies["imdb_id"]
            .astype("string")
            .str.replace("tt", "", regex=False),
            errors="coerce"
        )

        # Create lookup between Movies id and imdb_id
        imdb_lookup = dict(
            zip(self.df_movies["id"], movies_imdb)
        )

        # Find duplicated tmdbIds
        duplicates = (
            self.df_links["tmdbId"].notna()
            & self.df_links["tmdbId"].duplicated(keep=False)
        )

        # Compare IMDb IDs
        expected_imdb = self.df_links["tmdbId"].map(imdb_lookup)

        incorrect = (
            duplicates
            & expected_imdb.notna()
            & self.df_links["imdbId"].notna()
            & (
                self.df_links["imdbId"].fillna(-1)
                != expected_imdb.fillna(-1)
            )
        )

        print("Incorrect links removed:", incorrect.sum())

        self.df_links = self.df_links.loc[
            ~incorrect
        ].reset_index(drop=True)

        print("Rows after:", len(self.df_links))

    # Clean Ratings
    def refine_ratings_data(self):
        print("\n--- CLEANING RATINGS ---")
        print("Rows before:", len(self.df_ratings))

        for col in ["userId", "movieId", "rating"]:
            self.df_ratings[col] = pd.to_numeric(
                self.df_ratings[col], errors="coerce"
            )

        self.df_ratings = self.df_ratings.dropna(
            subset=["userId", "movieId", "rating"]
        )

        valid_rating = (
            self.df_ratings["rating"].between(0.5, 5.0)
            & (self.df_ratings["rating"] * 2 % 1 == 0)
        )

        self.df_ratings = self.df_ratings[valid_rating].copy()

        self.df_ratings = self.df_ratings.drop_duplicates()

        self.df_ratings["timestamp"] = pd.to_datetime(
            self.df_ratings["timestamp"],
            unit="s",
            errors="coerce"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")

        self.df_ratings = self.df_ratings.reset_index(drop=True)

        print("Rows after:", len(self.df_ratings))

    # Clean Credits
    def refine_credits_data(self):
        print("\n--- CLEANING CREDITS ---")
        print("Rows before:", len(self.df_credits))

        self.df_credits["id"] = pd.to_numeric(
            self.df_credits["id"], errors="coerce"
        )

        self.df_credits = self.df_credits.dropna(subset=["id"])

        self.df_credits = self.df_credits.drop_duplicates()

        self.df_credits = self.df_credits.drop_duplicates(
            subset="id", keep="first"
        )

        self.df_credits = self.df_credits.reset_index(drop=True)

        print("Rows after:", len(self.df_credits))
        
    # Remove duplicate actors within each movie
    def remove_duplicate_actors(self, cast):
        seen = set()
        unique_cast = []

        for actor in cast:
            actor_id = actor.get("id")

            if actor_id in seen:
                continue

            seen.add(actor_id)
            unique_cast.append(actor)

        return unique_cast

    # Add movie_id to Movies using Links
    def add_movie_id(self):

        # Exclude links without a valid tmdbId
        valid_links = self.df_links.dropna(subset=["tmdbId"])

        # Match Movies id with Links tmdbId
        movie_id_lookup = valid_links.set_index("tmdbId")["movieId"]

        self.df_movies["movie_id"] = self.df_movies["id"].map(
            movie_id_lookup
        )

        print(
            "Missing movie_id:",
            self.df_movies["movie_id"].isna().sum()
        )
        print(
            "Duplicate movie_id:",
            self.df_movies["movie_id"].duplicated().sum()
        )

    # Add decade
    def add_decade(self):
        release_dates = pd.to_datetime(
            self.df_movies["release_date"], errors="coerce"
        )

        decade = release_dates.dt.year // 10 * 10
        self.df_movies["decade"] = [int(d) if pd.notna(d) else None for d in decade] # doesnt convert None values to int
          
    # Add cast
    def add_cast(self):
        cast_fields = ["id", "name", "gender", "order"]

        cast_lookup = dict(zip(
            self.df_credits["id"],
            self.df_credits["cast"].apply(
                lambda value: self.remove_duplicate_actors(
                    self.parse_list(value, fields=cast_fields)
                )
            )
        ))

        # Map movie ids from credits and movies
        self.df_movies["cast"] = self.df_movies["id"].map(
            lambda movie_id: cast_lookup.get(movie_id, [])
        )

    # Add crew where the job is Director
    def add_crew(self):
        crew_fields = ["id", "name", "job"]

        crew_lookup = dict(zip(
            self.df_credits["id"],
            self.df_credits["crew"].apply(
                lambda value: [
                    member
                    for member in self.parse_list(value, crew_fields)
                    if member["job"] == "Director"
                ]
            )
        ))

        # Map movie ids from credits and movies
        self.df_movies["crew"] = self.df_movies["id"].map(
            lambda movie_id: crew_lookup.get(movie_id, [])
        )
    
    # Helper function to convert genres from strings to objects 
    def add_genres_object(self):
        genres_fields = ["id", "name"]

        self.df_movies["genres"] = self.df_movies["genres"].apply(
            lambda value: self.parse_list(value, genres_fields)
        )
    
    # Helper function to convert production companies from strings to objects 
    def add_prod_companies_object(self):
        production_comp_fields = ["name", "id"]

        self.df_movies["production_companies"] = self.df_movies["production_companies"].apply(
            lambda value: self.parse_list(value, production_comp_fields)
        )
    
    # Helper function to convert production countries from strings to objects 
    def add_prod_countries_object(self):
        countries_fields = ["iso_3166_1", "name"]

        self.df_movies["production_countries"] = (
            self.df_movies["production_countries"].apply(
                lambda value: [
                    {
                        "country_code": country["iso_3166_1"],
                        "name": country["name"]
                    }
                    for country in self.parse_list(value, countries_fields)
                ]
                if pd.notna(value) else []
            )
        )
    
    # Helper function to convert production companies from strings to objects 
    def add_belongs_to_coll_object(self):
        collection_fields = ["id", "name", "poster_path", "backdrop_path"]

        self.df_movies["belongs_to_collection"] = (
            self.df_movies["belongs_to_collection"].apply(
                lambda value: {
                    key: parsed[key]
                    for key in collection_fields
                    if key in parsed
                }
                if isinstance(value, str)
                and isinstance((parsed := ast.literal_eval(value)), dict)
                else None
            )
        )
    

    # Run preprocessing
    def run(self):

        # 1. Clean Movies
        self.refine_movies_data()
        self.handle_missing_values()

        # 2. Clean Links
        self.refine_links_data()
        self.remove_incorrect_links()

        # 3. Add movie_id to Movies
        self.add_movie_id()

        # 4. Clean Ratings
        self.refine_ratings_data()

        # 5. Clean Credits
        self.refine_credits_data()

        # 6. Add decade, cast and crew to Movies
        self.add_decade()
        self.add_cast()
        self.add_crew()

        # 7. Add genre, proudction_company and production_countries objects to movies collection
        self.add_genres_object()
        self.add_prod_companies_object()
        self.add_prod_countries_object()
        self.add_belongs_to_coll_object()

        # 8. Store selected columns in dictionaries

        self.set_columns(
            self.links_dict,
            self.df_links,
            ["movieId", "tmdbId"]
        )

        self.set_columns(
            self.credits_dict,
            self.df_credits,
            ["id", "cast", "crew"]
        )

        self.set_columns(
            self.ratings_dict,
            self.df_ratings,
            ["userId", "movieId", "rating"]
        )

        self.set_columns(
            self.movies_dict,
            self.df_movies,
            [
                "id",
                "movie_id",
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
            ]
        )


    def get_movies_dict(self):
        return self.movies_dict

    def get_ratings_dict(self):
        return self.ratings_dict

def main():
    data = ProcessData()
    data.run()


if __name__ == "__main__":
    main()
