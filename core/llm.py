import google.generativeai as genai
import json
import re


def get_model(api_key):
    """
    Dynamically fetch available Gemini models and fallback safely
    """
    genai.configure(api_key=api_key)

    fallback_models = [
        "models/gemini-1.5-flash",
        "models/gemini-1.5-pro",
        "models/gemini-pro"
    ]

    try:
        models = genai.list_models()

        available_models = [
            m.name for m in models
            if "generateContent" in m.supported_generation_methods
        ]

        gemini_models = [m for m in available_models if "gemini" in m]

        if gemini_models:
            return genai.GenerativeModel(gemini_models[0]), gemini_models[0]
        else:
            return genai.GenerativeModel(fallback_models[0]), fallback_models[0]

    except Exception:
        return genai.GenerativeModel(fallback_models[0]), fallback_models[0]


def clean_json_response(text):
    """
    Cleans Gemini response (removes ```json blocks)
    """
    text = re.sub(r"```json|```", "", text).strip()
    return text


def get_triage_decision(api_key, data, score, flags):
    """
    Main function to generate triage output
    """
    try:
        model, model_name = get_model(api_key)
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

        cleaned = clean_json_response(response.text)

        try:
            parsed = json.loads(cleaned)
        except:
            parsed = {"raw_response": cleaned}

        return {
            "model_used": model_name,
            "output": parsed
        }

    except Exception as e:
        return {
            "model_used": model_name,
            "error": str(e)
        }