import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
import os

def train_model():
    with open(os.path.join(os.path.dirname(__file__), "SOS-Ai-TrainingData.json"), encoding='utf-8') as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    labels = [item["label"] for item in data]

    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(texts, labels)

    model_path = os.path.join(os.path.dirname(__file__), "emergency_classifier.pkl")
    joblib.dump(model, model_path)

if __name__ == "__main__":
    train_model()