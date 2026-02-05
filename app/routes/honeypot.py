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


# ===== MODELS =====
class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, Any]]
    metadata: Dict[str, Any]


# ===== MAIN ENDPOINT =====
@router.post("/honeypot")
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(...)
):

    # ===== AUTH =====
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    # ===== SESSION LOAD =====
    session = get_session(request.sessionId)

    # ===== SAFE SESSION INIT (NO BREAK IF MISSING KEYS) =====
    session.setdefault("messages", [])
    session.setdefault("scam_detected", False)
    session.setdefault("callback_sent", False)
    session.setdefault("intelligence", {
        "upiIds": [],
        "phoneNumbers": [],
        "phishingLinks": [],
        "suspiciousKeywords": []
    })

    message_text = request.message.text

    # ===== STORE MESSAGE =====
    session["messages"].append(message_text)

    # ===== SCAM DETECTION =====
    scam_score = detect_scam_score(message_text)

    if scam_score >= 1:
        session["scam_detected"] = True

    # ===== INTELLIGENCE EXTRACTION =====
    if session["scam_detected"]:
        extract_intelligence(message_text, session)

    # ===== GEMINI REPLY =====
    reply = generate_gemini_reply(
        message_text,
        session["messages"]
    )

    # ===== SAFE FALLBACK =====
    if not isinstance(reply, str) or len(reply.strip()) == 0:
        reply = "Can you explain more about this?"

    reply = reply.strip()[:300]

    # ===== FINAL CALLBACK =====
    if (
        session["scam_detected"]
        and len(session["messages"]) >= 6
        and not session["callback_sent"]
    ):
        try:
            send_final_callback(request.sessionId, session)
        except Exception as e:
            print("Callback Error:", e)

    return {
        "status": "success",
        "reply": reply
    }
