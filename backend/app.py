from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
import re

app = Flask(__name__)

# Load ML model
with open("model/interaction_model.pkl", "rb") as f:
    model, vectorizer, label_encoder = pickle.load(f)

# Load datasets
interaction_df = pd.read_csv("data/drug_interactions.csv")
recommendation_df = pd.read_csv("data/drug_recommendations.csv")

# Drug list
drug_list = list(
    set(interaction_df["drug1"].tolist() + interaction_df["drug2"].tolist())
)

# NLP drug extraction
def extract_drugs(text):
    text = text.lower()
    found = set()
    for drug in drug_list:
        if re.search(r"\b" + re.escape(drug.lower()) + r"\b", text):
            found.add(drug.lower())
    return list(found)

# Recommendation module
def recommend(drug):
    row = recommendation_df[
        recommendation_df["drug"].str.lower() == drug.lower()
    ]
    if not row.empty:
        return row["alternative"].values[0]
    return None

# Explainability
def explain(severity):
    if severity == "mild":
        return "Low interaction risk based on learned dataset patterns."
    elif severity == "moderate":
        return "Known interaction patterns; monitoring or dosage adjustment recommended."
    else:
        return "High-risk drug combination with potential serious adverse effects."

DISCLAIMER = (
    "This system is for educational and research purposes only and "
    "is not a substitute for professional medical advice."
)

@app.route("/")
def home():
    return jsonify({"message": "Drug Interaction Prediction API running"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    drugs = extract_drugs(text)
    if len(drugs) < 2:
        return jsonify({"error": "At least two known drugs required"}), 400

    pair = drugs[0] + " " + drugs[1]
    X = vectorizer.transform([pair])
    probs = model.predict_proba(X)[0]
    idx = probs.argmax()

    severity = label_encoder.inverse_transform([idx])[0]
    confidence = round(probs[idx] * 100, 2)

    response = {
        "drugs": drugs[:2],
        "severity": severity,
        "confidence": confidence,
        "explanation": explain(severity),
        "disclaimer": DISCLAIMER
    }

    if severity in ["moderate", "severe"]:
        response["recommended_alternative"] = (
            recommend(drugs[1]) or "No safer alternative found"
        )

    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

