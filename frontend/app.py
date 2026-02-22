import streamlit as st
import requests
import time

st.set_page_config(page_title="Drug Interaction Prediction", layout="centered")

# ================= TITLE =================
st.markdown("""
<h1 style='text-align:center;color:#4CAF50;'>💊 Drug Interaction Prediction System</h1>
<p style='text-align:center;font-size:18px;'>
Enter medicines in natural language<br>
<i>Example: I am taking warfarin and aspirin</i>
</p>
""", unsafe_allow_html=True)

text = st.text_area("🔍 Enter medicines:", height=120)

# ================= BUTTON =================
if st.button("🚀 Analyze Interactions", use_container_width=True):

    if not text.strip():
        st.warning("⚠️ Please enter medicine details.")
    else:

        placeholder = st.empty()

        with placeholder.container():
            st.info("🧬 Analyzing drug interactions...")

        try:
            res = requests.post(
                "http://127.0.0.1:5000/predict",
                json={"text": text},
                timeout=10
            )

            placeholder.empty()

            if res.status_code == 200:

                data = res.json()

                # ================= DETECTED DRUGS =================
                st.markdown("### 💊 Detected Drugs")
                st.success(", ".join(data["drugs"]))

                # ================= SEVERITY =================
                st.markdown("### ⚠️ Severity Level")
                severity = data["severity"].upper()

                if severity == "SEVERE":
                    st.error(severity)
                elif severity == "MODERATE":
                    st.warning(severity)
                else:
                    st.success(severity)

                # ================= CONFIDENCE =================
                st.markdown("### 📊 Confidence")
                st.progress(int(data["confidence"]))
                st.write(f"**{data['confidence']} %**")

                # ================= INTERACTION DESCRIPTION =================
                if "interaction_description" in data:
                    st.markdown("### 🧾 Interaction Description")
                    st.info(data["interaction_description"])

                # ================= MECHANISM =================
                if "mechanism" in data:
                    st.markdown("### ⚙️ Mechanism of Interaction")
                    st.info(data["mechanism"])

                # ================= MANAGEMENT =================
                if "management" in data:
                    st.markdown("### 🏥 Management Advice")
                    st.warning(data["management"])

                # ================= EXPLANATION =================
                st.markdown("### 🧠 Explanation")
                st.write(data.get("explanation", ""))
                # ================= SIDE EFFECTS =================
                st.markdown("### 🩺 Possible Side Effects")
                st.warning(data.get("side_effects", "Not available"))
                # ================= ALTERNATIVE =================
                if "recommended_alternative" in data:
                    st.markdown("### 💡 Safer Alternative")
                    st.success(data["recommended_alternative"])

                # ================= DATASET NOTE =================
                if "dataset_reference" in data:
                    st.markdown("### 📚 Dataset Reference")
                    st.caption(data["dataset_reference"])

                # ================= DISCLAIMER =================
                st.markdown("---")
                st.caption(data["disclaimer"])

            else:
                st.error(f"❌ {res.json().get('error')}")

        except Exception as e:
            placeholder.empty()
            st.error(f"❌ Backend error: {e}")