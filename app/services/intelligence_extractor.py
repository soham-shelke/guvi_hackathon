import re


def normalize_phone(phone):
    phone = phone.replace(" ", "").replace("-", "")

    if phone.startswith("+"):
        return phone

    if phone.startswith("0"):
        phone = phone[1:]

    if len(phone) >= 10 and phone.isdigit():
        return "+" + phone

    return phone


def extract_intelligence(message_text, session):

    # ✅ SAFE INITIALIZATION (Prevents Missing Key Errors)
    if "intelligence" not in session:
        session["intelligence"] = {}

    intelligence = session["intelligence"]

    intelligence.setdefault("upiIds", [])
    intelligence.setdefault("phoneNumbers", [])
    intelligence.setdefault("phishingLinks", [])
    intelligence.setdefault("suspiciousKeywords", [])
    intelligence.setdefault("bankAccounts", [])
    intelligence.setdefault("emails", [])

    # ========================
    # PATTERNS
    # ========================

    upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"

    phone_pattern = r"\+\d{10,15}"

    bank_pattern = r"\b\d{9,18}\b"

    link_pattern = r"(https?://[^\s]+|www\.[^\s]+)"

    email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

    keyword_list = [
        "urgent",
        "verify",
        "otp",
        "blocked",
        "suspended",
        "immediate",
        "account blocked",
        "verify now"
    ]

    # ========================
    # EXTRACTION
    # ========================

    upis = re.findall(upi_pattern, message_text)
    phones_raw = re.findall(phone_pattern, message_text)
    banks = re.findall(bank_pattern, message_text)
    links = re.findall(link_pattern, message_text)
    emails = re.findall(email_pattern, message_text)

    phones = [normalize_phone(p) for p in phones_raw]

    # Remove phone digits from bank accounts
    clean_banks = []
    for b in banks:
        if not any(b in p for p in phones):
            clean_banks.append(b)

    found_keywords = []
    lower_msg = message_text.lower()
    for kw in keyword_list:
        if kw in lower_msg:
            found_keywords.append(kw)

    # ========================
    # MERGE INTO SESSION
    # ========================

    intelligence["upiIds"] = list(set(intelligence["upiIds"] + upis))
    intelligence["phoneNumbers"] = list(set(intelligence["phoneNumbers"] + phones))
    intelligence["bankAccounts"] = list(set(intelligence["bankAccounts"] + clean_banks))
    intelligence["phishingLinks"] = list(set(intelligence["phishingLinks"] + links))
    intelligence["emails"] = list(set(intelligence["emails"] + emails))
    intelligence["suspiciousKeywords"] = list(set(intelligence["suspiciousKeywords"] + found_keywords))

    print("INTELLIGENCE:", intelligence)
