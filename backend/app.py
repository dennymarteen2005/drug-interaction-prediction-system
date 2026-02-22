from flask import Flask, request, jsonify, send_file
import pickle
import pandas as pd
import re
import os

app = Flask(__name__)

# ================= LOAD MODEL =================
with open("model/interaction_model.pkl", "rb") as f:
    model, vectorizer, label_encoder = pickle.load(f)

# ================= LOAD DATA =================
interaction_df = pd.read_csv("data/drug_interactions.csv")
recommendation_df = pd.read_csv("data/drug_recommendations.csv")
side_effects_df = pd.read_csv("data/drug_side_effects.csv")
# ================= DRUG LIST =================
drug_list = list(
    set(
        interaction_df["drug1"].str.lower().tolist()
        + interaction_df["drug2"].str.lower().tolist()
    )
)

# ================= NLP DRUG EXTRACTION =================
def extract_drugs(text):
    text = text.lower()
    found = set()
    for drug in drug_list:
        if re.search(r"\b" + re.escape(drug) + r"\b", text):
            found.add(drug)
    return list(found)

# ================= RECOMMENDATION =================
def recommend(drug):
    row = recommendation_df[
        recommendation_df["drug"].str.lower() == drug.lower()
    ]
    if not row.empty:
        return row["alternative"].values[0]
    return "No safer alternative found"

# ================= EXPLANATION =================
def explain(severity):
    return {
        "mild": "Low interaction risk. These drugs are generally safe when used together.",
        "moderate": "Moderate interaction detected. Monitoring or dosage adjustment is advised.",
        "severe": "High-risk interaction. These drugs should not be taken together without medical supervision."
    }.get(severity, "No explanation available")

# ================= RISK LEVEL =================
def risk_level(severity):
    return {
        "mild": "Low Risk",
        "moderate": "Medium Risk",
        "severe": "High Risk"
    }.get(severity, "Unknown")

# ================= MANAGEMENT =================
def action_message(severity):
    return {
        "mild": "You may continue medication as prescribed.",
        "moderate": "Consult a doctor and monitor symptoms carefully.",
        "severe": "Avoid taking these drugs together and consult a doctor immediately."
    }.get(severity, "Consult a healthcare professional.")

# ================= INTERACTION DESCRIPTION =================
def interaction_description(d1, d2, severity):
    if severity == "mild":
        return f"{d1} and {d2} have a minor interaction and are usually safe with monitoring."
    elif severity == "moderate":
        return f"{d1} and {d2} may interact and require monitoring or dosage adjustment."
    else:
        return f"{d1} and {d2} have a high-risk interaction and should generally be avoided."

# ================= MECHANISM =================
def mechanism(severity):
    return {
        "mild": "Minimal pharmacological overlap between drugs.",
        "moderate": "Possible metabolic competition or additive drug effects.",
        "severe": "Strong interaction affecting metabolism, toxicity, or bleeding risk."
    }.get(severity, "Unknown interaction mechanism")

DISCLAIMER = (
    "⚠️ This system is for educational and research purposes only. "
    "It is not a substitute for professional medical advice."
)
def get_side_effects(d1, d2):
    row = side_effects_df[
        ((side_effects_df["drug1"].str.lower() == d1.lower()) &
         (side_effects_df["drug2"].str.lower() == d2.lower()))
        |
        ((side_effects_df["drug1"].str.lower() == d2.lower()) &
         (side_effects_df["drug2"].str.lower() == d1.lower()))
    ]
    if not row.empty:
        return row["side_effects"].values[0]
    return "No major side effects recorded in dataset."
# ================= ROUTES =================
@app.route("/")
def home():
    return jsonify({"message": "Drug Interaction Prediction API running"})

# ================= PREDICTION API =================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    detected_drugs = extract_drugs(text)

    if len(detected_drugs) < 2:
        return jsonify({"error": "At least two known drugs required"}), 400

    d1, d2 = detected_drugs[0], detected_drugs[1]

    pair = d1 + " " + d2
    X = vectorizer.transform([pair])
    probs = model.predict_proba(X)[0]
    idx = probs.argmax()

    severity = label_encoder.inverse_transform([idx])[0]
    confidence = round(probs[idx] * 100, 2)

    response = {
        "drugs": [d1, d2],
        "drug_count": len(detected_drugs),
        "severity": severity,
        "risk_level": risk_level(severity),
        "confidence": confidence,

        # NEW DDINTER STYLE FIELDS
        "interaction_description": interaction_description(d1, d2, severity),
        "mechanism": mechanism(severity),
        "management": action_message(severity),
        "explanation": explain(severity),
        "dataset_reference": "Prediction based on labeled clinical drug interaction dataset.",
        "side_effects": get_side_effects(detected_drugs[0], detected_drugs[1]),
        "disclaimer": DISCLAIMER
    }

    if severity in ["moderate", "severe"]:
        response["recommended_alternative"] = recommend(d2)

    return jsonify(response)

# ================= SHAP IMAGE ROUTES =================
@app.route("/shap/global")
def shap_global():
    path = "backend/shap_global.png"
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return jsonify({"error": "Global SHAP plot not found"}), 404

@app.route("/shap/local")
def shap_local():
    path = "backend/shap_local.png"
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return jsonify({"error": "Local SHAP plot not found"}), 404

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)