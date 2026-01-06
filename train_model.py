import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# Load dataset
df = pd.read_csv("data/drug_interactions.csv")

# Create drug pair text
df["pair"] = df["drug1"] + " " + df["drug2"]

# Encode labels
le = LabelEncoder()
y = le.fit_transform(df["severity"])

# TF-IDF feature extraction
vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
X = vectorizer.fit_transform(df["pair"])

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)


# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))


# Save model
with open("model/interaction_model.pkl", "wb") as f:
    pickle.dump((model, vectorizer, le), f)

print("✅ Model trained and saved successfully.")
