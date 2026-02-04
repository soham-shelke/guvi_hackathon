import random

SCAM_REPLIES = [
    "Why is my account blocked?",
    "Which bank is this about?",
    "Can you send official verification?",
    "How do I verify this safely?",
    "Is there a customer care number?"
]

NORMAL_REPLIES = [
    "Okay, I understand.",
    "Can you explain more?",
    "I am not sure I follow."
]

def generate_agent_reply(is_scam):
    if is_scam:
        return random.choice(SCAM_REPLIES)
    return random.choice(NORMAL_REPLIES)
