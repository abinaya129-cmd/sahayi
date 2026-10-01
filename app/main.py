"""SAHAYI API - one FastAPI app, every channel.

  GET  /                      demo dashboard (voice mic, SMS phone, impact wall)
  POST /api/start             new conversation -> greeting + language options
  POST /api/message           user utterance (typed or post-STT) -> brain reply
  POST /api/voice             audio upload -> Google STT -> brain reply
  GET  /api/languages         12-language registry
  GET  /api/schemes           scheme catalog
  GET  /api/impact            live impact wall (Green Receipt totals)
  GET  /api/sms/{phone}       mock inbox (powers the on-screen phone)
  GET  /api/track/{tid}       application status
  POST /api/track/{tid}/advance  move status pipeline (demo beat)
  GET  /api/csc?loc=          nearest CSC
  GET  /api/nlu/status        explainability endpoint
  GET  /api/health            liveness + capability report
  GET  /pdf/{tid}.pdf         generated application PDF
  POST /ivr/voice             Twilio IVR webhook (TwML)
  POST /ivr/sms               Twilio inbound SMS webhook (TwML)
  POST /whatsapp              Twilio WhatsApp webhook (TwML)
  GET  /whatsapp/send         dev helper: push a WhatsApp/SMS message to outbox
"""
import os
import uuid

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from . import db, nlu
from .config import settings
from .conversation import Conversation
from .languages import LANGUAGES
from .schemes import SCHEMES
from .services import impact, speech
from .services.csc import locate
from .services.sms import inbox, twilio_enabled

app = FastAPI(title="SAHAYI", version=settings.VERSION,
              description=settings.TAGLINE)
os.makedirs(settings.PDF_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


def _conv(session_id: str | None) -> Conversation:
    return Conversation(session_id or uuid.uuid4().hex)


# ------------------------------------------------------------------ dashboard

@app.get("/", response_class=HTMLResponse)
def index():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return HTMLResponse("<h1>SAHAYI</h1><p>Dashboard missing: static/index.html</p>")


# ------------------------------------------------------------------ core API

@app.post("/api/start")
def api_start(phone: str = Form(""), channel: str = Form("dashboard")):
    conv = _conv(None)
    reply = conv.start(phone=phone)
    return reply


@app.post("/api/message")
def api_message(session_id: str = Form(...), text: str = Form(...), phone: str = Form("")):
    conv = _conv(session_id)
    if phone and not conv.phone:
        conv.phone = phone
        conv._remember(phone=phone)
    return conv.handle(text)


@app.post("/api/voice")
async def api_voice(session_id: str = Form(...), language: str = Form("hi"),
                    audio: UploadFile = File(...)):
    """Audio -> STT -> brain. Requires Google STT; otherwise explains fallback."""
    data = await audio.read()
    stt = speech.speech_to_text(data, language)
    if "error" in stt:
        raise HTTPException(status_code=503, detail=stt["error"])
    conv = _conv(session_id)
    reply = conv.handle(stt.get("text", ""))
    reply["heard"] = stt.get("text", "")
    return reply


@app.get("/api/languages")
def api_languages():
    return {"count": len(LANGUAGES), "languages": LANGUAGES}


@app.get("/api/schemes")
def api_schemes():
    return {"count": len(SCHEMES),
            "schemes": [{"slug": k, **{kk: vv for kk, vv in v.items() if kk != "rules"}}
                        for k, v in SCHEMES.items()]}


@app.get("/api/impact")
def api_impact():
    return impact.totals()


@app.get("/api/sms/{phone}")
def api_sms(phone: str):
    return {"phone": phone, "messages": inbox(phone)}


@app.get("/api/track/{tid}")
def api_track(tid: str):
    from .services.tracking import status_of
    st = status_of(tid)
    if not st:
        raise HTTPException(status_code=404, detail="Tracking ID not found")
    return st


@app.post("/api/track/{tid}/advance")
def api_track_advance(tid: str):
    from .services.tracking import advance
    st = advance(tid)
    if not st:
        raise HTTPException(status_code=404, detail="Tracking ID not found")
    return st


@app.get("/api/csc")
def api_csc(loc: str = "", lat: float | None = None, lon: float | None = None):
    return locate(loc, lat, lon)


@app.get("/api/nlu/status")
def api_nlu_status():
    return nlu.nlu_status()


@app.get("/api/health")
def api_health():
    return {
        "status": "ok", "app": settings.APP_NAME, "version": settings.VERSION,
        "speech": speech.status(), "sms": "twilio" if twilio_enabled() else "mock",
        "impact": impact.totals(),
    }


@app.get("/pdf/{tid}.pdf")
def api_pdf(tid: str):
    rec = db.get_application_by_tracking(tid.upper())
    if not rec or not rec["pdf_path"] or not os.path.exists(rec["pdf_path"]):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(rec["pdf_path"], media_type="application/pdf",
                        filename=f"SAHAYI_{tid.upper()}.pdf")


# ------------------------------------------------------------------ Twilio IVR

def _twml_say(text: str, with_gather: bool = True) -> str:
    """Tiny TwML builder (no XML lib needed)."""
    gather = ""
    if with_gather:
        gather = ('<Gather input="speech" language="hi-IN" action="/ivr/voice" '
                  'method="POST" speechTimeout="auto"/>')
    return (f'<?xml version="1.0" encoding="UTF-8"?><Response>'
            f'<Say language="hi-IN">{text}</Say>{gather}</Response>')


@app.post("/ivr/voice")
async def ivr_voice(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid", uuid.uuid4().hex)
    speech_result = form.get("SpeechResult", "")
    # Twilio STT already transcribed; feed the brain
    conv = Conversation(f"ivr-{call_sid}")
    if not speech_result:
        return Response(_twml_say("Namaste! Main SAHAYI hoon. Boliye, kaunsi seva chahiye?"),
                        media_type="application/xml")
    reply = conv.handle(speech_result)
    return Response(_twml_say(reply["speak"][:600]), media_type="application/xml")


@app.post("/ivr/sms")
async def ivr_sms(request: Request):
    form = await request.form()
    body = form.get("Body", "")
    from_no = form.get("From", "unknown")
    db.log_sms(from_no, f"[inbound] {body}", kind="inbound")
    conv = Conversation(f"sms-{from_no[-10:]}")
    reply = conv.handle(body)
    sms_out = sms.send_sms(from_no, reply["speak"][:300])
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply["text"][:300]}</Message></Response>',
        media_type="application/xml")


# ------------------------------------------------------------------ WhatsApp

@app.post("/whatsapp")
async def whatsapp(request: Request):
    form = await request.form()
    body = form.get("Body", "")
    from_no = form.get("From", "whatsapp:unknown").replace("whatsapp:", "")
    db.log_sms(from_no, f"[wa-in] {body}", kind="whatsapp")
    conv = Conversation(f"wa-{from_no[-10:]}")
    reply = conv.handle(body)
    return Response(
        f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply["text"][:300]}</Message></Response>',
        media_type="application/xml")


@app.get("/whatsapp/send")
def whatsapp_send(phone: str, text: str):
    """Dev helper so the dashboard can pre-seed the mock inbox."""
    from .services.sms import send_sms
    return send_sms(phone, text, kind="whatsapp")
