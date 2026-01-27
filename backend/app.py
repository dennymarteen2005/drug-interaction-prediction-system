from flask import Flask, request, jsonify
import pickle
import pandas as pd
import re

app = Flask(__name__)

# ========== LOAD MODEL ==========
with open("model/interaction_model.pkl", "rb") as f:
    model, vectorizer, label_encoder = pickle.load(f)

# ========== LOAD DATA ==========
interaction_df = pd.read_csv(r"backend/data/drug_interactions.csv")
recommendation_df = pd.read_csv(r"backend/data/drug_recommendations.csv")

# ========== DRUG LIST ==========
drug_list = list(
    set(interaction_df["drug1"].str.lower().tolist() +
        interaction_df["drug2"].str.lower().tolist())
)

# ========== NLP DRUG EXTRACTION ==========
def extract_drugs(text):
    text = text.lower()
    found = set()
    for drug in drug_list:
        if re.search(r"\b" + re.escape(drug) + r"\b", text):
            found.add(drug)
    return list(found)

# ========== RECOMMENDATION ==========
def recommend(drug):
    row = recommendation_df[
        recommendation_df["drug"].str.lower() == drug.lower()
    ]
    if not row.empty:
        return row["alternative"].values[0]
    return "No safer alternative found"

# ========== EXPLANATION ==========
def explain(severity):
    return {
        "mild": "Low interaction risk based on known data.",
        "moderate": "Moderate interaction. Monitoring is recommended.",
        "severe": "High-risk interaction with serious side effects."
    }.get(severity, "No explanation available")

# ========== RISK LEVEL ==========
def risk_level(severity):
    return {
        "mild": "Low Risk",
        "moderate": "Medium Risk",
        "severe": "High Risk"
    }.get(severity, "Unknown")

# ========== ACTION MESSAGE ==========
def action_message(severity):
    return {
        "mild": "You may continue medication as prescribed.",
        "moderate": "Consult a doctor if symptoms appear.",
        "severe": "Avoid taking these drugs together."
    }.get(severity, "Consult a healthcare professional.")

DISCLAIMER = (
    "⚠️ Educational purpose only. Not a replacement for medical advice."
)

# ========== ROUTES ==========
@app.route("/")
def home():
    return jsonify({"message": "Drug Interaction Prediction API running"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    detected_drugs = extract_drugs(text)

    if len(detected_drugs) < 2:
        return jsonify({"error": "At least two known drugs required"}), 400

    pair = detected_drugs[0] + " " + detected_drugs[1]
    X = vectorizer.transform([pair])
    probs = model.predict_proba(X)[0]
    idx = probs.argmax()

    severity = label_encoder.inverse_transform([idx])[0]
    confidence = round(probs[idx] * 100, 2)

    response = {
        "drugs": detected_drugs[:2],
        "drug_count": len(detected_drugs),
        "severity": severity,
        "risk_level": risk_level(severity),
        "confidence": confidence,
        "explanation": explain(severity),
        "what_should_i_do": action_message(severity),
        "disclaimer": DISCLAIMER
    }

    if severity in ["moderate", "severe"]:
        response["recommended_alternative"] = recommend(detected_drugs[1])

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)