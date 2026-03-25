import streamlit as st
from core.llm import get_triage_decision
from core.rules import rule_engine
from core.scoring import risk_score

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="AI Triage Assistant", layout="centered")

# -----------------------
# Sidebar (API Key)
# -----------------------
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# -----------------------
# Title
# -----------------------
st.title("🏥 AI Triage Decision Assistant (MVP)")
st.markdown("Hybrid AI system combining rules, risk scoring, and LLM reasoning")

# -----------------------
# Input Form
# -----------------------
st.subheader("Patient Information")

age = st.number_input("Age", min_value=0, max_value=120, value=50)

symptoms = st.text_input(
    "Symptoms (comma separated)",
    placeholder="e.g., chest pain, shortness of breath"
)

bp = st.text_input("Blood Pressure (e.g., 120/80)")

hr = st.number_input("Heart Rate", min_value=0, max_value=200, value=80)

spo2 = st.number_input("Oxygen Saturation (%)", min_value=0, max_value=100, value=98)

history = st.text_input(
    "Medical History",
    placeholder="e.g., hypertension, diabetes"
)

arrival = st.selectbox("Arrival Mode", ["walk-in", "ambulance"])

# -----------------------
# Input Validation
# -----------------------
def validate_input(data):
    if not data["symptoms"]:
        return False, "Symptoms are required"
    if data["spo2"] < 0 or data["spo2"] > 100:
        return False, "Invalid oxygen saturation"
    return True, ""

# -----------------------
# Evaluate Button
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

    # Validate input
    is_valid, error_msg = validate_input(data)
    if not is_valid:
        st.error(error_msg)
        st.stop()

    # -----------------------
    # Rules + Scoring
    # -----------------------
    flags = rule_engine(data)
    score = risk_score(flags)

    st.subheader("🔍 Intermediate Signals")
    st.write("**Flags:**", flags)
    st.write("**Risk Score:**", f"{score}%")

    # -----------------------
    # LLM Call
    # -----------------------
    if not api_key:
        st.error("Please enter Gemini API key in sidebar")
    else:
        with st.spinner("Analyzing patient data..."):

            result = get_triage_decision(api_key, data, score, flags)

        # -----------------------
        # Output Handling
        # -----------------------
        if "error" in result:
            st.error("LLM processing failed")
            st.write(result)

        else:
            st.success(f"Model used: {result['model_used']}")

            output = result["output"]

            st.subheader("🧠 AI Recommendation")

            if isinstance(output, dict):
                st.json(output)

                # Highlight critical cases
                if "priority_level" in output and "Level 1" in output["priority_level"]:
                    st.error("⚠ High Priority Case - Immediate Attention Required")

            else:
                st.write(output)

# -----------------------
# Human Override Section
# -----------------------
st.subheader("👨‍⚕️ Human Override")

override = st.text_input("Enter clinician decision (optional)")

if override:
    st.success("Override recorded (for audit/logging in production)")

# -----------------------
# Footer (Safety Note)
# -----------------------
st.markdown("---")
st.caption(
    "This is a decision-support tool. Final clinical decisions must be made by qualified medical professionals."
)