import re

def extract_intelligence(message_text, session):

    if "intelligence" not in session:
        session["intelligence"] = {
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }

    # ===== HIGH CAPTURE UPI REGEX =====
    # Captures most payment handles including fake scam domains
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"

    # ===== PHONE REGEX (KEEPS FULL NUMBER) =====
    phone_pattern = r"(?:\+91[-\s]?)?[6-9]\d{9}"

    # ===== LINK REGEX =====
    link_pattern = r"(https?://[^\s]+)"

    new_upi = re.findall(upi_pattern, message_text)
    new_phone = re.findall(phone_pattern, message_text)
    new_links = re.findall(link_pattern, message_text)

    session["intelligence"]["upiIds"] = list(
        set(session["intelligence"]["upiIds"] + new_upi)
    )

    session["intelligence"]["phoneNumbers"] = list(
        set(session["intelligence"]["phoneNumbers"] + new_phone)
    )

    session["intelligence"]["phishingLinks"] = list(
        set(session["intelligence"]["phishingLinks"] + new_links)
    )

    print("INTELLIGENCE:", session["intelligence"])
