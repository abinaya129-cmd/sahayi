"""End-to-end tests: the exact journey SAHAYI performs live on stage."""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SAHAYI_DB"] = "test_sahayi.db"

from app.main import app  # noqa: E402
from app import db  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _db():
    if os.path.exists("test_sahayi.db"):
        os.remove("test_sahayi.db")
    db.init_db()
    yield
    db.close()  # release the sqlite handle so Windows can delete the file
    if os.path.exists("test_sahayi.db"):
        os.remove("test_sahayi.db")


@pytest.fixture()
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "ok"
    assert j["impact"]["women_helped"] >= 1847


def test_start_returns_language_options(client):
    j = client.post("/api/start").json()
    assert j["state"] == "LANGUAGE"
    assert len(j["options"]) == 13  # 12 Indian languages + English
    assert j["fraud_shield"]["enabled"]


def test_full_happy_path_pm_kisan(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500001"}).json()

    j = say("hindi")
    assert j["state"] == "SCHEME"
    j = say("kisan ke liye paisa chahiye")
    assert j["state"] == "INTERVIEW"
    j = say("haan")            # is_farmer
    j = say("haan")            # has_land
    j = say("nahi")            # is_taxpayer -> eligible
    assert j["state"] == "VERDICT"
    assert j.get("eligible") is True
    j = say("documents")
    assert j["state"] == "DOCS"
    j = say("haan")            # start form
    assert j["state"] == "PROFILE"
    j = say("Lakshmi")
    j = say("9876543210")
    j = say("Rajasthan Barmer")
    assert j["state"] == "TRACKING"
    tid = j["tracking"]["tracking_id"]
    assert tid.startswith("SAH-")

    # SMS actually delivered to the mock inbox
    inbox = client.get("/api/sms/9876543210").json()["messages"]
    assert any(tid in m["body"] for m in inbox)
    assert any("SAHAYI" in m["body"] for m in inbox)

    # PDF generated and served
    r = client.get(f"/pdf/{tid}.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:4] == b"%PDF"

    # Tracking pipeline advances to approval
    st = client.post(f"/api/track/{tid}/advance").json()
    assert st["status"] == "CSC_VERIFIED"
    st = client.post(f"/api/track/{tid}/advance").json()
    st = client.post(f"/api/track/{tid}/advance").json()
    assert st["status"] == "APPROVED"


def test_english_full_flow(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500010"}).json()

    j = say("english")
    assert j["state"] == "SCHEME"
    assert "English" in j["text"] or "continue" in j["text"].lower()
    j = say("farmer money")
    assert j["state"] == "INTERVIEW"
    assert "Do you or your family do farming?" in j["text"]
    j = say("yes"); j = say("yes"); j = say("no")
    assert j["state"] == "VERDICT"
    assert j.get("eligible") is True
    assert "Congratulations" in j["text"]
    assert j["card"]["type"] == "success"
    j = say("documents")
    assert "Documents you need" in j["text"]


def test_ask_anything_kb(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500011"}).json()

    say("hindi")
    j = say("mujhe e bike chahiye")
    assert "PM E-DRIVE" in j["text"] or "E-DRIVE" in j["text"]
    assert j["card"]["type"] == "info"
    assert j["chips"], "KB answers must offer chips back into the flow"
    j = say("scholarship")
    assert "scholarships.gov.in" in j["text"]
    j = say("free phone milega")
    up = j["text"].upper()
    assert "NAHI" in up or "NO " in up
    j = say("kisan")
    assert j["state"] == "INTERVIEW"  # chips lead back into schemes


def test_kb_from_scheme_state(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500012"}).json()

    say("hindi")
    j = say("solar bijli")
    assert "Surya Ghar" in j["text"]


def test_rejection_suggests_alternatives(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500002"}).json()

    say("hindi")
    say("ujjwala gas")
    say("nahi")    # is_woman=False
    say("nahi")    # has_gas=False
    say("nahi")    # is_bpl=False
    j = say("25")  # age -> verdict: rejected
    assert j["state"] == "VERDICT"
    assert j.get("eligible") is False
    # never a dead end: options to continue exist + reasons are human-readable
    assert any(o["action"] in ("docs", "scheme") for o in j["options"])
    assert "mahilao" in j["text"] or "yojana" in j["text"]


def test_multilingual_scheme_detection(client):
    from app.nlu import detect_scheme, detect_yes_no
    assert detect_scheme("விவசாய பணம்") == "pm_kisan"       # Tamil farmer
    assert detect_scheme("రైతు డబ్బు") == "pm_kisan"          # Telugu farmer
    assert detect_scheme("gas connection chahiye") == "ujjwala"
    assert detect_scheme("ghar banana hai") == "awas"
    assert detect_scheme("kaam chahiye") == "mgnrega"
    assert detect_yes_no("हाँ") is True
    assert detect_yes_no("nahi") is False


def test_tracking_id_spoken_anywhere(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500003"}).json()

    say("hindi"); say("kisan"); say("haan"); say("haan"); say("nahi")
    say("documents"); say("haan"); say("Test User"); say("9876500003")
    tid = say("Rajasthan")["tracking"]["tracking_id"]
    # new session, speak the ID cold -> status comes back
    j2 = client.post("/api/start").json()
    j3 = client.post("/api/message", data={"session_id": j2["session_id"],
                                           "text": tid, "phone": ""}).json()
    assert j3["tracking"]["tracking_id"] == tid


def test_csc_locator(client):
    j = client.get("/api/csc", params={"loc": "tamil nadu madurai"}).json()
    assert j["results"][0]["district"] == "Madurai"
    j = client.get("/api/csc", params={"lat": 25.7, "lon": 71.3}).json()
    assert j["results"][0]["district"] == "Barmer"


def test_ivr_webhook_twml(client):
    r = client.post("/ivr/voice", data={"CallSid": "CA123", "SpeechResult": ""})
    assert r.status_code == 200
    assert "<Say" in r.text and "SAHAYI" in r.text


def test_whatsapp_webhook(client):
    r = client.post("/whatsapp", data={"From": "whatsapp:+919876000004", "Body": "kisan"})
    assert r.status_code == 200
    assert "<Message>" in r.text


def test_nlu_status_endpoint(client):
    j = client.get("/api/nlu/status").json()
    assert j["languages"] == 12 and j["explainable"] is True


def test_impact_increments_after_application(client):
    before = client.get("/api/impact").json()["applications"]
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876500005"}).json()

    say("hindi"); say("bank"); say("nahi"); say("haan"); say("30")
    say("documents"); say("haan"); say("Demo Devi"); say("9876500005"); say("Bihar")
    after = client.get("/api/impact").json()["applications"]
    assert after == before + 1
