import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2")
]

MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash"
]

FALLBACK_REPLY = "Can you explain more about this?"

SYSTEM_PROMPT = """
You are part of a cybersecurity honeypot interacting with a scammer.

Return ONLY the SMS reply text.
No explanations.
No analysis.
No roleplay formatting.
No markdown.

CRITICAL SECURITY RULES:
NEVER generate:
- OTP numbers
- PIN numbers
- CVV numbers
- Bank account numbers
- UPI PIN
- Any numeric verification codes

If scammer asks for OTP or PIN:
You must refuse politely and ask for alternative verification.
"""


def generate_gemini_reply(message_text, session_messages):

    history_text = "\n".join(session_messages[-5:])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Message:
{message_text}
"""

    for model in MODELS:
        for key in KEYS:

            if not key:
                continue

            try:
                print(f"Trying MODEL + KEY → {model}")

                genai.configure(api_key=key)
                model_obj = genai.GenerativeModel(model)

                response = model_obj.generate_content(prompt)

                if response and response.text:
                    print(f"SUCCESS → {model}")
                    return response.text.strip()

            except Exception as e:
                print(f"FAIL → {model} → {e}")

    return FALLBACK_REPLY
