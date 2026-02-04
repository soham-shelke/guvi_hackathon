SCAM_KEYWORDS = [
    "verify", "upi", "urgent", "blocked",
    "otp", "suspend", "bank", "kyc"
]

def detect_scam_score(text):
    text = text.lower()
    score = sum(word in text for word in SCAM_KEYWORDS)
    return score
