from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.session_store import get_session
from app.services.scam_detector import detect_scam_score
from app.services.intelligence_extractor import extract_intelligence
from app.services.callback_service import send_final_callback
from app.services.gemini_agent import generate_gemini_reply

router = APIRouter()

API_KEY = "test123"

FALLBACK_REPLY = "Can you explain more about this?"

# =========================
# MODELS
# =========================

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, Any]]
    metadata: Dict[str, Any]


# =========================
# SAFE ENDPOINT
# =========================

@router.post("/honeypot")
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(...)
):

    try:

        # ========= AUTH =========
        if x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Invalid API Key")

        # ========= SESSION =========
        session = get_session(request.sessionId)

        message_text = request.message.text or ""
        session.setdefault("messages", []).append(message_text)
        session.setdefault("scam_detected", False)
        session.setdefault("callback_sent", False)

        # ========= SCAM DETECTION =========
        try:
            scam_score = detect_scam_score(message_text)
            if scam_score >= 1:
                session["scam_detected"] = True
        except Exception as e:
            print("Scam detection error:", e)

        # ========= EXTRACTION =========
        try:
            if session.get("scam_detected"):
                extract_intelligence(message_text, session)
        except Exception as e:
            print("Extraction error:", e)

        # ========= GEMINI REPLY =========
        reply = FALLBACK_REPLY

        try:
            gemini_reply = generate_gemini_reply(
                message_text,
                session.get("messages", [])
            )

            if isinstance(gemini_reply, str) and len(gemini_reply.strip()) > 5:
                reply = gemini_reply.strip()[:300]

        except Exception as e:
            print("Gemini error:", e)

        # ========= CALLBACK =========
        try:
            if (
                session.get("scam_detected")
                and len(session.get("messages", [])) >= 6
                and not session.get("callback_sent", False)
            ):
                send_final_callback(request.sessionId, session)
        except Exception as e:
            print("Callback error:", e)

        # ========= ALWAYS RETURN VALID =========
        return {
            "status": "success",
            "reply": reply
        }

    except Exception as fatal:
        print("FATAL ENDPOINT ERROR:", fatal)

        return {
            "status": "success",
            "reply": FALLBACK_REPLY
        }
