import re

UPI_PATTERN = re.compile(r"\b[\w\.-]{2,}@[\w\.-]{2,}\b")
PHONE_PATTERN = re.compile(r"\+\d{8,15}")
EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b")
LINK_PATTERN = re.compile(r"(https?://[^\s]+|www\.[^\s]+)")
BANK_PATTERN = re.compile(r"\b\d{9,18}\b")

SUSPICIOUS_KEYWORDS = [
    "otp", "urgent", "verify", "blocked", "suspended",
    "security alert", "immediate", "act now", "send otp",
    "payment", "transfer", "bank", "login"
]


def extract_intelligence(message_text, session):

    # 🔥 NEVER LET KEYS BREAK
    if "intelligence" not in session:
        session["intelligence"] = {}

    intel = session["intelligence"]

    intel.setdefault("upiIds", [])
    intel.setdefault("phoneNumbers", [])
    intel.setdefault("phishingLinks", [])
    intel.setdefault("bankAccounts", [])
    intel.setdefault("emails", [])
    intel.setdefault("suspiciousKeywords", [])

    # Extract
    upis = UPI_PATTERN.findall(message_text)
    phones = PHONE_PATTERN.findall(message_text)
    emails = EMAIL_PATTERN.findall(message_text)
    links = LINK_PATTERN.findall(message_text)
    banks = BANK_PATTERN.findall(message_text)

    # Remove phone numbers from bank list
    banks = [b for b in banks if not any(b in p for p in phones)]

    # Keywords
    found_keywords = [
        kw for kw in SUSPICIOUS_KEYWORDS
        if kw.lower() in message_text.lower()
    ]

    # Merge unique
    intel["upiIds"] = list(set(intel["upiIds"] + upis))
    intel["phoneNumbers"] = list(set(intel["phoneNumbers"] + phones))
    intel["emails"] = list(set(intel["emails"] + emails))
    intel["phishingLinks"] = list(set(intel["phishingLinks"] + links))
    intel["bankAccounts"] = list(set(intel["bankAccounts"] + banks))
    intel["suspiciousKeywords"] = list(set(intel["suspiciousKeywords"] + found_keywords))

    print("INTELLIGENCE:", intel)