import re


def normalize_phone(phone):
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("+"):
        return phone
    if len(phone) >= 10:
        return phone
    return phone


def extract_intelligence(message_text, session):

    try:

        if "intelligence" not in session:
            session["intelligence"] = {
                "upiIds": [],
                "phoneNumbers": [],
                "phishingLinks": [],
                "suspiciousKeywords": [],
                "bankAccounts": [],
                "emails": []   # ✅ NEW FIELD
            }

        intel = session["intelligence"]

        # =========================
        # UPI DETECTION
        # =========================
        upi_pattern = r"\b[a-zA-Z0-9._-]{2,}@[a-zA-Z]{2,}\b"

        # =========================
        # EMAIL DETECTION (NEW)
        # =========================
        email_pattern = r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"

        # =========================
        # PHONE DETECTION
        # Only if starts with +
        # =========================
        phone_pattern = r"\+\d{8,15}"

        # =========================
        # LINKS (http + www)
        # =========================
        link_pattern = r"(https?://[^\s]+|www\.[^\s]+)"

        # =========================
        # BANK ACCOUNT (Digits not after +)
        # =========================
        bank_pattern = r"(?<!\+)\b\d{9,18}\b"

        # =========================
        # SUSPICIOUS KEYWORDS
        # =========================
        suspicious_words = [
            "urgent",
            "verify",
            "immediate",
            "otp",
            "blocked",
            "suspend",
            "kyc",
            "update",
            "expire",
            "limited time",
            "act now",
            "send otp"
        ]

        # =========================
        # FIND ALL
        # =========================
        new_upi = re.findall(upi_pattern, message_text)
        new_emails = re.findall(email_pattern, message_text)
        new_phone_raw = re.findall(phone_pattern, message_text)
        new_links = re.findall(link_pattern, message_text)
        new_bank = re.findall(bank_pattern, message_text)

        # Normalize phone
        new_phone = [normalize_phone(p) for p in new_phone_raw]

        # Keywords
        found_keywords = [
            word for word in suspicious_words
            if word.lower() in message_text.lower()
        ]

        # =========================
        # MERGE INTO SESSION
        # =========================
        intel["upiIds"] = list(set(intel["upiIds"] + new_upi))
        intel["emails"] = list(set(intel["emails"] + new_emails))
        intel["phoneNumbers"] = list(set(intel["phoneNumbers"] + new_phone))
        intel["phishingLinks"] = list(set(intel["phishingLinks"] + new_links))
        intel["bankAccounts"] = list(set(intel["bankAccounts"] + new_bank))
        intel["suspiciousKeywords"] = list(set(intel["suspiciousKeywords"] + found_keywords))

        session["intelligence"] = intel

        print("INTELLIGENCE:", session["intelligence"])

    except Exception as e:
        print("Extraction error:", e)
