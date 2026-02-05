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
    "gemini-1.5-flash",
    "gemini-2.5-flash-lite",
]


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

def clean_gemini_output(text):

    if not text:
        return text

    # Remove common leakage patterns
    bad_markers = [
        "My Response:",
        "Here's my response:",
        "Here is my response:",
        "I will respond as",
        "Okay, I need to respond",
        "Here's how I'd respond",
        "You:",
        "**My Response:**"
    ]

    cleaned = text

    for marker in bad_markers:
        if marker in cleaned:
            cleaned = cleaned.split(marker)[-1]

    # Remove markdown stars
    cleaned = cleaned.replace("**", "")

    return cleaned.strip()


def generate_gemini_reply(message_text, session_messages):

    history_text = "\n".join(session_messages[-5:])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Message:
{message_text}
"""

    for key in KEYS:

        if not key:
            continue

        try:
            genai.configure(api_key=key)

            for model_name in MODELS:

                try:
                    print(f"Trying KEY + MODEL → {model_name}")

                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)

                    if response.text:
                        print(f"SUCCESS → {model_name}")
                        return clean_gemini_output(response.text.strip())


                except Exception as model_error:
                    print(f"MODEL FAIL → {model_name} → {model_error}")
                    continue

        except Exception as key_error:
            print(f"KEY FAIL → {key_error}")
            continue

    return "Can you explain more about this?"


