import streamlit as st
import requests

st.set_page_config(page_title="Drug Interaction Prediction", layout="centered")

st.title("💊 Drug Interaction Prediction System")

st.markdown("""
Enter medicines in **natural language**.

Example:  
*I am taking warfarin and aspirin*
""")

text = st.text_area("Enter medicines:", height=120)

if st.button("Analyze"):
    if not text.strip():
        st.warning("Please enter medicine details.")
    else:
        with st.spinner("Analyzing..."):
            try:
                res = requests.post(
                    "http://127.0.0.1:5000/predict",
                    json={"text": text},
                    timeout=10
                )
                if res.status_code == 200:
                    data = res.json()

                    st.subheader("Detected Drugs")
                    st.write(", ".join(data["drugs"]))

                    st.subheader("Interaction Severity")
                    st.write(data["severity"].upper())

                    st.subheader("Confidence Score")
                    st.write(f"{data['confidence']}%")

                    st.subheader("Explanation")
                    st.write(data["explanation"])

                    if "recommended_alternative" in data:
                        st.subheader("Recommended Alternative")
                        st.write(data["recommended_alternative"])

                    st.info(data["disclaimer"])
                else:
                    st.error(res.json().get("error"))

            except Exception as e:
                st.error(f"Backend error: {e}")
