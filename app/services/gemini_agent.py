import google.generativeai as genai
import os
import time

KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
]

MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.0-flash"
]

FAST_FALLBACK_REPLIES = [
    "I didn’t get OTP yet, can you resend?",
    "Which account is this regarding?",
    "I am not understanding, can you explain?",
    "Is this from bank or support team?"
]

SYSTEM_PROMPT = """
You are a worried customer talking to support.
Return only SMS reply.
Never send OTP.
Never confirm payment.
Keep message short.
"""


def generate_gemini_reply(message_text, session_messages):

    history = "\n".join(session_messages[-4:])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history}

Message:
{message_text}
"""

    start_time = time.time()

    for key in KEYS:
        if not key:
            continue

        try:
            genai.configure(api_key=key)

            for model_name in MODELS:

                # 🔥 HARD LATENCY LIMIT
                if time.time() - start_time > 3.5:
                    return FAST_FALLBACK_REPLIES[0]

                try:
                    model = genai.GenerativeModel(model_name)

                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.4,
                            "max_output_tokens": 60
                        }
                    )

                    if response.text:
                        text = response.text.strip()

                        # Safety filter
                        if "otp is" in text.lower():
                            return FAST_FALLBACK_REPLIES[1]

                        return text

                except Exception:
                    continue

        except Exception:
            continue

    return FAST_FALLBACK_REPLIES[2]