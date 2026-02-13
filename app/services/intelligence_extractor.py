import re


def normalize_phone(phone):
    phone = phone.replace(" ", "").replace("-", "")

    if phone.startswith("00"):
        phone = "+" + phone[2:]

    if phone.startswith("0") and len(phone) > 10:
        phone = phone[1:]

    if phone.startswith("+"):
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
            "suspiciousKeywords": [],
            "bankAccounts": []
        }

    msg = message_text.lower()

    # ========================
    # UPI
    # ========================
    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"
    new_upi = re.findall(upi_pattern, message_text)

    # ========================
    # BANK ACCOUNTS (FIRST)
    # ========================
    bank_pattern = r"\b\d{12,18}\b"
    bank_accounts = re.findall(bank_pattern, message_text)

    # Remove bank accounts from message for phone detection
    cleaned_for_phone = message_text
    for acc in bank_accounts:
        cleaned_for_phone = cleaned_for_phone.replace(acc, " ")

    # ========================
    # GLOBAL PHONE DETECTION
    # ========================
    phone_pattern = r"(?:\+?\d{1,3}[-\s]?)?[6-9]\d{9}"
    phone_raw = re.findall(phone_pattern, cleaned_for_phone)

    phones = [normalize_phone(p) for p in phone_raw]

    # ========================
    # LINKS (http + www)
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

    found_keywords = [k for k in keyword_list if k in msg]

    # ========================
    # STORE UNIQUE
    # ========================
    intel = session["intelligence"]

    intel["upiIds"] = list(set(intel["upiIds"] + new_upi))
    intel["phoneNumbers"] = list(set(intel["phoneNumbers"] + phones))
    intel["phishingLinks"] = list(set(intel["phishingLinks"] + links))
    intel["bankAccounts"] = list(set(intel["bankAccounts"] + bank_accounts))
    intel["suspiciousKeywords"] = list(set(intel["suspiciousKeywords"] + found_keywords))

    print("INTELLIGENCE:", intel)
