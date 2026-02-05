import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
]

key_index = 0


def get_next_key():
    global key_index

    key = GEMINI_KEYS[key_index]

    key_index = (key_index + 1) % len(GEMINI_KEYS)

    return key
