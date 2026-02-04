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


class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class HoneypotRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post("/honeypot")
async def honeypot_endpoint(
    request: HoneypotRequest,
    x_api_key: str = Header(...)
):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session = get_session(request.sessionId)

    message_text = request.message.text
    session["messages"].append(message_text)

    # ===== SCAM DETECTION =====
    scam_score = detect_scam_score(message_text)

    if scam_score >= 1:
        session["scam_detected"] = True

    # ===== INTELLIGENCE EXTRACTION =====
    if session.get("scam_detected"):
        extract_intelligence(message_text, session)

    # ===== GEMINI REPLY =====
    reply = generate_gemini_reply(
        message_text,
        session["messages"]
    )

    if not isinstance(reply, str) or len(reply.strip()) == 0:
        reply = "Can you explain more about this?"

    reply = reply.strip()[:300]

    # ===== FINAL CALLBACK =====
    if (
        session.get("scam_detected")
        and len(session.get("messages", [])) >= 6
        and not session.get("callback_sent", False)
    ):
        send_final_callback(request.sessionId, session)

    return {
        "status": "success",
        "reply": reply
    }
