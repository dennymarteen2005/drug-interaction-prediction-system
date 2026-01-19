import streamlit as st
import requests
import time

# ================= PAGE CONFIG =================
st.title("ui updated")
st.set_page_config(
    page_title="Drug Interaction Prediction",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= BACKEND URL =================
BACKEND_URL = "https://drug-interaction-backend.onrender.com/predict"

# ================= CSS + ANIMATIONS =================
st.markdown("""
<style>

/* ===== Animated Gradient Background ===== */
.stApp {
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364, #000000);
    background-size: 400% 400%;
    animation: gradientBG 14s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* ===== Main Card ===== */
.card {
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 35px;
    box-shadow: 0 25px 60px rgba(0,0,0,0.4);
    transition: transform 0.4s ease, box-shadow 0.4s ease;
    margin-top: 40px;
}

.card:hover {
    transform: translateY(-10px);
    box-shadow: 0 30px 70px rgba(0,255,255,0.35);
}

/* ===== Title ===== */
.title {
    text-align: center;
    font-size: 46px;
    font-weight: 800;
    color: cyan;
    letter-spacing: 1px;
}

/* ===== Subtitle ===== */
.subtitle {
    text-align: center;
    color: #ddd;
    font-size: 18px;
    margin-bottom: 30px;
}

/* ===== Result Box Animation ===== */
.result-box {
    animation: fadeUp 0.9s ease forwards;
    background: rgba(0,0,0,0.6);
    padding: 25px;
    border-radius: 16px;
    margin-top: 25px;
    border-left: 6px solid cyan;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(35px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* ===== Button Style ===== */
button[kind="primary"] {
    background: linear-gradient(90deg, cyan, #00ffaa);
    border-radius: 14px;
    font-size: 18px;
    padding: 10px 25px;
}

/* ===== Spinner Color ===== */
div[data-testid="stSpinner"] > div {
    border-top-color: cyan !important;
}

</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="title">💊 Drug–Drug Interaction Predictor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI-powered system to detect potential drug interactions from clinical text</div>',
    unsafe_allow_html=True
)

# ================= CARD START =================
st.markdown('<div class="card">', unsafe_allow_html=True)

user_input = st.text_area(
    "📝 Enter patient drug usage sentence",
    placeholder="Example: The patient uses ibuprofen along with prednisone",
    height=120
)

predict_clicked = st.button("🔍 Predict Interaction")

st.markdown('</div>', unsafe_allow_html=True)

# ================= PREDICTION =================
if predict_clicked:
    if len(user_input.strip().split()) < 3:
        st.error("⚠️ Please enter a sentence with at least two drugs.")
    else:
        try:
            with st.spinner("Analyzing drug interactions using AI..."):
                time.sleep(1.2)  # smooth UX
                response = requests.post(
                    BACKEND_URL,
                    json={"text": user_input},
                    timeout=25
                )

            if response.status_code == 200:
                result = response.json()

                st.markdown(f"""
                <div class="result-box">
                    <h3>⚠️ Interaction Severity: <span style="color:cyan">{result.get("severity","Unknown")}</span></h3>
                    <p><b>Confidence:</b> {result.get("confidence","N/A")}%</p>
                    <p><b>Explanation:</b> {result.get("explanation","No details available.")}</p>
                </div>
                """, unsafe_allow_html=True)

            else:
                st.error("❌ Backend error. Please try again later.")

        except Exception as e:
            st.error(f"❌ Error connecting to backend: {e}")

# ================= FOOTER =================
st.markdown("""
<br><br>
<div style="text-align:center; color:#aaa;">
    Built with ❤️ using Python, ML & Streamlit<br>
    Academic Project – Drug Interaction Prediction System
</div>
""", unsafe_allow_html=True)
