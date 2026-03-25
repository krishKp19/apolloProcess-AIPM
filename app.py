import streamlit as st
import google.generativeai as genai
import json

# -----------------------
# Sidebar for API Key
# -----------------------
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

if api_key:
    genai.configure(api_key=api_key)

# -----------------------
# UI
# -----------------------
st.title("AI Triage Decision Assistant (MVP)")

age = st.number_input("Age", 0, 120, 50)
symptoms = st.text_input("Symptoms (comma separated)")
bp = st.text_input("Blood Pressure (e.g., 120/80)")
hr = st.number_input("Heart Rate", 0, 200, 80)
spo2 = st.number_input("Oxygen Saturation", 0, 100, 98)
history = st.text_input("Medical History")
arrival = st.selectbox("Arrival Mode", ["walk-in", "ambulance"])

# -----------------------
# Rules Engine
# -----------------------
def rule_engine(data):
    flags = []

    if data["spo2"] < 92:
        flags.append("low_oxygen")

    if "chest pain" in data["symptoms"]:
        flags.append("cardiac_risk")

    if data["hr"] > 110:
        flags.append("tachycardia")

    return flags

# -----------------------
# Risk Score
# -----------------------
def risk_score(flags):
    score = 0

    if "low_oxygen" in flags:
        score += 40
    if "cardiac_risk" in flags:
        score += 30
    if "tachycardia" in flags:
        score += 20

    return min(score, 100)

# -----------------------
# Generate Output
# -----------------------
if st.button("Evaluate Patient"):

    data = {
        "age": age,
        "symptoms": symptoms.lower(),
        "bp": bp,
        "hr": hr,
        "spo2": spo2,
        "history": history,
        "arrival": arrival
    }

    flags = rule_engine(data)
    score = risk_score(flags)

    st.subheader("Intermediate Signals")
    st.write("Flags:", flags)
    st.write("Risk Score:", score)

    if not api_key:
        st.error("Please enter API key")
    else:
        model = genai.GenerativeModel("gemini-pro")

        prompt = f"""
You are a clinical triage support assistant.

STRICT RULES:
- Do NOT provide diagnosis
- Do NOT replace clinician judgment
- Base reasoning ONLY on provided data

Patient Data:
{data}

Risk Score: {score}
Flags: {flags}

Return ONLY valid JSON:
{{
  "priority_level": "",
  "risk_score": "",
  "reasoning": "",
  "recommended_action": ""
}}
"""

        response = model.generate_content(prompt)

        try:
            output = json.loads(response.text)
            st.subheader("AI Recommendation")
            st.json(output)
        except:
            st.error("Invalid response format")
            st.write(response.text)

# -----------------------
# Human Override
# -----------------------
st.subheader("Human Override")
override = st.text_input("Enter clinician decision (optional)")
if override:
    st.success("Override recorded")