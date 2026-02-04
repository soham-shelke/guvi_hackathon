import os
from dotenv import load_dotenv

load_dotenv()

keys_string = os.getenv("GEMINI_API_KEYS", "")
GEMINI_KEYS = [k.strip() for k in keys_string.split(",") if k.strip()]

current_key_index = 0


def get_next_key():
    global current_key_index

    if not GEMINI_KEYS:
        raise Exception("No Gemini keys found")

    key = GEMINI_KEYS[current_key_index]

    current_key_index = (current_key_index + 1) % len(GEMINI_KEYS)

    return key
