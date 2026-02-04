import re
from app.services.gemini_intelligence import gemini_extract_intelligence


# ==============================
# REGEX EXTRACTION (FAST LAYER)
# ==============================
def extract_regex_intelligence(message_text):

    upi_ids = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", message_text)

    phone_numbers = re.findall(
        r"(?:\+91[-\s]?|0)?[6-9]\d{9}",
        message_text
    )

    links = re.findall(
        r"(https?://[^\s]+)",
        message_text
    )

    return {
        "upiIds": upi_ids,
        "phoneNumbers": phone_numbers,
        "phishingLinks": links
    }


# ==============================
# HYBRID EXTRACTION (MAIN)
# ==============================
def extract_intelligence(message_text, session):

    # REGEX FIRST (FAST + SAFE)
    regex_data = extract_regex_intelligence(message_text)

    # GEMINI SECOND (SMART)
    gemini_data = gemini_extract_intelligence(message_text)

    merged = {
        "upiIds": list(set(regex_data.get("upiIds", []) + gemini_data.get("upiIds", []))),
        "phoneNumbers": list(set(regex_data.get("phoneNumbers", []) + gemini_data.get("phoneNumbers", []))),
        "phishingLinks": list(set(regex_data.get("phishingLinks", []) + gemini_data.get("phishingLinks", []))),
        "bankNames": gemini_data.get("bankNames", []),
        "scamType": gemini_data.get("scamType", "unknown"),
        "sensitiveDataRequested": gemini_data.get("sensitiveDataRequested", []),
        "urgencyLevel": gemini_data.get("urgencyLevel", "unknown")
    }

    session["intelligence"] = merged

    print("HYBRID INTELLIGENCE:", merged)
