"""Tiny sqlite3 layer - zero ORM dependencies so the demo never breaks.

Tables:
  users          - phone-keyed profiles (voice fingerprint / returning-caller memory)
  sessions       - one conversation (IVR call, WhatsApp chat or dashboard session)
  applications   - one scheme application with tracking id
  sms_outbox     - every SMS SAHAYI sends (mock inbox powers the on-screen phone)
  impact_events  - green-receipt events feeding the impact dashboard
"""
import json
import sqlite3
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

from .config import settings

_lock = threading.Lock()
_conn: Optional[sqlite3.Connection] = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  phone TEXT PRIMARY KEY,
  name TEXT DEFAULT '',
  language TEXT DEFAULT 'hi',
  profile TEXT DEFAULT '{}',
  created_at REAL
);
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  phone TEXT DEFAULT '',
  channel TEXT DEFAULT 'dashboard',
  language TEXT DEFAULT 'hi',
  state TEXT DEFAULT 'GREETING',
  context TEXT DEFAULT '{}',
  created_at REAL,
  updated_at REAL
);
CREATE TABLE IF NOT EXISTS applications (
  id TEXT PRIMARY KEY,
  tracking_id TEXT UNIQUE,
  phone TEXT,
  scheme TEXT,
  language TEXT DEFAULT 'hi',
  profile TEXT DEFAULT '{}',
  status TEXT DEFAULT 'FORM_GENERATED',
  eligible INTEGER DEFAULT 1,
  benefit_inr REAL DEFAULT 0,
  pdf_path TEXT DEFAULT '',
  created_at REAL
);
CREATE TABLE IF NOT EXISTS sms_outbox (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone TEXT,
  body TEXT,
  kind TEXT DEFAULT 'info',
  created_at REAL
);

