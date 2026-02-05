import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
]

MODELS = [
    "gemini-3-flash",
    "gemini-2.5-flash-lite"
]


SYSTEM_PROMPT = """
You are part of a cybersecurity research honeypot system interacting with a suspected scammer.

Goal:
Extract scam intelligence naturally while acting like normal worried customer.
"""


def try_generate(key, prompt):

    genai.configure(api_key=key)

    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            if response.text:
                return response.text.strip()

        except Exception as e:
            print("Model failed:", model_name, e)

    return None


def generate_gemini_reply(message_text, session_messages):

    history_text = "\n".join(session_messages[-5:])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Message:
{message_text}
"""

    # ===== FAILOVER LOGIC =====
    for key in KEYS:
        if not key:
            continue

        try:
            reply = try_generate(key, prompt)
            if reply:
                return reply

        except Exception as e:
            print("Key failed:", e)

    return "Can you explain more about this?"
