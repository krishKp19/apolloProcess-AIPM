import google.generativeai as genai
import json

def get_model():
    """
    Automatically selects a working Gemini model with fallback
    """
    model_candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]

    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            # lightweight test call
            model.generate_content("test", request_options={"timeout": 5})
            return model, model_name
        except Exception:
            continue

    raise Exception("No available Gemini models found")


def get_triage_decision(api_key, data, score, flags):
    """
    Main function to get triage decision from Gemini
    """
    genai.configure(api_key=api_key)

    try:
        model, model_name = get_model()
    except Exception as e:
        return {
            "error": "Model selection failed",
            "details": str(e)
        }

    prompt = f"""
You are a clinical triage support assistant.

STRICT RULES:
- Do NOT provide diagnosis
- Do NOT replace clinician judgment
- Use ONLY provided structured data

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

    try:
        response = model.generate_content(prompt)

        # Try parsing JSON safely
        try:
            parsed = json.loads(response.text)
        except:
            parsed = {"raw_response": response.text}

        return {
            "model_used": model_name,
            "output": parsed
        }

    except Exception as e:
        return {
            "model_used": model_name,
            "error": str(e)
        }