import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import shap

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# ==============================
# LOAD DATA
# ==============================
df = pd.read_csv("backend/data/drug_interactions.csv")

# Ensure lowercase consistency
df["drug1"] = df["drug1"].str.lower()
df["drug2"] = df["drug2"].str.lower()
df["severity"] = df["severity"].str.lower()

# Create text feature
df["pair"] = df["drug1"] + " " + df["drug2"]

X = df["pair"]
y = df["severity"]

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# ==============================
# TRAIN / TEST SPLIT
# ==============================
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded,
    test_size=0.25,
    random_state=42,
    stratify=y_encoded
)

# ==============================
# FEATURE EXTRACTION
# ==============================
vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=500
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ==============================
# MODEL TRAINING
# ==============================
model = LogisticRegression(
    max_iter=1000,
    multi_class="multinomial"
)

model.fit(X_train_vec, y_train)

# ==============================
# MODEL EVALUATION
# ==============================
y_pred = model.predict(X_test_vec)

accuracy = accuracy_score(y_test, y_pred)
print(f"\n✅ Model Accuracy: {accuracy * 100:.2f} %\n")

print("📊 Classification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=label_encoder.classes_
))

# ==============================
# CONFUSION MATRIX
# ==============================
cm = confusion_matrix(
    y_test,
    y_pred,
    labels=range(len(label_encoder.classes_))
)

plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=label_encoder.classes_,
    yticklabels=label_encoder.classes_
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig("backend/confusion_matrix.png", dpi=300)
plt.close()

print("✅ Confusion Matrix saved as backend/confusion_matrix.png")

# ==============================
# SAVE MODEL
# ==============================
os_path = "backend/model/interaction_model.pkl"
with open(os_path, "wb") as f:
    pickle.dump((model, vectorizer, label_encoder), f)

print("✅ Model saved successfully")

# ==============================
# GLOBAL SHAP EXPLANATION
# ==============================
print("\nGenerating Global SHAP Explanation...")

explainer = shap.LinearExplainer(
    model,
    X_train_vec,
    feature_perturbation="interventional"
)

shap_values = explainer.shap_values(X_train_vec)

# Use SEVERE class for global explanation (highest risk)
severe_index = list(label_encoder.classes_).index("severe")

shap.summary_plot(
    shap_values[severe_index] if isinstance(shap_values, list) else shap_values,
    X_train_vec.toarray(),
    feature_names=vectorizer.get_feature_names_out(),
    show=False
)

plt.title("Global SHAP Explanation (Severe Interactions)")
plt.tight_layout()
plt.savefig("backend/shap_global.png", dpi=300)
plt.close()

print("✅ Global SHAP plot saved")

# ==============================
# DRUG-SPECIFIC EVALUATION
# ==============================
def evaluate_specific_drug(drug_name, df, model, vectorizer, label_encoder):
    print(f"\n🔍 Drug-Specific Evaluation for: {drug_name.upper()}")

    drug_df = df[
        (df["drug1"] == drug_name.lower()) |
        (df["drug2"] == drug_name.lower())
    ].copy()

    if drug_df.empty:
        print("⚠️ No data found for this drug")
        return

    drug_df["pair"] = drug_df["drug1"] + " " + drug_df["drug2"]

    X_drug = vectorizer.transform(drug_df["pair"])
    y_true = label_encoder.transform(drug_df["severity"])
    y_pred = model.predict(X_drug)

    print("\n📊 Classification Report:")
    print(classification_report(
        y_true,
        y_pred,
        labels=range(len(label_encoder.classes_)),
        target_names=label_encoder.classes_,
        zero_division=0
    ))

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=range(len(label_encoder.classes_))
    )

    plt.figure(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Oranges",
        xticklabels=label_encoder.classes_,
        yticklabels=label_encoder.classes_
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion Matrix – {drug_name.upper()}")
    plt.tight_layout()
    plt.savefig(f"backend/confusion_matrix_{drug_name}.png", dpi=300)
    plt.close()

    print(f"✅ Confusion matrix saved: backend/confusion_matrix_{drug_name}.png")

# Evaluate key drugs
evaluate_specific_drug("warfarin", df, model, vectorizer, label_encoder)
evaluate_specific_drug("ibuprofen", df, model, vectorizer, label_encoder)
evaluate_specific_drug("paracetamol", df, model, vectorizer, label_encoder)

# ==============================
# LOCAL SHAP EXPLANATION
# ==============================
def shap_local_explanation(text_input, model, vectorizer, label_encoder):
    print("\n🔍 Generating Local SHAP Explanation...")

    X_input = vectorizer.transform([text_input])

    explainer = shap.LinearExplainer(
        model,
        X_train_vec,
        feature_perturbation="interventional"
    )

    shap_values = explainer.shap_values(X_input)

    pred_class_index = model.predict(X_input)[0]
    pred_class_name = label_encoder.inverse_transform([pred_class_index])[0]

    print(f"🧠 Predicted Severity: {pred_class_name.upper()}")

    # SAFE handling
    if isinstance(shap_values, list):
        class_shap_values = shap_values[pred_class_index]
    else:
        class_shap_values = shap_values

    shap.summary_plot(
        class_shap_values,
        X_input.toarray(),
        feature_names=vectorizer.get_feature_names_out(),
        plot_type="bar",
        show=False
    )

    plt.title(f"Local SHAP Explanation ({pred_class_name.upper()})")
    plt.tight_layout()
    plt.savefig("backend/shap_local.png", dpi=300)
    plt.close()

    print("✅ Local SHAP explanation saved: backend/shap_local.png")

# Example local explanation
shap_local_explanation(
    "warfarin aspirin",
    model,
    vectorizer,
    label_encoder
)
