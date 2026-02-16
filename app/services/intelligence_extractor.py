import re


# =============================
# NORMALIZATION HELPERS
# =============================

def normalize_phone(phone):
    phone = phone.replace(" ", "").replace("-", "")

    if phone.startswith("+"):
        return phone

    return None


def is_likely_bank_account(number):
    """
    Bank accounts usually:
    - 9 to 18 digits
    - No +
    """
    if number.startswith("+"):
        return False

    return 9 <= len(number) <= 18


# =============================
# MAIN EXTRACTION FUNCTION
# =============================

def extract_intelligence(message_text, session):

    try:

        # ===== SAFE INIT =====
        if "intelligence" not in session:
            session["intelligence"] = {}

        intelligence = session["intelligence"]

        intelligence.setdefault("upiIds", [])
        intelligence.setdefault("phoneNumbers", [])
        intelligence.setdefault("phishingLinks", [])
        intelligence.setdefault("suspiciousKeywords", [])
        intelligence.setdefault("bankAccounts", [])
        intelligence.setdefault("emails", [])

        text_lower = message_text.lower()

        # =============================
        # UPI IDS
        # =============================
        upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"
        upis = re.findall(upi_pattern, message_text)

        # =============================
        # EMAILS
        # =============================
        email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
        emails = re.findall(email_pattern, message_text)

        # Remove emails from UPI false positives
        upis = [u for u in upis if u not in emails]

        # =============================
        # LINKS (http + www)
        # =============================
        link_pattern = r"(https?://[^\s]+|www\.[^\s]+)"
        links = re.findall(link_pattern, message_text)

        # =============================
        # PHONE NUMBERS (ONLY if starts with +)
        # =============================
        phone_pattern = r"\+\d{8,15}"
        phones = re.findall(phone_pattern, message_text)

        phones = [normalize_phone(p) for p in phones if normalize_phone(p)]

        # =============================
        # GENERIC NUMBER CAPTURE
        # =============================
        number_pattern = r"\b\d{9,18}\b"
        numbers = re.findall(number_pattern, message_text)

        bank_accounts = [
            n for n in numbers
            if is_likely_bank_account(n)
        ]

        # =============================
        # KEYWORDS
        # =============================
        keyword_list = [
            "otp",
            "verify",
            "urgent",
            "immediate",
            "blocked",
            "suspended",
            "kyc",
            "update",
            "click link",
            "security alert",
            "limited time",
            "act now"
        ]

        keywords_found = [
            k for k in keyword_list
            if k in text_lower
        ]

        # =============================
        # MERGE UNIQUE
        # =============================
        intelligence["upiIds"] = list(set(intelligence["upiIds"] + upis))
        intelligence["emails"] = list(set(intelligence["emails"] + emails))
        intelligence["phoneNumbers"] = list(set(intelligence["phoneNumbers"] + phones))
        intelligence["phishingLinks"] = list(set(intelligence["phishingLinks"] + links))
        intelligence["bankAccounts"] = list(set(intelligence["bankAccounts"] + bank_accounts))
        intelligence["suspiciousKeywords"] = list(set(intelligence["suspiciousKeywords"] + keywords_found))

        print("INTELLIGENCE:", intelligence)

    except Exception as e:
        print("Extraction error:", e)