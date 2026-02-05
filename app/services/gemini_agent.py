import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# ===== KEYS (Auto filter empty) =====
KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
]

KEYS = [k for k in KEYS if k]

# ===== MODEL PRIORITY (BEST → FALLBACK) =====
MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash"
]

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = """
You are part of a cybersecurity research honeypot system interacting with a suspected scammer.

Goal:
Extract scam intelligence naturally while acting like normal worried customer.

CRITICAL OUTPUT RULES:
Return ONLY the message that the customer would send to the scammer.
Do NOT explain reasoning.
Do NOT describe what you are doing.
Do NOT include phrases like "My Response", "Here is my response", or roleplay markers.
Do NOT include markdown formatting.
Do NOT include analysis or planning text.
Write ONLY the final SMS-style reply message.
"""


# ===== OUTPUT CLEANER =====
def clean_gemini_output(text):

    if not text:
        return text

    bad_markers = [
        "My Response:",
        "Here's my response:",
        "Here is my response:",
        "I will respond as",
        "Okay, I need to respond",
        "Here's how I'd respond",
        "You:",
        "**My Response:**",
        "---"
    ]

    cleaned = text

    for marker in bad_markers:
        if marker in cleaned:
            cleaned = cleaned.split(marker)[-1]

    cleaned = cleaned.replace("**", "")

    return cleaned.strip()


# ===== MAIN GENERATION FUNCTION =====
def generate_gemini_reply(message_text, session_messages):

    history_text = "\n".join(session_messages[-5:])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Message:
{message_text}
"""

    # ===== MODEL FIRST → KEY FAILOVER =====
    for model_name in MODELS:

        for key in KEYS:

            try:
                print(f"Trying MODEL + KEY → {model_name} | {key[:6]}...")

                genai.configure(api_key=key)

                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)

                if response and response.text:
                    print(f"SUCCESS → {model_name}")
                    return clean_gemini_output(response.text.strip())

            except Exception as e:
                print(f"FAIL → {model_name} | {key[:6]} → {e}")
                continue

    # ===== FINAL FALLBACK =====
    return "Can you explain more about this?"
