import streamlit as st
import requests
import time

st.set_page_config(page_title="Drug Interaction Prediction", layout="centered")

# Custom CSS for animations and styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.05); }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes float {
        0%, 100% {
            transform: translateY(0px) rotate(0deg);
        }
        50% {
            transform: translateY(-25px) rotate(8deg);
        }
    }
    
    @keyframes floatReverse {
        0%, 100% {
            transform: translateY(0px) rotate(0deg);
        }
        50% {
            transform: translateY(25px) rotate(-8deg);
        }
    }
    
    @keyframes drift {
        0% {
            transform: translate(0, 0) rotate(0deg);
        }
        25% {
            transform: translate(15px, -20px) rotate(10deg);
        }
        50% {
            transform: translate(-10px, -40px) rotate(-10deg);
        }
        75% {
            transform: translate(-20px, -20px) rotate(5deg);
        }
        100% {
            transform: translate(0, 0) rotate(0deg);
        }
    }
    
    @keyframes morph {
        0%, 100% {
            border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%;
        }
        50% {
            border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%;
        }
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Animated gradient background */
    .stApp {
        background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
    }
    
    /* Floating medical elements */
    .floating-bg {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    
    .medicine {
        position: absolute;
        font-size: 3rem;
        opacity: 0.12;
        animation-duration: 8s;
        animation-iteration-count: infinite;
        animation-timing-function: ease-in-out;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
        transition: all 0.3s ease;
    }
    
    .medicine:hover {
        opacity: 0.4;
        transform: scale(1.3) rotate(15deg) !important;
        filter: drop-shadow(0 0 20px rgba(255,255,255,0.6));
    }
    
    .medicine:nth-child(1) { left: 10%; top: 15%; animation: float 7s infinite; animation-delay: 0s; }
    .medicine:nth-child(2) { left: 85%; top: 25%; animation: floatReverse 8s infinite; animation-delay: 1s; }
    .medicine:nth-child(3) { left: 20%; top: 65%; animation: drift 9s infinite; animation-delay: 2s; }
    .medicine:nth-child(4) { left: 80%; top: 70%; animation: float 10s infinite; animation-delay: 1.5s; }
    .medicine:nth-child(5) { left: 50%; top: 10%; animation: floatReverse 8.5s infinite; animation-delay: 0.5s; }
    .medicine:nth-child(6) { left: 30%; top: 45%; animation: drift 9.5s infinite; animation-delay: 3s; }
    .medicine:nth-child(7) { left: 65%; top: 85%; animation: float 8s infinite; animation-delay: 2.5s; }
    .medicine:nth-child(8) { left: 45%; top: 80%; animation: floatReverse 9s infinite; animation-delay: 1s; }
    .medicine:nth-child(9) { left: 15%; top: 35%; animation: drift 7.5s infinite; animation-delay: 4s; }
    .medicine:nth-child(10) { left: 75%; top: 50%; animation: float 8.5s infinite; animation-delay: 3.5s; }
    
    /* Floating DNA strands */
    .dna-helix {
        position: absolute;
        width: 100px;
        height: 400px;
        opacity: 0.08;
    }
    
    .dna-helix:nth-child(11) { left: 5%; top: 20%; animation: spin 30s linear infinite; }
    .dna-helix:nth-child(12) { right: 5%; top: 40%; animation: spin 35s linear infinite reverse; }
    
    /* Morphing blobs */
    .blob {
        position: absolute;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(255,255,255,0.1), transparent);
        animation: morph 10s ease-in-out infinite, float 15s ease-in-out infinite;
        filter: blur(40px);
    }
    
    .blob:nth-child(13) { left: -10%; top: -10%; }
    .blob:nth-child(14) { right: -10%; bottom: -10%; animation-delay: 5s; }
    
    .content-wrapper {
        position: relative;
        z-index: 1;
        padding: 2rem 1rem;
    }
    
    .main-title {
        text-align: center;
        font-size: 3.5rem;
        font-weight: 700;
        color: white;
        text-shadow: 0 5px 30px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
        animation: slideIn 0.8s ease-out;
        letter-spacing: -1px;
    }
    
    .main-title:hover {
        animation: pulse 1s ease-in-out;
    }
    
    .subtitle {
        text-align: center;
        color: rgba(255,255,255,0.95);
        font-size: 1.2rem;
        margin-bottom: 3rem;
        animation: slideIn 1s ease-out;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .result-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 25px;
        margin: 1.5rem 0;
        animation: slideIn 0.6s ease-out;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 2px solid rgba(255,255,255,0.5);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .result-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
        transform: rotate(45deg);
        transition: all 0.5s ease;
    }
    
    .result-card:hover::before {
        left: 100%;
    }
    
    .result-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(0,0,0,0.25);
    }
    
    .result-card h3 {
        color: #2d3748;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
        font-weight: 600;
        position: relative;
    }
    
    .drug-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.8rem;
        border-radius: 30px;
        margin: 0.5rem 0.5rem 0.5rem 0;
        font-weight: 600;
        font-size: 1.1rem;
        animation: slideIn 0.4s ease-out;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .drug-badge:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .severity-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 25px;
        margin: 1.5rem 0;
        animation: slideIn 0.6s ease-out;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .severity-card::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .severity-card:hover::after {
        width: 500px;
        height: 500px;
    }
    
    .severity-card:hover {
        transform: scale(1.02);
    }
    
    .severity-high {
        border: 3px solid #e53e3e;
        background: linear-gradient(135deg, rgba(229, 62, 62, 0.1), rgba(255, 255, 255, 0.95));
    }
    
    .severity-high .severity-text {
        color: #e53e3e;
        font-size: 3rem;
        font-weight: 700;
        margin: 1rem 0;
        text-shadow: 0 3px 10px rgba(229, 62, 62, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .severity-moderate {
        border: 3px solid #ed8936;
        background: linear-gradient(135deg, rgba(237, 137, 54, 0.1), rgba(255, 255, 255, 0.95));
    }
    
    .severity-moderate .severity-text {
        color: #ed8936;
        font-size: 3rem;
        font-weight: 700;
        margin: 1rem 0;
        text-shadow: 0 3px 10px rgba(237, 137, 54, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .severity-low {
        border: 3px solid #48bb78;
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(255, 255, 255, 0.95));
    }
    
    .severity-low .severity-text {
        color: #48bb78;
        font-size: 3rem;
        font-weight: 700;
        margin: 1rem 0;
        text-shadow: 0 3px 10px rgba(72, 187, 120, 0.3);
        animation: pulse 2s ease-in-out infinite;
    }
    
    .confidence-display {
        text-align: center;
        padding: 2rem;
    }
    
    .confidence-circle {
        width: 180px;
        height: 180px;
        margin: 0 auto;
        position: relative;
        animation: slideIn 0.8s ease-out;
    }
    
    .confidence-circle svg {
        transform: rotate(-90deg);
    }
    
    .confidence-circle-bg {
        fill: none;
        stroke: #e2e8f0;
        stroke-width: 12;
    }
    
    .confidence-circle-fill {
        fill: none;
        stroke: url(#gradient);
        stroke-width: 12;
        stroke-linecap: round;
        stroke-dasharray: 502;
        stroke-dashoffset: 502;
        animation: fillCircle 2s ease-out forwards;
    }
    
    @keyframes fillCircle {
        to {
            stroke-dashoffset: var(--dash-offset);
        }
    }
    
    .confidence-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .explanation-text {
        font-size: 1.15rem;
        line-height: 1.9;
        color: #4a5568;
        position: relative;
    }
    
    .alternative-box {
        background: linear-gradient(135deg, #f0fff4, #e6ffee);
        border: 3px solid #48bb78;
        border-radius: 20px;
        padding: 1.8rem;
        margin-top: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .alternative-box::before {
        content: '✨';
        position: absolute;
        top: 10px;
        right: 10px;
        font-size: 2rem;
        opacity: 0.3;
    }
    
    .alternative-box:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(72, 187, 120, 0.2);
    }
    
    .alternative-box p {
        color: #2f855a;
        font-size: 1.15rem;
        line-height: 1.7;
        margin: 0;
        font-weight: 500;
    }
    
    .section-icon {
        font-size: 1.8rem;
        margin-right: 0.8rem;
        display: inline-block;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .analyzing-container {
        text-align: center;
        padding: 4rem 2rem;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
    }
    
    .spinner-text {
        font-size: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        margin-top: 1.5rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .pill-icon {
        font-size: 5rem;
        animation: float 2s ease-in-out infinite;
        filter: drop-shadow(0 10px 20px rgba(102, 126, 234, 0.3));
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        padding: 1rem 3rem;
        border-radius: 50px;
        border: none;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
    }
    
    /* Custom textarea styling */
    .stTextArea textarea {
        border-radius: 25px;
        border: 3px solid #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
        backdrop-filter: blur(10px);
        font-size: 1.2rem;
        padding: 1.5rem;
        transition: all 0.3s ease;
        color: #ffffff !important;
        font-weight: 500;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    
    .stTextArea textarea:focus {
        border-color: #764ba2;
        box-shadow: 0 12px 35px rgba(118, 75, 162, 0.4);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        transform: translateY(-2px);
    }
    
    .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        opacity: 1;
        font-weight: 400;
    }
    
    .stTextArea label {
        color: white !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        text-shadow: 0 3px 15px rgba(0,0,0,0.4);
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# Floating medicine background with interactive elements
st.markdown("""
<div class="floating-bg">
    <div class="medicine">💊</div>
    <div class="medicine">💉</div>
    <div class="medicine">🧪</div>
    <div class="medicine">💊</div>
    <div class="medicine">⚕️</div>
    <div class="medicine">💊</div>
    <div class="medicine">🧬</div>
    <div class="medicine">💉</div>
    <div class="medicine">🔬</div>
    <div class="medicine">⚗️</div>
    <div class="dna-helix">🧬</div>
    <div class="dna-helix">🧬</div>
    <div class="blob"></div>
    <div class="blob"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)

st.markdown('<div class="main-title">💊 Drug Interaction Prediction System</div>', unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
Enter medicines in <strong>natural language</strong> to analyze potential interactions<br>
<em>Example: I am taking warfarin and aspirin</em>
</div>
""", unsafe_allow_html=True)

text = st.text_area("🔍 Enter medicines:", height=120, placeholder="Type your medicines here...")

if st.button("🚀 Analyze Interactions", use_container_width=True):
    if not text.strip():
        st.warning("⚠️ Please enter medicine details.")
    else:
        # Animated loading state
        placeholder = st.empty()
        
        with placeholder.container():
            st.markdown("""
            <div class="analyzing-container">
                <div class="pill-icon">💊</div>
                <div class="spinner-text">Analyzing drug interactions...</div>
            </div>
            """, unsafe_allow_html=True)
        
        try:
            res = requests.post(
                "http://127.0.0.1:5000/predict",
                json={"text": text},
                timeout=10
            )
            
            # Clear loading animation
            placeholder.empty()
            
            if res.status_code == 200:
                data = res.json()
                
                # Animated results display
                time.sleep(0.2)
                
                # Detected Drugs
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<h3><span class="section-icon">💊</span>Detected Medicines</h3>', unsafe_allow_html=True)
                drugs_html = "".join([f'<span class="drug-badge">{drug}</span>' for drug in data["drugs"]])
                st.markdown(drugs_html, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                time.sleep(0.1)
                
                # Severity
                severity = data["severity"].lower()
                severity_class = f"severity-{severity}" if severity in ["high", "moderate", "low"] else "severity-card"
                
                severity_icons = {
                    "high": "🔴",
                    "moderate": "🟠", 
                    "low": "🟢"
                }
                severity_icon = severity_icons.get(severity, "⚠️")
                
                st.markdown(f'''
                <div class="severity-card {severity_class}">
                    <h3><span class="section-icon">⚠️</span>Interaction Risk Level</h3>
                    <div class="severity-text">{severity_icon} {data["severity"].upper()}</div>
                    <p style="color: #4a5568; font-size: 1rem; margin-top: 1rem;">
                        This indicates the level of concern for combining these medications
                    </p>
                </div>
                ''', unsafe_allow_html=True)
                
                time.sleep(0.1)
                
                # Confidence Score with animated circular progress
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<h3><span class="section-icon">📊</span>Analysis Confidence</h3>', unsafe_allow_html=True)
                confidence = data['confidence']
                dash_offset = 502 - (502 * confidence / 100)
                
                # Determine confidence level description
                if confidence >= 80:
                    conf_desc = "High confidence - Strong evidence base"
                    conf_color = "#48bb78"
                elif confidence >= 60:
                    conf_desc = "Moderate confidence - Good data support"
                    conf_color = "#ed8936"
                else:
                    conf_desc = "Lower confidence - Limited data available"
                    conf_color = "#e53e3e"
                
                st.markdown(f"""
                <div class="confidence-display">
                    <div class="confidence-circle">
                        <svg width="180" height="180">
                            <defs>
                                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                    <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                                    <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
                                </linearGradient>
                            </defs>
                            <circle class="confidence-circle-bg" cx="90" cy="90" r="80"/>
                            <circle class="confidence-circle-fill" cx="90" cy="90" r="80" 
                                    style="--dash-offset: {dash_offset};"/>
                        </svg>
                        <div class="confidence-text">{confidence}%</div>
                    </div>
                    <p style="color: {conf_color}; font-size: 1rem; font-weight: 600; margin-top: 1rem;">
                        {conf_desc}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                time.sleep(0.1)
                
                # Explanation
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown('<h3><span class="section-icon">📝</span>What This Means</h3>', unsafe_allow_html=True)
                st.markdown(f'<p class="explanation-text">{data["explanation"]}</p>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Recommended Alternative (if exists)
                if "recommended_alternative" in data:
                    time.sleep(0.1)
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<h3><span class="section-icon">💡</span>Safer Alternative</h3>', unsafe_allow_html=True)
                    st.markdown(f'<div class="alternative-box"><p>{data["recommended_alternative"]}</p></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Disclaimer
                time.sleep(0.1)
                st.info(f"ℹ️ {data['disclaimer']}")
            else:
                st.error(f"❌ {res.json().get('error')}")
        
        except Exception as e:
            placeholder.empty()
            st.error(f"❌ Backend error: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # Close content-wrapper