import re


# =============================
# PHONE NORMALIZATION (GLOBAL SAFE)
# =============================

def normalize_phone(phone):

    if not phone:
        return phone

    phone = phone.replace(" ", "").replace("-", "")

    # Already international format
    if phone.startswith("+"):
        return phone

    # India fallback
    if len(phone) == 10 and phone[0] in "6789":
        return "+91" + phone

    return phone


# =============================
# MAIN EXTRACTION FUNCTION
# =============================

def extract_intelligence(message_text, session):

    try:

        # =============================
        # SAFE SESSION INIT
        # =============================

        if "intelligence" not in session:
            session["intelligence"] = {}

        session["intelligence"].setdefault("upiIds", [])
        session["intelligence"].setdefault("phoneNumbers", [])
        session["intelligence"].setdefault("phishingLinks", [])
        session["intelligence"].setdefault("suspiciousKeywords", [])
        session["intelligence"].setdefault("bankAccounts", [])

        # =============================
        # PATTERNS
        # =============================

        # UPI
        upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z0-9._-]{2,}\b"

        # GLOBAL PHONE
        phone_pattern = r"(?:\+?\d{1,3})?[ -]?[6-9]\d{9}"

        # LINKS
        link_pattern = r"(https?://[^\s]+|www\.[^\s]+)"

        # BANK ACCOUNT (12–18 digits)
        bank_pattern = r"\b\d{12,18}\b"

        # KEYWORDS
        keywords = [
            "urgent",
            "verify",
            "immediate",
            "otp",
            "blocked",
            "suspended",
            "freeze",
            "limited time",
            "act now",
            "security alert",
            "payment request",
            "upi pin",
            "send otp"
        ]

        # =============================
        # EXTRACT RAW
        # =============================

        new_upi = re.findall(upi_pattern, message_text)
        new_phone_raw = re.findall(phone_pattern, message_text)
        new_links = re.findall(link_pattern, message_text)
        new_bank_raw = re.findall(bank_pattern, message_text)

        # Normalize phones
        new_phone = [normalize_phone(p) for p in new_phone_raw]

        # Keyword detection
        lower_text = message_text.lower()
        found_keywords = [k for k in keywords if k in lower_text]

        # =============================
        # BANK FILTERING (ANTI PHONE OVERLAP)
        # =============================

        filtered_bank = []

        phone_digits = [p.replace("+", "") for p in new_phone]

        for b in new_bank_raw:

            # Skip if bank contains phone digits
            if any(pd in b for pd in phone_digits):
                continue

            # Skip India country code phone style numbers
            if b.startswith("91") and len(b) == 12:
                continue

            filtered_bank.append(b)

        # =============================
        # MERGE INTO SESSION (DEDUP SAFE)
        # =============================

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
            set(session["intelligence"]["bankAccounts"] + filtered_bank)
        )

        session["intelligence"]["suspiciousKeywords"] = list(
            set(session["intelligence"]["suspiciousKeywords"] + found_keywords)
        )

        print("INTELLIGENCE:", session["intelligence"])

    except Exception as e:
        print("Extraction error:", e)
