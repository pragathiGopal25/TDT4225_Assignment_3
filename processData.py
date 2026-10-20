import pandas as pd
class ProcessData:

    def __init__(self, filename):
        self.df = pd.read_csv(filename, low_memory=False)

    def refine_data(self):
        print("Rows before cleaning:", len(self.df))

        # Remove movies with invalid id
        self.df["id"] = pd.to_numeric(
            self.df["id"], errors="coerce"
        )

        print("Invalid IDs:", self.df["id"].isna().sum())
        self.df = self.df.dropna(subset=["id"])

        # Remove duplicate movies, here keeping highest vote count? Or should we do it different?
        print("Duplicate IDs:", self.df["id"].duplicated().sum())

        self.df["vote_count"] = pd.to_numeric(
            self.df["vote_count"], errors="coerce"
        )

        self.df = self.df.sort_values(
            "vote_count", ascending=False, kind="stable"
        )

        self.df = self.df.drop_duplicates(
            subset="id", keep="first"
        )

        self.df = self.df.reset_index(drop=True)

        print("Rows after cleaning:", len(self.df))

    def handle_missing_values(self):

        # Set title to a_title if title is missing
        self.df["title"] = self.df["title"].fillna(
            self.df["a_title"]
        )

        # Set emty text to an emty string
        text_columns = ["overview", "tagline"]

        for col in text_columns:
            self.df[col] = self.df[col].fillna("")

        # Replace missing arrays with empty arrays (as strings since the valid arrays are string)
        # Make it easier to work with arrays in MongoDB, shows that no genres or companies is registrered for the movie
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

        # Treat runtime = 0 as missing so it dont mess up calculations
        self.df.loc[
            self.df["runtime"] == 0, "runtime"
        ] = float("nan")

        # Convert release dates to datetime
        self.df["release_date"] = pd.to_datetime(
            self.df["release_date"], errors="coerce"
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
        print(self.df[required_columns].isna().sum())

        print("\nTotal movies:", len(self.df))


def main():
    p = ProcessData("archive/movies_metadata.csv")

    p.refine_data()
    p.handle_missing_values()


if __name__ == "__main__":
    main()
