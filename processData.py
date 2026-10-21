import pandas as pd
class ProcessData:

    def __init__(self, filename):
        self.df = pd.read_csv(filename, low_memory=False)

    def refine_movies_data(self):
        print("\n--- CLEANING MOVIES ---")
        print("Rows before:", len(self.df))

        # Remove movies with invalid id
        self.df["id"] = pd.to_numeric(
            self.df["id"], errors="coerce"
        )
        self.df = self.df.dropna(subset=["id"])

        # Remove duplicate movies, keeping highest vote count
        self.df["vote_count"] = pd.to_numeric(
            self.df["vote_count"], errors="coerce"
        )

        self.df = (
            self.df.sort_values(
                "vote_count", ascending=False, kind="stable"
            )
            .drop_duplicates(subset="id", keep="first")
            .reset_index(drop=True)
        )

        print("Rows after:", len(self.df))

    def handle_missing_values(self):

        # Set title to original_title if title is missing
        self.df["title"] = self.df["title"].fillna(
            self.df["original_title"]
        )

        # Set empty text to an empty string
        text_columns = ["overview", "tagline"]

        for col in text_columns:
            self.df[col] = self.df[col].fillna("")

        # Replace missing arrays with empty arrays (as strings since the valid arrays are strings)
        # Make it easier to work with arrays in MongoDB, shows that no genres or companies are registered for the movie
        array_columns = [
            "genres",
            "production_companies",
            "production_countries"
        ]

        for col in array_columns:
            self.df[col] = self.df[col].fillna("[]")

        # Convert numeric fields
        numeric_columns = [
            "revenue",
            "runtime",
            "vote_average",
            "vote_count"
        ]

        for col in numeric_columns:
            self.df[col] = pd.to_numeric(
                self.df[col], errors="coerce"
            )

        # Treat runtime = 0 as missing so it doesn't affect calculations
        self.df.loc[
            self.df["runtime"] == 0, "runtime"
        ] = float("nan")

        # Convert release dates to datetime
        self.df["release_date"] = pd.to_datetime(
            self.df["release_date"], errors="coerce"
        )

    def refine_links_data(self):
        print("\n--- CLEANING LINKS ---")
        print("Rows before:", len(self.df))

        # Convert IDs to numeric values
        for col in ["movieId", "tmdbId"]:
            self.df[col] = pd.to_numeric(
                self.df[col], errors="coerce"
            )

        # Remove rows without valid movieId
        self.df = self.df.dropna(subset=["movieId"])

        # Remove completely identical rows
        self.df = self.df.drop_duplicates()

        # Keep movieId unique
        self.df = (
            self.df.drop_duplicates(subset="movieId", keep="first")
            .reset_index(drop=True)
        )

    def remove_incorrect_links(self, movies_df):

        # Convert IMDb IDs to comparable numeric values
        # Since some duplicates have different imdbId
        self.df["imdbId"] = pd.to_numeric(
            self.df["imdbId"], errors="coerce"
        )

        movies_imdb = pd.to_numeric(
            movies_df["imdb_id"]
            .astype("string")
            .str.replace("tt", "", regex=False),
            errors="coerce"
        )

        # Create lookup between TMDB ID and IMDb ID
        imdb_lookup = dict(zip(movies_df["id"], movies_imdb))

        # Find duplicated tmdbIds
        duplicates = (
            self.df["tmdbId"].notna()
            & self.df["tmdbId"].duplicated(keep=False)
        )

        # Check if IMDb IDs match
        expected_imdb = self.df["tmdbId"].map(imdb_lookup)

        incorrect = (
            duplicates
            & expected_imdb.notna()
            & self.df["imdbId"].notna()
            & (self.df["imdbId"].fillna(-1) != expected_imdb.fillna(-1))
        )

        print("Incorrect links removed:", incorrect.sum())

        self.df = self.df.loc[~incorrect].reset_index(drop=True)

        print("Rows after:", len(self.df))

    def refine_ratings_data(self):
        print("\n--- CLEANING RATINGS ---")
        print("Rows before:", len(self.df))

        # Convert identifiers and rating to numeric values
        for col in ["userId", "movieId", "rating"]:
            self.df[col] = pd.to_numeric(
                self.df[col], errors="coerce"
            )

        # Remove rows with invalid required values
        self.df = self.df.dropna(
            subset=["userId", "movieId", "rating"]
        )

        # Check rating range and increments
        valid_rating = (
            self.df["rating"].between(0.5, 5.0)
            & (self.df["rating"] * 2 % 1 == 0)
        )

        # Remove invalid ratings
        self.df = self.df[valid_rating].copy()

        # Remove completely identical rows only
        self.df = self.df.drop_duplicates()

        # Convert timestamp to datetime
        self.df["timestamp"] = pd.to_datetime(
            self.df["timestamp"],
            unit="s",
            errors="coerce"
        )

        self.df = self.df.reset_index(drop=True)

        print("Rows after:", len(self.df))
        
        
    def refine_credits_data(self):
        print("\n--- CLEANING CREDITS ---")
        print("Rows before:", len(self.df))

        # Convert id to numeric
        self.df["id"] = pd.to_numeric(
            self.df["id"], errors="coerce"
        )

        # Remove rows with invalid id
        self.df = self.df.dropna(subset=["id"])

        # Remove completely identical rows
        self.df = self.df.drop_duplicates()
        
        # Remove duplicate movie IDs (same cast and crew, ignoring order)
        self.df = self.df.drop_duplicates(
            subset="id", keep="first"
        )

        self.df = self.df.reset_index(drop=True)

        print("Rows after:", len(self.df))


def main():

    # Movies
    movies = ProcessData("archive/movies_metadata.csv")
    movies.refine_movies_data()
    movies.handle_missing_values()

    # Links
    links = ProcessData("archive/links.csv")
    links.refine_links_data()
    links.remove_incorrect_links(movies.df)

    # Ratings
    ratings = ProcessData("archive/ratings_small.csv")
    ratings.refine_ratings_data()
    
    # Credits
    credits = ProcessData("archive/credits.csv")
    credits.refine_credits_data()


if __name__ == "__main__":
    main()