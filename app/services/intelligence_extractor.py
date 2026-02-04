import re

from requests import session

def extract_intelligence(text, session):

    upi = re.findall(r'\w+@\w+', text)
    phones = re.findall(r'\+?\d{10,13}', text)
    links = re.findall(r'http[s]?://\S+', text)

    session["intelligence"]["upiIds"] = list(
        set(session["intelligence"]["upiIds"] + upi)
    )

    session["intelligence"]["phoneNumbers"] = list(
        set(session["intelligence"]["phoneNumbers"] + phones)
    )

    session["intelligence"]["phishingLinks"] = list(
        set(session["intelligence"]["phishingLinks"] + links)
    )


    # Keyword tracking
    keywords = ["urgent", "verify", "blocked", "suspend"]
    for k in keywords:
        if k in text.lower():
            session["intelligence"]["suspiciousKeywords"].append(k)
