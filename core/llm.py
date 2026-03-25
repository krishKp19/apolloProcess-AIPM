import google.generativeai as genai
import json

def get_triage_decision(api_key, data, score, flags):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
You are a clinical triage support assistant.

STRICT RULES:
- Do NOT provide diagnosis
- Do NOT replace clinician judgment
- Use only provided data

Patient Data:
{data}

Risk Score: {score}
Flags: {flags}

Return ONLY JSON:
{{
  "priority_level": "",
  "risk_score": "",
  "reasoning": "",
  "recommended_action": ""
}}
"""

    response = model.generate_content(prompt)

    try:
        return json.loads(response.text)
    except:
        return {"error": response.text}