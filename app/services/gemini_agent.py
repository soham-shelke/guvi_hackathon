import google.generativeai as genai
from app.services.gemini_key_manager import get_next_key


SYSTEM_PROMPT = """
You are simulating realistic responses as part of a cybersecurity research honeypot system.

Goal:
- Engage with suspected scam messages
- Ask natural clarification questions
- Avoid sharing sensitive info
- Encourage scammer to reveal details

Important:
- Defensive cybersecurity research context
- Do NOT help scammers
- Do NOT provide personal or financial info
- Natural conversational tone allowed

Style:
- Slightly confused
- Concerned about account safety
- Asking verification questions
"""


def generate_gemini_reply(message_text, session_messages):

    history_text = "\n".join(session_messages[-6:])

    prompt = f"""
{SYSTEM_PROMPT}

Conversation:
{history_text}

Message:
{message_text}
"""

    try:
        key = get_next_key()   # ONLY ONE KEY PER REQUEST

        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-3-flash-preview")

        response = model.generate_content(prompt)

        if hasattr(response, "text") and response.text:
            return response.text.strip()

    except Exception as e:
        print("Gemini key failed fast:", e)

    return "Why is my account being blocked? Can you explain?"
