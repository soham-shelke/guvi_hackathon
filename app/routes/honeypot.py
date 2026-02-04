from fastapi import APIRouter, Header, Request
from fastapi.concurrency import run_in_threadpool
import json
import datetime

from app.services.session_store import get_session
from app.services.scam_detector import detect_scam_score
from app.services.intelligence_extractor import extract_intelligence
from app.services.callback_service import send_final_callback
from app.services.gemini_agent import generate_gemini_reply

router = APIRouter()

API_KEY = "test123"


# =====================================
# SAFE RESPONSE BUILDER
# =====================================
def safe_response(reply_text):

    if not isinstance(reply_text, str):
        reply_text = "Can you explain more about this?"

    reply_text = reply_text.strip()

    if len(reply_text) == 0:
        reply_text = "Can you explain more about this?"

    reply_text = reply_text.replace("\n", " ").replace("\r", " ")

    reply_text = reply_text[:300]

    return {
        "status": "success",
        "reply": reply_text
    }


# =====================================
# MAIN ENDPOINT (ULTRA SAFE VERSION)
# =====================================
@router.post("/honeypot")
async def honeypot_endpoint(
    request: Request,
    x_api_key: str = Header(None)
):

    start_time = datetime.datetime.utcnow()

    print("\n==============================")
    print("REQUEST ARRIVED:", start_time.isoformat())

    # ===== HEADERS LOG =====
    try:
        print("HEADERS:", dict(request.headers))
    except:
        pass

    # ===== RAW BODY LOG =====
    try:
        raw_body = await request.body()
        raw_text = raw_body.decode("utf-8", errors="ignore")
        print("RAW BODY:", raw_text)
    except:
        raw_text = ""
        print("RAW BODY: <FAILED TO READ>")

    print("==============================")

    # ===== API KEY SAFE CHECK =====
    if x_api_key != API_KEY:
        return safe_response("Can you explain more about this?")

    # ===== SAFE BODY PARSE =====
    try:
        body = json.loads(raw_text) if raw_text else {}
    except:
        body = {}

    # ===== SAFE FIELD EXTRACTION =====
    session_id = str(body.get("sessionId", "eval-session"))

    message = body.get("message", {})

    message_text = str(message.get("text", ""))

    # ===== SESSION =====
    session = get_session(session_id)

    if message_text:
        session["messages"].append(message_text)

        scam_score = detect_scam_score(message_text)

        if scam_score >= 1:
            session["scam_detected"] = True

        if session.get("scam_detected"):
            try:
                extract_intelligence(message_text, session)
            except Exception as e:
                print("Extraction error:", e)

    # ===== FAST SAFE REPLY =====
    reply = "Can you explain more about this?"

    if session.get("scam_detected") and len(session["messages"]) > 1:
        try:
            gemini_reply = await run_in_threadpool(
                generate_gemini_reply,
                message_text,
                session["messages"]
            )

            if isinstance(gemini_reply, str):
                reply = gemini_reply

        except Exception as e:
            print("Gemini error:", e)

    # ===== CALLBACK SAFE =====
    try:
        if (
            session.get("scam_detected")
            and len(session["messages"]) >= 6
            and not session["callback_sent"]
        ):
            send_final_callback(session_id, session)
    except Exception as e:
        print("Callback error:", e)

    end_time = datetime.datetime.utcnow()

    print("RESPONSE SENT:", end_time.isoformat())
    print("TOTAL TIME:", (end_time - start_time).total_seconds())
    print("==============================\n")

    return safe_response(reply)
