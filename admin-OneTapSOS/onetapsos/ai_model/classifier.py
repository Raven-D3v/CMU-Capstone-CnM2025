import joblib
import os
import json
import re

# Load the trained model (TF-IDF + Naive Bayes)
model_path = os.path.join(os.path.dirname(__file__), "emergency_classifier.pkl")
model_data = joblib.load(model_path)
model = joblib.load(model_path)

# Load keyword-based boosting dictionary
keywords_path = os.path.join(os.path.dirname(__file__), "keyword_boost.json")
with open(keywords_path, 'r', encoding='utf-8') as f:
    keyword_dict = json.load(f)

def keyword_boost_levels(text):
    """
    Enhanced keyword boosting with level-based weighting.
    Returns:
        score_dict (dict): label -> total keyword match score
    """
    text = text.lower()
    score_dict = {}

    for label, keywords in keyword_dict.items():
        score = 0
        for entry in keywords:
            *keyword_parts, level_str = entry.rsplit(" ", 1)
            keyword = " ".join(keyword_parts)
            try:
                level = int(level_str)
            except ValueError:
                continue

            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                score += level
        if score > 0:
            score_dict[label] = score

    return score_dict

def classify_emergency(text):
    """
    Returns:
        label (str): predicted category
        confidence (float): confidence percentage (0–100)
    """
    prediction_proba = model.predict_proba([text])[0]
    predicted_label = model.classes_[prediction_proba.argmax()]
    confidence = round(prediction_proba.max() * 100, 2)

    # Use new level-based keyword scoring
    match_scores = keyword_boost_levels(text)

    if match_scores:
        # Get top-scoring keyword label
        top_keyword_label = max(match_scores, key=match_scores.get)
        top_keyword_score = match_scores[top_keyword_label]

        # Boost confidence if top keyword matches model prediction
        if top_keyword_label == predicted_label:
            confidence = min(confidence + top_keyword_score * 3, 100.0)
        else:
            alt_index = list(model.classes_).index(top_keyword_label)
            alt_conf = prediction_proba[alt_index] * 100 + top_keyword_score * 3
            if alt_conf > confidence:
                predicted_label = top_keyword_label
                confidence = round(min(alt_conf, 100.0), 2)

    return predicted_label, confidence

# Optional test run
if __name__ == "__main__":
    test_text = "Ninakawan ako ng wallet"
    label, confidence = classify_emergency(test_text)
    print(f"Test: {test_text}")
    print(f"Prediction: {label} ({confidence}%)")
