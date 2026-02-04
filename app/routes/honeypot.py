from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from app.services.session_store import get_session
from app.services.scam_detector import detect_scam_score
from app.services.intelligence_extractor import extract_intelligence
from app.services.callback_service import send_final_callback
from app.services.gemini_agent import generate_gemini_reply

from fastapi.concurrency import run_in_threadpool


router = APIRouter()

API_KEY = "test123"


# ===== STRICT MODELS (Tester Compatible) =====

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

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    session = get_session(request.sessionId)

    message_text = request.message.text
    session["messages"].append(message_text)

    # ===== SCAM DETECTION =====
    scam_score = detect_scam_score(message_text)

    if scam_score >= 1:
        session["scam_detected"] = True

    # ===== EXTRACTION =====
    if session["scam_detected"]:
        extract_intelligence(message_text, session)

    # ===== GEMINI AI REPLY (SAFE RESTORED VERSION) =====
    reply = "Can you explain more about this?"

    # 🔥 IMPORTANT: Skip Gemini on first message (prevents blocking delay)
    if session["scam_detected"] and len(session["messages"]) > 1:

        try:
            gemini_reply = await run_in_threadpool(
            generate_gemini_reply,
            message_text,
            session["messages"]
            )


            if isinstance(gemini_reply, str) and len(gemini_reply.strip()) > 5:
                reply = gemini_reply[:350]

        except Exception as e:
            print("Gemini skipped or failed:", e)


    # ===== CALLBACK (SAFE) =====
    if (
        session["scam_detected"]
        and len(session["messages"]) >= 6
        and not session["callback_sent"]
    ):
        try:
            send_final_callback(request.sessionId, session)
        except Exception as e:
            print("Callback error:", e)

    return {
        "status": "success",
        "reply": str(reply)
    }
