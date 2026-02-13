import re


def extract_intelligence(message_text, session):

    # ========================
    # SAFE INTELLIGENCE INIT
    # ========================
    if "intelligence" not in session:
        session["intelligence"] = {}

    intel = session["intelligence"]

    intel.setdefault("upiIds", [])
    intel.setdefault("phoneNumbers", [])
    intel.setdefault("phishingLinks", [])
    intel.setdefault("suspiciousKeywords", [])
    intel.setdefault("bankAccounts", [])

    msg_lower = message_text.lower()

    # ========================
    # UPI
    # ========================
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"
    new_upi = re.findall(upi_pattern, message_text)

    # ========================
    # PHONE → ONLY + NUMBERS
    # ========================
    phone_pattern = r"\+\d{10,15}"
    phones = re.findall(phone_pattern, message_text)

    # ========================
    # REMOVE PHONES FROM TEXT
    # ========================
    cleaned_text = message_text
    for p in phones:
        cleaned_text = cleaned_text.replace(p, " ")

    # ========================
    # BANK ACCOUNTS → DIGITS ONLY
    # ========================
    bank_pattern = r"\b\d{10,18}\b"
    bank_accounts = re.findall(bank_pattern, cleaned_text)

    # ========================
    # LINKS
    # ========================
    link_pattern = r"(https?://[^\s]+|www\.[^\s]+)"
    links = re.findall(link_pattern, message_text)

    # ========================
    # KEYWORDS
    # ========================
    keyword_list = [
        "urgent", "verify", "otp", "blocked", "suspended",
        "immediate", "send otp", "account blocked",
        "security alert", "verify now", "limited time",
        "frozen", "suspend", "click link"
    ]

    found_keywords = [k for k in keyword_list if k in msg_lower]

    # ========================
    # STORE UNIQUE
    # ========================
    intel["upiIds"] = list(set(intel["upiIds"] + new_upi))
    intel["phoneNumbers"] = list(set(intel["phoneNumbers"] + phones))
    intel["phishingLinks"] = list(set(intel["phishingLinks"] + links))
    intel["bankAccounts"] = list(set(intel["bankAccounts"] + bank_accounts))
    intel["suspiciousKeywords"] = list(set(intel["suspiciousKeywords"] + found_keywords))

    print("INTELLIGENCE:", intel)
