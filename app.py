import streamlit as st
from core.llm import get_triage_decision
from core.rules import rule_engine
from core.scoring import risk_score

# -----------------------
# Page Config
# -----------------------
st.set_page_config(page_title="AI Triage Assistant", layout="centered")

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("🔑 Settings")
api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# -----------------------
# Title
# -----------------------
st.title("🏥 AI Triage Decision Assistant (MVP)")
st.markdown("Hybrid AI system combining rules, scoring, and LLM reasoning")

# -----------------------
# Inputs
# -----------------------
st.subheader("Patient Information")

age = st.number_input("Age", 0, 120, 50)

symptoms = st.text_input(
    "Symptoms (comma separated)",
    placeholder="chest pain, shortness of breath"
)

bp = st.text_input("Blood Pressure (e.g., 120/80)")

hr = st.number_input("Heart Rate", 0, 200, 80)

spo2 = st.number_input("Oxygen Saturation (%)", 0, 100, 98)

history = st.text_input("Medical History")

arrival = st.selectbox("Arrival Mode", ["walk-in", "ambulance"])

# -----------------------
# Validation
# -----------------------
def validate_input(data):
    if not data["symptoms"]:
        return False, "Symptoms required"
    if data["spo2"] < 0 or data["spo2"] > 100:
        return False, "Invalid SpO2"
    return True, ""

# -----------------------
# Evaluate
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

    valid, msg = validate_input(data)
    if not valid:
        st.error(msg)
        st.stop()

    # -----------------------
    # Rules + Score
    # -----------------------
    flags = rule_engine(data)
    score = risk_score(flags)

    st.subheader("🔍 Intermediate Signals")
    st.write("Flags:", flags)
    st.write("Risk Score:", f"{score}%")

    # -----------------------
    # LLM
    # -----------------------
    if not api_key:
        st.error("Enter API key in sidebar")
    else:
        with st.spinner("Running AI analysis..."):
            result = get_triage_decision(api_key, data, score, flags)

        if "error" in result:
            st.error("LLM failed")
            st.write(result)

        else:
            st.success(f"Model used: {result['model_used']}")

            output = result["output"]

            st.subheader("🧠 AI Recommendation")

            if isinstance(output, dict):
                st.json(output)

                # Highlight critical
                if "priority_level" in output:
                    if "Level 1" in output["priority_level"]:
                        st.error("⚠ Critical Case - Immediate Attention")

            else:
                st.write(output)

# -----------------------
# Human Override
# -----------------------
st.subheader("👨‍⚕️ Human Override")

override = st.text_input("Enter clinician override")

if override:
    st.success("Override recorded")

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption("This is a clinical decision-support tool. Final decisions rest with medical professionals.")