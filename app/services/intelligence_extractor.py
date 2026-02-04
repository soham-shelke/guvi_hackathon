import re


def extract_intelligence(message_text, session):

    # Ensure intelligence exists
    if "intelligence" not in session:
        session["intelligence"] = {
            "upiIds": [],
            "phoneNumbers": [],
            "phishingLinks": []
        }

    # Extract new values
    new_upi = re.findall(r"[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}", message_text)

    new_phone = re.findall(
        r"(?:\+91[-\s]?|0)?[6-9]\d{9}",
        message_text
    )

    new_links = re.findall(
        r"(https?://[^\s]+)",
        message_text
    )

    # Merge without duplicates
    session["intelligence"]["upiIds"] = list(
        set(session["intelligence"]["upiIds"] + new_upi)
    )

    session["intelligence"]["phoneNumbers"] = list(
        set(session["intelligence"]["phoneNumbers"] + new_phone)
    )

    session["intelligence"]["phishingLinks"] = list(
        set(session["intelligence"]["phishingLinks"] + new_links)
    )

    print("INTELLIGENCE:", session["intelligence"])
