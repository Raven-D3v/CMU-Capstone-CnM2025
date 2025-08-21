import joblib
import os
import json
import re
import random  # for probabilistic dropping

# Paths
BASE_DIR = os.path.dirname(__file__)
WORD_LVL_DIR = os.path.join(BASE_DIR, "training_dt/word_lvl")
print("[DEBUG] WORD directory:", WORD_LVL_DIR)

# Load the trained model (TF-IDF + Naive Bayes)
model_path = os.path.join(BASE_DIR, "emergency_classifier.pkl")
model = joblib.load(model_path)

# Load keyword-based boosting dictionary
keywords_path = os.path.join(BASE_DIR, "keyword_boost.json")
with open(keywords_path, 'r', encoding='utf-8') as f:
    keyword_dict = json.load(f)

# Load normalization dictionary
normalization_path = os.path.join(BASE_DIR, "word_normalization.json")
with open(normalization_path, 'r', encoding='utf-8') as f:
    normalization_dict = json.load(f)

# Load global word weights (applied to all text, regardless of category)
global_word_weights_path = os.path.join(WORD_LVL_DIR, "word_weight.json")
print("[DEBUG] word_weights directory:", global_word_weights_path)
if os.path.exists(global_word_weights_path):
    with open(global_word_weights_path, "r", encoding="utf-8") as f:
        global_word_weights = json.load(f)
else:
    global_word_weights = {}
    
# Load category-specific word levels (optional)
category_word_weights = {}
for category_file in ["assault_word.json", "robbery_word.json", "harassment_word.json", "others_word.json"]:
    path = os.path.join(WORD_LVL_DIR, category_file)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            category_word_weights[category_file.replace("_word.json", "")] = json.load(f)

# Compile regex patterns for normalization
substitution_patterns = {
    re.compile(r'\b(' + '|'.join(map(re.escape, variants)) + r')\b'): root
    for root, variants in normalization_dict.items()
}

def normalize_text(text):
    """Replace word variants with their normalized root forms."""
    text = text.lower()
    for pattern, replacement in substitution_patterns.items():
        text = pattern.sub(replacement, text)                
    return text

def apply_word_weights(text):
    """
    Apply word weights deterministically (no randomness).
    - weight = 0   → always drop
    - 0 < weight < 1 → keep only if weight >= 0.5
    - weight = 1   → keep once (normal)
    - weight > 1   → duplicate according to rounded weight
    """
    print("[DEBUG] Loaded word weights:", global_word_weights)

    tokens = text.split()
    weighted_tokens = []

    for token in tokens:
        weight = global_word_weights.get(token, 1.0)

        if weight == 0:
            print(f"[DEBUG] Dropped '{token}' (weight=0)")
            continue
        elif weight < 1.0:
            if weight >= 0.5:
                weighted_tokens.append(token)
                print(f"[DEBUG] Soft-kept '{token}' (weight={weight})")
            else:
                print(f"[DEBUG] Dropped '{token}' (weight={weight})")
        else:
            weighted_tokens.extend([token] * int(round(weight)))
            if weight > 1:
                print(f"[DEBUG] Duplicated '{token}' x{int(round(weight))} (weight={weight})")
            else:
                print(f"[DEBUG] Kept '{token}' (weight=1)")
                
    # Add this line to see the reconstructed text
    final_text = " ".join(weighted_tokens)
    print(f"[DEBUG] Final text after weighting: '{final_text}'")

    return " ".join(weighted_tokens)

    

def keyword_boost_levels(text):
    """
    Keyword boosting based on keyword_boost.json.
    Returns: dict {label: total score}
    """
    score_dict = {}
    for label, keywords in keyword_dict.items():
        score = 0.0
        for entry in keywords:
            *keyword_parts, level_str = entry.rsplit(" ", 1)
            keyword = " ".join(keyword_parts)
            try:
                keyword_level = int(level_str)
            except ValueError:
                continue

            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                score += keyword_level
        if score > 0:
            score_dict[label] = score
    return score_dict

def classify_emergency(text):
    # Step 1: Normalize
    normalized_text = normalize_text(text)

    # Step 2: Apply word weights
    weighted_text = apply_word_weights(normalized_text)

    # SAFETY CHECK: too short → classify as "others"
    if len(weighted_text.split()) < 2:
        print(f"[DEBUG] Too few meaningful tokens → classified as 'others'")
        return "others", 0.0

    # Step 3: Model prediction
    print(f"[DEBUG] Text passed to model: '{weighted_text}'")
    prediction_proba = model.predict_proba([weighted_text])[0]
    predicted_label = model.classes_[prediction_proba.argmax()]
    confidence = round(prediction_proba.max() * 100, 2)

    # Step 4: Keyword boosting
    match_scores = keyword_boost_levels(normalized_text)

    # Debug info
    print(f"[DEBUG] Raw Text: {text}")
    print(f"[DEBUG] Normalized: {normalized_text}")
    print(f"[DEBUG] Weighted Text: {weighted_text}")
    print(f"[DEBUG] Prediction Probabilities: {dict(zip(model.classes_, prediction_proba))}")
    print(f"[DEBUG] Keyword Match Scores: {match_scores}")
    print(f"[DEBUG] Initial Prediction: {predicted_label} ({confidence}%)")

    # Step 5: Combine AI prediction with keyword boosting
    if match_scores:
        top_keyword_label = max(match_scores, key=match_scores.get)
        top_keyword_score = match_scores[top_keyword_label]

        if top_keyword_label == predicted_label:
            confidence = min(confidence + top_keyword_score * 7, 100.0)
        else:
            alt_index = list(model.classes_).index(top_keyword_label)
            alt_conf = prediction_proba[alt_index] * 100 + top_keyword_score * 7
            if alt_conf > confidence:
                predicted_label = top_keyword_label
                confidence = round(min(alt_conf, 100.0), 2)

    return predicted_label, confidence

# Optional test run
if __name__ == "__main__":
    test_text = input("Input your emergency here: ")
    label, confidence = classify_emergency(test_text)
    print(f"Test: {test_text}")
    print(f"Prediction: {label} ({confidence}%)")
