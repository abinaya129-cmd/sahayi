"""SMS gateway: real Twilio when configured, DB-backed mock inbox otherwise.

Every message is ALWAYS logged to the mock inbox - that's what powers the
on-screen phone in the demo dashboard. When Twilio creds exist, the same
message also goes out over the real network (judges' real phones).
"""
from .. import db
from ..config import settings

_client = None
if settings.TWILIO_SID and settings.TWILIO_TOKEN and settings.TWILIO_FROM:
    try:
        from twilio.rest import Client
        _client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
    except Exception:
        _client = None


def twilio_enabled() -> bool:
    return _client is not None


def send_sms(phone: str, body: str, kind: str = "info") -> dict:
    """Send SMS. Returns channel info for the API response."""
    body = (body or "").strip()
    db.log_sms(phone, body, kind)
    result = {"channel": "mock", "phone": phone, "body": body[:160]}
    if _client is not None and phone and not phone.startswith("demo"):
        try:
            msg = _client.messages.create(to=phone, from_=settings.TWILIO_FROM, body=body)
            result["channel"] = "twilio"
            result["sid"] = msg.sid
        except Exception as e:  # network failure must never break the demo
            result["twilio_error"] = str(e)
    return result


def inbox(phone: str, limit: int = 30) -> list:
    return db.sms_inbox(phone, limit)
