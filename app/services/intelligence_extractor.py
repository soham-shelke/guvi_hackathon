import re

def normalize_phone(phone):
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = phone[1:]
    if phone.startswith("+91"):
        return phone
    if len(phone) == 10:
        return "+91" + phone
    return phone


def extract_intelligence(message_text, session):

    if "intelligence" not in session:
        session["intelligence"] = {
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }

    # ===== HIGH CAPTURE UPI =====
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"

    # ===== FULL PHONE CAPTURE =====
    phone_pattern = r"(?:\+91[-\s]?|0)?[6-9]\d{9}"

    # ===== LINKS =====
    link_pattern = r"(https?://[^\s]+)"

    new_upi = re.findall(upi_pattern, message_text)
    new_phone_raw = re.findall(phone_pattern, message_text)
    new_links = re.findall(link_pattern, message_text)

    # Normalize phone numbers
    new_phone = [normalize_phone(p) for p in new_phone_raw]

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
