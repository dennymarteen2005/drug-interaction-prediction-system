import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="Drug Interaction Prediction System",
    page_icon="💊",
    layout="centered"
)

# Title
st.title("💊 Drug Interaction Prediction System")
st.write(
    "Enter a sentence containing **two drug names**. "
    "The system will predict possible drug–drug interaction severity."
)

# Medical disclaimer
st.warning(
    "⚠️ This tool is for **educational purposes only**. "
    "Always consult a healthcare professional."
)

# Input box
user_input = st.text_area(
    "Enter your text:",
    placeholder="Example: I am taking warfarin and aspirin"
)

# Backend URL (your deployed backend)
BACKEND_URL = "https://drug-interaction-backend.onrender.com/predict"

# Predict button
if st.button("🔍 Predict Interaction"):
    if user_input.strip() == "":
        st.error("Please enter some text.")
    else:
        with st.spinner("Analyzing drug interaction..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"text": user_input},
                    timeout=60
                )


                if response.status_code == 200:
                    result = response.json()

                    st.success("Prediction Successful ✅")

                    st.subheader("📊 Results")
                    st.write(f"**Drug 1:** {result.get('drug_1', 'N/A')}")
                    st.write(f"**Drug 2:** {result.get('drug_2', 'N/A')}")

                    severity = result.get("severity", "Unknown")
                    confidence = result.get("confidence", 0)

                    if severity.lower() == "high":
                        st.error(f"🚨 Severity: {severity}")
                    elif severity.lower() == "moderate":
                        st.warning(f"⚠️ Severity: {severity}")
                    else:
                        st.success(f"✅ Severity: {severity}")

                    st.write(f"**Confidence Score:** {confidence:.2f}")
                    st.write(f"**Explanation:** {result.get('explanation', 'N/A')}")
                    st.write(f"**Recommendation:** {result.get('recommendation', 'N/A')}")

                else:
                    st.error("Backend error. Please try again later.")

            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
