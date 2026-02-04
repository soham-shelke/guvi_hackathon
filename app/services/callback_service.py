import requests


def send_final_callback(session_id, session):

    payload = {
        "sessionId": session_id,
        "scamDetected": session.get("scam_detected", False),
        "totalMessagesExchanged": len(session.get("messages", [])),
        "extractedIntelligence": session.get("intelligence", {}),
        "agentNotes": "Automated honeypot engagement completed"
    }

    try:
        print("\n===== SENDING FINAL CALLBACK =====")
        print("Payload:", payload)

        res = requests.post(
            "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
            json=payload,
            timeout=5
        )

        print("Callback Status Code:", res.status_code)
        print("Callback Response:", res.text)

        if res.status_code == 200:
            session["callback_sent"] = True
            print("Callback marked as sent ✅")
        else:
            print("Callback returned non-200")

        print("===================================\n")

    except Exception as e:
        print("Callback failed :", e)
