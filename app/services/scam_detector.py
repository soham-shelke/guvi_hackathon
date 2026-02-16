import re

# Ultra fast keyword detection (no loops inside loops)
SCAM_KEYWORDS = re.compile(
    r"(otp|verify|urgent|blocked|suspend|suspended|k y c|kyc|update account|"
    r"login|bank|payment|upi|transfer|send money|refund|lottery|prize|"
    r"security alert|reset password|click link|limited time|act now)",
    re.IGNORECASE
)

# Suspicious entity patterns
LINK_PATTERN = re.compile(r"(https?://|www\.)", re.IGNORECASE)
UPI_PATTERN = re.compile(r"\b[\w\.-]{2,}@[\w\.-]{2,}\b")
PHONE_PATTERN = re.compile(r"\+\d{8,15}")
EMAIL_PATTERN = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}\b")


def detect_scam_score(message_text: str) -> int:

    if not message_text:
        return 0

    score = 0

    # Fast keyword check
    if SCAM_KEYWORDS.search(message_text):
        score += 1

    # Entity based scoring
    if LINK_PATTERN.search(message_text):
        score += 1

    if UPI_PATTERN.search(message_text):
        score += 1

    if PHONE_PATTERN.search(message_text):
        score += 1

    if EMAIL_PATTERN.search(message_text):
        score += 1

    return score