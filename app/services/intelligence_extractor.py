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

    # ===== SAFE SESSION STRUCTURE INIT =====
    if "intelligence" not in session:
        session["intelligence"] = {
            "bankAccounts": [],
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": [],
            "suspiciousKeywords": []
        }

    # Backward safety (if old session exists)
    session["intelligence"].setdefault("bankAccounts", [])
    session["intelligence"].setdefault("upiIds", [])
    session["intelligence"].setdefault("phoneNumbers", [])
    session["intelligence"].setdefault("phishingLinks", [])
    session["intelligence"].setdefault("suspiciousKeywords", [])

    # ===== PATTERNS =====

    # UPI
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"

    # Phone
    phone_pattern = r"(?:\+91[-\s]?|0)?[6-9]\d{9}"

    # Links
    link_pattern = r"(https?://[^\s]+)"

    # Bank Accounts (Generic Long Numbers)
    bank_pattern = r"\b\d{9,18}\b"

    # Suspicious Keywords
    suspicious_words = [
        "urgent",
        "verify",
        "blocked",
        "suspended",
        "immediate",
        "otp",
        "verify now",
        "account blocked",
        "payment required",
        "send money"
    ]

    # ===== EXTRACTION =====

    new_upi = re.findall(upi_pattern, message_text)
    new_phone_raw = re.findall(phone_pattern, message_text)
    new_links = re.findall(link_pattern, message_text)
    new_bank = re.findall(bank_pattern, message_text)

    # Normalize phone numbers
    new_phone = [normalize_phone(p) for p in new_phone_raw]

    # Keyword detection
    new_keywords = [
        word for word in suspicious_words
        if word.lower() in message_text.lower()
    ]

    # ===== MERGE INTO SESSION =====

    session["intelligence"]["upiIds"] = list(
        set(session["intelligence"]["upiIds"] + new_upi)
    )

    session["intelligence"]["phoneNumbers"] = list(
        set(session["intelligence"]["phoneNumbers"] + new_phone)
    )

    session["intelligence"]["phishingLinks"] = list(
        set(session["intelligence"]["phishingLinks"] + new_links)
    )

    session["intelligence"]["bankAccounts"] = list(
        set(session["intelligence"]["bankAccounts"] + new_bank)
    )

    session["intelligence"]["suspiciousKeywords"] = list(
        set(session["intelligence"]["suspiciousKeywords"] + new_keywords)
    )

    print("INTELLIGENCE:", session["intelligence"])
