import google.generativeai as genai
import json
from app.services.gemini_key_manager import get_next_key


INTEL_PROMPT = """
You are a cybersecurity intelligence extraction engine.

Extract scam intelligence from the message.

Return ONLY JSON. No explanation.

Fields:
upiIds: array of UPI IDs
phoneNumbers: array of phone numbers
phishingLinks: array of URLs
bankNames: array of bank names mentioned
scamType: string (phishing / vishing / payment scam / account takeover / unknown)
sensitiveDataRequested: array (OTP, PIN, CVV, Password, Account Number, Aadhaar, etc)
urgencyLevel: low / medium / high

If none found → return empty arrays or "unknown".
"""


def gemini_extract_intelligence(message_text):

    prompt = f"""
{INTEL_PROMPT}

Message:
{message_text}

Return valid JSON only.
"""

    try:
        key = get_next_key()
        genai.configure(api_key=key)

        model = genai.GenerativeModel("gemini-3-flash-preview")

        response = model.generate_content(prompt)

        text = response.text.strip()

        text = text.replace("```json", "").replace("```", "")

        return json.loads(text)

    except Exception as e:
        print("Gemini intel extraction error:", e)

        return {
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "bankNames": [],
            "scamType": "unknown",
            "sensitiveDataRequested": [],
            "urgencyLevel": "unknown"
        }
