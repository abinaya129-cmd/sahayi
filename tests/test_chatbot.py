"""Chatbot breadth tests: SAHAYI must answer anything a user throws at her."""
import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["SAHAYI_DB"] = "test_chatbot.db"

from app.main import app  # noqa: E402
from app import db  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def _db():
    if os.path.exists("test_chatbot.db"):
        os.remove("test_chatbot.db")
    db.init_db()
    yield
    db.close()
    if os.path.exists("test_chatbot.db"):
        os.remove("test_chatbot.db")


@pytest.fixture()
def client():
    return TestClient(app)


def _session(client):
    j = client.post("/api/start").json()
    sid = j["session_id"]

    def say(text):
        return client.post("/api/message",
                           data={"session_id": sid, "text": text, "phone": "9876555000"}).json()
    return say


def test_document_services(client):
    say = _session(client)
    say("hindi")
    for utter, expect in [
        ("ration card kaise banega", "anaj"),
        ("aadhaar update karna hai", "Aadhaar Seva Kendra"),
        ("pan card chahiye", "e-PAN"),
        ("voter id banwani", "voters.eci.gov.in"),
        ("passport lagwana hai", "passportindia"),
    ]:
        j = say(utter)
        assert expect.lower() in j["text"].lower(), f"{utter} -> {j['text'][:80]}"
        assert j["card"]["type"] == "info"


def test_farmer_services(client):
    say = _session(client)
    say("hindi")
    j = say("kcc chahiye")
    assert "Kisan Credit" in j["text"] or "4%" in j["text"]
    j = say("fasal barbadi ho gayi")
    assert "PMFBY" in j["text"] or "BEEMA" in j["text"]
    j = say("mitti ki jaanch")
    assert "Soil Health" in j["text"]


def test_safety_helplines(client):
    say = _session(client)
    say("hindi")
    j = say("madad karo khatra hai")
    assert "112" in j["text"] and "181" in j["text"]
    j = say("mera otp kat gaya")
    assert "1930" in j["text"]


def test_dbt_and_buses(client):
    say = _session(client)
    say("hindi")
    j = say("kisan ki kist nahi ayi")
    assert "dbtbharat" in j["text"].lower()
    j = say("bus me sawari free hoti hai kya")
    assert "Shakti" in j["text"] or "bus" in j["text"].lower()


def test_question_words_do_not_match(client):
    say = _session(client)
    say("hindi")
    j = say("weather kaisa hai")
    # honest fallback, never a wrong confident answer
    assert "daayre" in j["text"] or "PURI madad" in j["text"]
    assert j["card"]["type"] == "fallback"


def test_smalltalk_reanchors(client):
    say = _session(client)
    say("hindi")
    j = say("hello")
    assert "SAHAYI" in j["text"]
    assert j["state"] == "SCHEME"


def test_mid_interview_side_question(client):
    say = _session(client)
    say("hindi")
    say("kisan")
    j = say("ration card kya hai")   # asks something else mid-interview
    assert "anaj" in j["text"].lower()
    assert "Wapas sawal par" in j["text"] or "Kya aap ya aapke parivar" in j["text"]
    j2 = say("haan")   # interview continues normally afterwards
    assert j2["state"] == "INTERVIEW"


def test_kb_without_language_set(client):
    """Judges type straight into the greeting - KB must answer there too."""
    say = _session(client)
    j = say("ration card kaise banega")   # no language chosen yet!
    assert "anaj" in j["text"].lower()
    j = say("fasal barbadi ho gayi")
    assert "PMFBY" in j["text"] or "BEEMA" in j["text"]


def test_english_kb_answers(client):
    say = _session(client)
    say("english")
    j = say("i want an e bike")
    assert "PM E-DRIVE" in j["text"]
    assert "Source:" in j["text"]
    j = say("emergency")
    assert "112" in j["text"]
