"""Application tracking: SAH-XXXXXX IDs resolve to a government-style status.

The demo pipeline simulates the real back-office: FORM_GENERATED -> CSC_VERIFIED
-> SUBMITTED -> APPROVED. POST /track/{id}/advance moves it forward so judges
can watch a live status update on stage - the 'wow' beat in the pitch.
"""
from .. import db
from ..schemes import SCHEMES

PIPELINE = ["FORM_GENERATED", "CSC_VERIFIED", "SUBMITTED", "APPROVED"]

_STEPS = {
    "FORM_GENERATED": "Form PDF ban gaya hai. Ise CSC ya online jama karaiye.",
    "CSC_VERIFIED": "CSC centre ne documents verify kar diye.",
    "SUBMITTED": "Yojana office mein submit ho gaya.",
    "APPROVED": "SANKALP! Aapki yojana MANZURI ho gayi hai. Paisa seedha bank khate mein.",
}

_STEPS_EN = {
    "FORM_GENERATED": "Form PDF ready. Submit at a CSC or online.",
    "CSC_VERIFIED": "Documents verified at CSC centre.",
    "SUBMITTED": "Submitted to scheme office.",
    "APPROVED": "SUCCESS! Application approved. Money goes straight to bank account.",
}


def status_of(tracking_id: str) -> dict | None:
    app = db.get_application_by_tracking(tracking_id.upper())
    if not app:
        return None
    scheme = SCHEMES.get(app["scheme"], {})
    return {
        "tracking_id": app["tracking_id"],
        "scheme": scheme.get("name", app["scheme"]),
        "scheme_emoji": scheme.get("emoji", "📄"),
        "status": app["status"],
        "status_message": _STEPS_EN.get(app["status"], app["status"]),
        "eligible": bool(app["eligible"]),
        "benefit_inr": app["benefit_inr"],
        "pipeline": PIPELINE,
        "step_index": PIPELINE.index(app["status"]) if app["status"] in PIPELINE else 0,
        "created_at": app["created_at"],
    }


def advance(tracking_id: str) -> dict | None:
    app = db.get_application_by_tracking(tracking_id.upper())
    if not app:
        return None
    idx = PIPELINE.index(app["status"]) if app["status"] in PIPELINE else 0
    nxt = PIPELINE[min(idx + 1, len(PIPELINE) - 1)]
    db.set_application_status(app["tracking_id"], nxt)
    return status_of(app["tracking_id"])