CREATE TABLE IF NOT EXISTS impact_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone TEXT,
  kind TEXT,
  co2_kg REAL DEFAULT 0,
  paper_sheets REAL DEFAULT 0,
  km_avoided REAL DEFAULT 0,
  benefit_inr REAL DEFAULT 0,
  meta TEXT DEFAULT '{}',
  created_at REAL
);
-- indexes last: every table above must exist before indexing it
CREATE INDEX IF NOT EXISTS idx_sms_phone ON sms_outbox(phone, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_phone ON sessions(phone);
CREATE INDEX IF NOT EXISTS idx_impact_phone ON impact_events(phone);
"""


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # WAL lets readers work while a write commits; NORMAL is crash-safe
    # for our per-turn commits and noticeably faster than the default.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db() -> None:
    global _conn
    with _lock:
        if _conn is None:
            _conn = _connect()
        _conn.executescript(SCHEMA)
        _conn.commit()


def _ensure() -> None:
    """Lazy init: serverless (Vercel) never runs startup events, so every
    entry point connects on first use instead of asserting."""
    if _conn is None:
        init_db()


def _now() -> float:
    return time.time()


# ---------------------------------------------------------------- users


def upsert_user(phone: str, name: str = "", language: str = "", profile: Optional[dict] = None) -> dict:
    _ensure()
    with _lock:
        row = _conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        if row:
            if name:
                _conn.execute("UPDATE users SET name=? WHERE phone=?", (name, phone))
            if language:
                _conn.execute("UPDATE users SET language=? WHERE phone=?", (language, phone))
            if profile:
                merged = {**json.loads(row["profile"]), **profile}
                _conn.execute("UPDATE users SET profile=? WHERE phone=?", (json.dumps(merged), phone))
            _conn.commit()
            row = _conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
            return dict(row)
        _conn.execute(
            "INSERT INTO users (phone,name,language,profile,created_at) VALUES (?,?,?,?,?)",
            (phone, name, language or "hi", json.dumps(profile or {}), _now()),
        )
        _conn.commit()
        return {"phone": phone, "name": name, "language": language or "hi",
                "profile": json.dumps(profile or {}), "created_at": _now()}


def get_user(phone: str) -> Optional[dict]:
    _ensure()
    with _lock:
        row = _conn.execute("SELECT * FROM users WHERE phone=?", (phone,)).fetchone()
        return dict(row) if row else None


def user_profile(phone: str) -> dict:
    u = get_user(phone)
    return json.loads(u["profile"]) if u else {}


# ---------------------------------------------------------------- sessions


def new_session(phone: str, channel: str, language: str) -> dict:
    sid = f"s-{uuid.uuid4().hex[:10]}"
    _ensure()
    with _lock:
        _conn.execute(
            "INSERT INTO sessions (id,phone,channel,language,state,context,created_at,updated_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (sid, phone, channel, language, "GREETING", "{}", _now(), _now()),
        )
        _conn.commit()
    return {"id": sid, "phone": phone, "channel": channel, "language": language,
            "state": "GREETING", "context": "{}"}


def get_session(sid: str) -> Optional[dict]:
    _ensure()
    with _lock:
        row = _conn.execute("SELECT * FROM sessions WHERE id=?", (sid,)).fetchone()
        return dict(row) if row else None


def update_session(sid: str, state: str, context: dict, language: Optional[str] = None) -> None:
    _ensure()
    with _lock:
        if language:
            _conn.execute("UPDATE sessions SET language=? WHERE id=?", (language, sid))
        _conn.execute("UPDATE sessions SET state=?, context=?, updated_at=? WHERE id=?",
                      (state, json.dumps(context), _now(), sid))
        _conn.commit()


def session_context(sid: str) -> dict:
    s = get_session(sid)
    return json.loads(s["context"]) if s else {}


# ---------------------------------------------------------------- applications


def create_application(phone: str, scheme: str, language: str, profile: dict,
                       eligible: bool, benefit_inr: float, pdf_path: str = "") -> dict:
    app_id = f"a-{uuid.uuid4().hex[:10]}"
    tracking_id = f"SAH-{uuid.uuid4().hex[:6].upper()}"
    _ensure()
    with _lock:
        _conn.execute(
            "INSERT INTO applications (id,tracking_id,phone,scheme,language,profile,status,"
            "eligible,benefit_inr,pdf_path,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (app_id, tracking_id, phone, scheme, language, json.dumps(profile),
             "FORM_GENERATED", int(eligible), benefit_inr, pdf_path, _now()),
        )
        _conn.commit()
    return {"id": app_id, "tracking_id": tracking_id, "scheme": scheme,
            "status": "FORM_GENERATED", "eligible": eligible, "benefit_inr": benefit_inr}


def get_application_by_tracking(tracking_id: str) -> Optional[dict]:
    _ensure()
    with _lock:
        row = _conn.execute("SELECT * FROM applications WHERE tracking_id=?", (tracking_id,)).fetchone()
        return dict(row) if row else None


def set_application_status(tracking_id: str, status: str) -> None:
    _ensure()
    with _lock:
        _conn.execute("UPDATE applications SET status=? WHERE tracking_id=?", (status, tracking_id))
        _conn.commit()


def set_application_pdf(tracking_id: str, pdf_path: str) -> None:
    _ensure()
    with _lock:
        _conn.execute("UPDATE applications SET pdf_path=? WHERE tracking_id=?", (pdf_path, tracking_id))
        _conn.commit()


# ---------------------------------------------------------------- sms + impact


def log_sms(phone: str, body: str, kind: str = "info") -> None:
    _ensure()
    with _lock:
        _conn.execute("INSERT INTO sms_outbox (phone,body,kind,created_at) VALUES (?,?,?,?)",
                      (phone, body, kind, _now()))
        _conn.commit()


def sms_inbox(phone: str, limit: int = 20) -> List[dict]:
    _ensure()
    with _lock:
        rows = _conn.execute(
            "SELECT * FROM sms_outbox WHERE phone=? ORDER BY created_at DESC LIMIT ?",
            (phone, limit)).fetchall()
        return [dict(r) for r in rows]


def log_impact(phone: str, kind: str, co2_kg: float, paper_sheets: float,
               km_avoided: float, benefit_inr: float, meta: Optional[dict] = None) -> None:
    _ensure()
    with _lock:
        _conn.execute(
            "INSERT INTO impact_events (phone,kind,co2_kg,paper_sheets,km_avoided,benefit_inr,meta,created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (phone, kind, co2_kg, paper_sheets, km_avoided, benefit_inr,
             json.dumps(meta or {}), _now()),
        )
        _conn.commit()


def close() -> None:
    """Close the shared connection (Windows test teardown needs this)."""
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None


def impact_totals() -> dict:
    _ensure()
    with _lock:
        row = _conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(co2_kg),0) AS co2, COALESCE(SUM(paper_sheets),0) AS paper,"
            " COALESCE(SUM(km_avoided),0) AS km, COALESCE(SUM(benefit_inr),0) AS inr"
            " FROM impact_events").fetchone()
        return dict(row)
