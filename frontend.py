import streamlit as st
import requests
import time
import matplotlib.pyplot as plt

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Drug Interaction Prediction",
    layout="centered"
)

BACKEND_URL = "http://127.0.0.1:5000/predict"

# ================= CSS =================
st.markdown("""
<style>
body {
    font-family: 'Poppins', sans-serif;
}
.stApp {
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
@keyframes gradient {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}
.card {
    background: rgba(255,255,255,0.95);
    border-radius: 20px;
    padding: 25px;
    margin-top: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.2);
}
.severity-high { color: #e53e3e; font-size: 32px; font-weight: bold; }
.severity-moderate { color: #ed8936; font-size: 32px; font-weight: bold; }
.severity-mild { color: #48bb78; font-size: 32px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("<h1 style='text-align:center;color:white;'>💊 Drug Interaction Prediction System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:white;'>AI-based severity prediction with Explainable AI (SHAP)</p>", unsafe_allow_html=True)

# ================= INPUT =================
text = st.text_area(
    "📝 Enter medicines in natural language",
    placeholder="Example: I am taking ibuprofen along with prednisone",
    height=120
)

# ================= BUTTON =================
if st.button("🔍 Analyze Interaction", use_container_width=True):

    if not text.strip():
        st.warning("Please enter medicine details.")
    else:
        with st.spinner("Analyzing drug interactions using AI..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"text": text},
                    timeout=15
                )

                if response.status_code != 200:
                    st.error(response.json().get("error"))
                else:
                    data = response.json()

                    # ================= RESULTS =================
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("💊 Detected Drugs")
                    for d in data["drugs"]:
                        st.markdown(f"- **{d}**")
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("### 🌍 Global Model Explanation (SHAP)")
                    st.image("backend/shap_global_summary.png",
                            caption="Overall feature importance across all drug interactions",
                            use_column_width=True)

                    # ================= SEVERITY =================
                    severity = data["severity"].lower()
                    sev_class = f"severity-{severity}"

                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("⚠️ Interaction Severity")
                    st.markdown(
                        f"<div class='{sev_class}'>{data['severity'].upper()}</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                    # ================= CONFIDENCE =================
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("📊 Prediction Confidence")
                    st.progress(int(data["confidence"]))
                    st.write(f"**{data['confidence']}% confidence**")
                    st.markdown("</div>", unsafe_allow_html=True)

                    # ================= EXPLANATION =================
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.subheader("🧠 Model Explanation")
                    st.write(data["explanation"])
                    st.markdown("</div>", unsafe_allow_html=True)

                    # ================= SHAP EXPLAINABLE AI =================
                    shap_data = data.get("shap_explanation", [])

                    if shap_data:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.subheader("🔍 Explainable AI (SHAP Analysis)")
                        st.write(
                            "This chart shows how much each drug influenced the model's decision."
                        )

                        features = [x["feature"] for x in shap_data]
                        impacts = [x["impact"] for x in shap_data]

                        fig, ax = plt.subplots()
                        ax.barh(features, impacts, color="purple")
                        ax.set_xlabel("Impact on Severity Prediction")
                        ax.set_ylabel("Drug")
                        ax.set_title("SHAP Feature Contribution")

                        st.pyplot(fig)
                        st.markdown("</div>", unsafe_allow_html=True)

                    # ================= ALTERNATIVE =================
                    if "recommended_alternative" in data:
                        st.markdown("<div class='card'>", unsafe_allow_html=True)
                        st.subheader("💡 Safer Alternative")
                        st.success(data["recommended_alternative"])
                        st.markdown("</div>", unsafe_allow_html=True)

                    # ================= DISCLAIMER =================
                    st.info(data["disclaimer"])

            except Exception as e:
                st.error(f"Backend error: {e}")
