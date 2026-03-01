import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import OneHotEncoder

def train_similarity_model():
    df = pd.read_csv("data/cleaned_exercises.csv")

    features = df[["target", "bodyPart","equipment"]]

    encoder = OneHotEncoder()
    encoded_matrix = encoder.fit_transform(features)

    similarity_matrix = cosine_similarity(encoded_matrix)

    model_data = {
        "similarity_matrix": similarity_matrix,
        "exercise_names": df["name"].tolist(),
        "df": df
    }

    with open("data/similarity_model.pkl", "wb") as f:
        pickle.dump(model_data, f)

if __name__ == "__main__":
    train_similarity_model()

