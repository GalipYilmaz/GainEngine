import pandas as pd

class DataManager:
    def __init__(self, file_path="data/cleaned_exercises.csv"):
        self.file_path = file_path
        self.df = self.load_data()

    def load_data(self):
        try:
            return pd.read_csv(self.file_path)
        except FileNotFoundError:
            return pd.DataFrame()

    def get_unique_body_parts(self):
        if self.df.empty:
            return []
        return sorted(self.df["bodyPart"].dropna().unique().tolist())

    def get_unique_equipment(self):
        if self.df.empty:
            return []
        return sorted(self.df["equipment"].dropna().unique().tolist())

    def get_data(self):
        return self.df