"""SAHAYI conversation state machine - the 'brain' every channel shares.

One orchestrator powers the dashboard, IVR and WhatsApp: greeting -> language
-> scheme -> interview -> verdict -> documents -> profile -> form PDF -> SMS
-> tracking -> CSC -> Green Receipt. Returning callers are greeted by name,
unclear answers are re-asked (never a dead end), the fraud-shield PSA plays on
first contact, and any 'SAH-XXXXXX' utterance fetches live status.
"""
import re
import uuid

from . import db, nlu
from .config import settings
from .languages import LANGUAGES, STRINGS, STRINGS_EN, normalize
from .rules import evaluate, reason_text
from .schemes import SCHEMES
from .services import impact, sms
from .services.answers import answer as kb_answer
from .services.answers import fallback as kb_fallback
from .services.answers import match as _kb_match_raw
from .services.csc import locate
from .services.forms import generate_form_pdf
from .services.tracking import _STEPS_EN

STATES = ["GREETING", "LANGUAGE", "SCHEME", "INTERVIEW", "VERDICT", "DOCS",
          "PROFILE", "FORM", "TRACKING", "CSC", "CLOSED"]


_TRACK_RE = re.compile(r"\bSAH[-\s]?[A-Z0-9]{6}\b", re.IGNORECASE)


def _t(key: str, _lang: str = "hi", **kw) -> str:
    src = STRINGS_EN if _lang == "en" else STRINGS
    return src.get(key, STRINGS.get(key, key)).format(**kw)


def kb_match(text: str):
    """Backward-compatible kb_match -> (key, entry)."""
    key, entry, _score = _kb_match_raw(text)
    return key, entry


def kb_score(text: str):
    """kb_match with the raw score, for KB-vs-scheme arbitration."""
    return _kb_match_raw(text)


def _match_language(text: str) -> str | None:
    norm = normalize(text)
    padded = f" {norm} "
    for code, meta in LANGUAGES.items():
        keys = {meta["name"].lower(), meta["native"], code}
        if any(k and (norm == k or f" {k} " in padded) for k in keys):
            return code
    aliases = {"hindi": "hi", "tamil": "ta", "telugu": "te", "kannada": "kn",
               "malayalam": "ml", "marathi": "mr", "gujarati": "gu",
               "bengali": "bn", "bangla": "bn", "punjabi": "pa", "urdu": "ur",
               "odia": "or", "assamese": "as", "english": "en"}
    for k, code in aliases.items():
        if f" {k} " in padded or norm == k:
            return code
    return None


def _fmt_benefit(inr: float) -> str:
    if inr >= 100000:
        return f"Rs {inr / 100000:g} lakh"
    return f"Rs {inr:,.0f}"


class Conversation:
    """Per-session dialogue orchestrator, persisted in the sessions table."""

    def __init__(self, session_id: str):
        self.sid = session_id
        s = db.get_session(session_id)
        if not s:
            s = db.new_session(phone="", channel="dashboard", language="hi")
            self.sid = s["id"]
        self.state = s["state"]
        self.language = s["language"]
        self.ctx = db.session_context(self.sid)
        self.phone = self.ctx.get("phone", "")

    # ------------------------------------------------------------- helpers
    def _reply(self, text: str, *, state: str | None = None, options: list | None = None,
               card: dict | None = None, chips: list | None = None, **extra) -> dict:
        if state:
            self.state = state
        db.update_session(self.sid, self.state, self.ctx, self.language)
        return {
            "session_id": self.sid,
            "state": self.state,
            "language": self.language,
            "text": text,
            "speak": text,
            "options": options or [],
            "card": card,
            "chips": chips or [],
            **extra,
        }

    def _remember(self, **kw) -> None:
        self.ctx.update(kw)

    # ------------------------------------------------------------- flow
    def start(self, phone: str = "") -> dict:
        self.state, self.language = "GREETING", "hi"
        self.ctx = {"phone": phone}
        user = db.get_user(phone) if phone else None
        hello = LANGUAGES["hi"]["hello"]
        if user and user.get("name"):
            text = _t("welcome_back", "hi", hello=hello, name=user["name"])
        else:
            text = _t("welcome", "hi", hello=hello)
        text += " Apni bhasha boliye ya chuniye. (Say 'English' for English.)"
        opts = [{"label": f"{LANGUAGES[c]['native']} ({LANGUAGES[c]['name']})",
                 "value": c, "action": "language"} for c in LANGUAGES]
        self._remember(fraud_shield_shown=True)
        return self._reply(text, state="LANGUAGE", options=opts,
                           fraud_shield=impact.fraud_shield())

    def handle(self, text: str) -> dict:
        """Single entry point for every user utterance in any state."""
        text = (text or "").strip()
        if not text:
            return self._reply(_t("not_understood", self.language))

        # Tracking ID spoken anywhere -> live status (wow beat)
        m = _TRACK_RE.search(text.upper())
        if m:
            self._remember(tracking_id=m.group(0).replace(" ", "-").upper())
            return self._reply_tracking()

        intent = nlu.detect_intent(text)

        # Smalltalk FIRST: a greeting must never be fuzzy-matched into 'help'
        # or a scheme. Exact-word greeting check, before any scoring.
        norm0 = f" {normalize(text)} "
        greetings = (" hello ", " hi ", " namaste ", " namaskar ", " hey ",
                     " namaskaram ", " vanakkam ")
        if any(g in norm0 for g in greetings) and intent not in ("yes", "no"):
            hello = LANGUAGES[self.language]["hello"]
            en = self.language == "en"
            body = f"{hello}! I am SAHAYI. " if en else f"{hello}! Main SAHAYI hoon. "
            if self.state == "INTERVIEW" and self.ctx.get("scheme"):
                slug = self.ctx["scheme"]
                qs = SCHEMES[slug]["questions_en"] if en and "questions_en" in SCHEMES[slug] else SCHEMES[slug]["questions"]
                i = int(self.ctx.get("q_index", 0))
                body += ("Back to my question: " if en else "Wapas sawal par: ") + _spoken(qs[i])
                return self._reply(body)
            return self._reply(body + _t("which_scheme", self.language),
                               state="SCHEME" if self.state != "INTERVIEW" else None,
                               options=_scheme_options(self.language),
                               chips=_scheme_chips())

        # Language switch mid-flow: 'english'/'हिन्दी'/'tamil' alone switches
        # the conversation language and re-asks the current question in it.
        bare_lang = _match_language(text)
        if bare_lang and bare_lang != self.language and len(normalize(text).split()) <= 2:
            self.language = bare_lang
            self._remember(language_chosen=bare_lang)
            en = bare_lang == "en"
            if self.state == "INTERVIEW" and self.ctx.get("scheme"):
                qs = SCHEMES[self.ctx["scheme"]]["questions_en"] if en and "questions_en" in SCHEMES[self.ctx["scheme"]] else SCHEMES[self.ctx["scheme"]]["questions"]
                i = int(self.ctx.get("q_index", 0))
                nq = _spoken(qs[i])
                self._remember(last_prompt=nq)
                return self._reply(_t("language_set", bare_lang,
                                      lang=LANGUAGES[bare_lang]["name"]) + " " +
                                   f"{'Question' if en else 'Sawal'} {i + 1}/{len(qs)}: {nq}")
            opts = (_scheme_options(bare_lang) if self.state in ("SCHEME", "VERDICT",
                                                                "DOCS", "TRACKING", "CLOSED")
                    else [])
            nxt = "SCHEME" if self.state == "LANGUAGE" else None
            return self._reply(_t("language_set", bare_lang,
                                  lang=LANGUAGES[bare_lang]["name"]),
                               state=nxt, options=opts)

        if intent == "repeat" and self.ctx.get("last_prompt"):
            return self._reply(self.ctx.get("last_prompt", _t("replay", self.language)))
        if intent == "help":
            return self._kb_or_fallback(text)

        handler = getattr(self, f"_handle_{self.state.lower()}", None)
        if handler is None:
            return self._handle_scheme(text)
        return handler(text)

    # ------------------------------------------------------------- states
    def _handle_greeting(self, text: str) -> dict:
        return self._handle_language(text)

    # ------------------------------------------------- general Q&A layer
    def _kb_or_fallback(self, text: str) -> dict:
        """Answer anything outside the 7 schemes: e-bike, phone, pension...
        Never a dead end - honest answer + chips back into the flow."""
        key, entry = kb_match(text)
        en = self.language == "en"
        if key:
            a = kb_answer(key, self.language)
            return self._reply(a["text"], card=a["card"], chips=a["chips"],
                               options=self._kb_options(a["chips"]),
                               kb_key=key)
        fb = kb_fallback(self.language)
        return self._reply(fb["text"], card=fb["card"], chips=fb["chips"],
                           options=self._kb_options(fb["chips"]))

    def _kb_options(self, chips: list) -> list:
        labels = {"scholarship": "🎓 Scholarship", "pension": "👴 Pension",
                  "ayushman": "🏥 Free treatment", "mudra loan": "💼 Business loan",
                  "ebike": "🛵 E-bike subsidy", "kisan": "🌾 PM-KISAN",
                  "gas": "🔥 Ujjwala gas", "ghar": "🏠 Awas ghar", "kaam": "👷 MGNREGA kaam"}
        out = []
        for c in chips:
            out.append({"label": labels.get(c, c.title()), "value": c, "action": "kb"})
        return out

    def _handle_language(self, text: str) -> dict:
        code = _match_language(text)
        if not code:
            # Voice UX: many users skip the language picker and just say what
            # they need ("kisan ke liye paisa" / "ration card kaise banega").
            # Same evidence arbitration as _handle_scheme - a strong KB topic
            # ('ration' 1.00) beats a fuzzy scheme maybe ('vishwakarma' 0.62).
            slug, score = nlu.detect_scheme_detail(text)
            key, _entry, kscore = kb_score(text)
            if slug and score >= 0.72 and score > kscore:
                return self._start_scheme(slug)
            if key:
                return self._kb_or_fallback(text)
            if slug:
                return self._start_scheme(slug)
            return self._reply(_t("not_understood", self.language) +
                               " Bhasha boliye - Hindi, Tamil, Telugu, English...")
        self.language = code
        self._remember(language_chosen=code)
        name = LANGUAGES[code]["name"]
        return self._reply(_t("language_set", self.language, lang=name), state="SCHEME",
                           options=_scheme_options(self.language),
                           chips=_scheme_chips())

    def _handle_scheme(self, text: str) -> dict:
        slug, score = nlu.detect_scheme_detail(text)
        key, _entry, kscore = kb_score(text)
        # Complaint markers: user reports a PROBLEM, not applying for a scheme
        # ('kisan ki KIST NAHI AYI' = DBT complaint, though 'kisan' is verbatim).
        complaint = any(w in normalize(text) for w in
                        ("nahi aya", "nahi ayi", "nahi mila", "kat gaya", "kat gayi",
                         "problem", "complaint", "shikayat", "NOT REACHED",
                         "not received", "stolen"))
        # Arbitrate by evidence. A verbatim scheme keyword wins ties;
        # complaints always defer to the KB.
        slug_kw = _exact_scheme_keyword(text)
        if complaint and key:
            return self._kb_or_fallback(text)
        if slug and score >= 0.72 and (score > kscore or (score == kscore and slug_kw)):
            return self._start_scheme(slug)
        if key and kscore >= max(score, 0.72):
            return self._kb_or_fallback(text)
        if slug and score >= 0.72:
            return self._start_scheme(slug)
        return self._kb_or_fallback(text)

    def _start_scheme(self, slug: str) -> dict:
        scheme = SCHEMES[slug]
        en = self.language == "en"
        qs = scheme["questions_en"] if en and "questions_en" in scheme else scheme["questions"]
        benefit = scheme["benefit_en"] if en and "benefit_en" in scheme else scheme["benefit_text"]
        q0 = _spoken(qs[0])
        self._remember(scheme=slug, q_index=0, facts={}, last_prompt=q0)
        return self._reply(
            f"{scheme['emoji']} {scheme['name']} - {benefit}. "
            f"{'Question' if en else 'Sawal'} 1/{len(qs)}: {q0}",
            state="INTERVIEW")

    def _handle_interview(self, text: str) -> dict:
        slug = self.ctx["scheme"]
        scheme = SCHEMES[slug]
        en = self.language == "en"
        qs = scheme["questions_en"] if en and "questions_en" in scheme else scheme["questions"]
        i = int(self.ctx.get("q_index", 0))
        q = qs[i]
        if q["type"] == "bool":
            ans = nlu.detect_yes_no(text)
            if ans is None:
                # Ask-anything mid-interview: answer the side question, then
                # re-ask the SAME question (never advances on confusion)
                key, _ = kb_match(text)
                if key:
                    a = kb_answer(key, self.language)
                    return self._reply(a["text"] + "\n\n" +
                                       ("Back to my question: " if en else "Wapas sawal par: ") +
                                       _spoken(q),
                                       card=a["card"], chips=a["chips"],
                                       options=self._kb_options(a["chips"]))
                return self._reply(_t("yes_no", self.language) + (" Say again please." if en else " Phir boliye."))
            val = ans
        else:
            val = nlu.extract_number(text)
            if val is None:
                return self._reply("Your age please - for example 26." if en
                                   else "Umar bataiye - jaise 'chhabbis' ya 26.")
            val = max(q.get("min", 1), min(q.get("max", 99), val))
        facts = dict(self.ctx.get("facts") or {})
        facts[q["id"]] = val
        self._remember(facts=facts)

        nxt = i + 1
        if nxt < len(qs):
            nq = _spoken(qs[nxt])
            self._remember(q_index=nxt, last_prompt=nq)
            return self._reply(f"{'Question' if en else 'Sawal'} {nxt + 1}/{len(qs)}: {nq}")
        eligible, failures = evaluate(scheme["rules"], facts)
        self._remember(eligible=eligible, failures=failures)
        reasons = "; ".join(reason_text(f, self.language) for f in failures)
        if eligible:
            body = _t("eligible", self.language, scheme=scheme["name"],
                      benefit=_fmt_benefit(scheme["benefit_inr"]))
            card = {"type": "success", "emoji": scheme["emoji"], "title": scheme["name"],
                    "facts": ["Benefit: " + _fmt_benefit(scheme["benefit_inr"]),
                              "All conditions met" if en else "Sabhi shartein puri hui"],
                    "source": "Next: documents, form, SMS" if en else "Aage: documents, form, SMS"}
        else:
            body = _t("not_eligible", self.language, reason=reasons)
            if not en:
                body += " Chinta mat kijiye - doosri yojana dekh lein."
            card = {"type": "reject", "emoji": "🤝", "title": scheme["name"],
                    "facts": [r.strip() for r in reasons.split(";")] if failures else [],
                    "source": ("Try another scheme - I will help" if en
                               else "Doosri yojana try kariye - main madad karungi")}
        chips = ["documents", "other scheme"] if eligible else ["kisan", "gas", "kaam", "scholarship"]
        return self._reply(body, state="VERDICT", card=card, chips=chips, options=[
            {"label": "Documents & continue" if en else "Documents sun kar aage badhein",
             "value": "docs", "action": "docs"},
            {"label": "Another scheme" if en else "Doosri yojana dekhein",
             "value": "other", "action": "scheme"}],
            eligible=eligible)

    def _handle_verdict(self, text: str) -> dict:
        en = self.language == "en"
        norm = normalize(text)
        key, _ = kb_match(text)
        if key and not ("doc" in norm or nlu.detect_yes_no(text) is True):
            return self._kb_or_fallback(text)
        if ("doc" in norm or "aage" in norm or "haan" in norm or "yes" in norm
                or nlu.detect_yes_no(text) is True):
            scheme = SCHEMES[self.ctx["scheme"]]
            card = {"type": "info", "emoji": "📋", "title": scheme["name"],
                    "facts": list(scheme["documents"]),
                    "source": "Carry originals + one photocopy each" if en
                              else "Original + ek photocopy lekar jaiye"}
            return self._reply(_t("docs_msg", self.language,
                                  docs=", ".join(scheme["documents"])),
                               state="DOCS", card=card, options=_form_options(self.language))
        return self._reply(_t("which_scheme", self.language), state="SCHEME",
                           options=_scheme_options(self.language), chips=_scheme_chips())

    def _handle_docs(self, text: str) -> dict:
        en = self.language == "en"
        norm = normalize(text)
        if "form" in norm or "bana" in norm or nlu.detect_yes_no(text) is True:
            return self._ask_name()
        key, _ = kb_match(text)
        if key:
            return self._kb_or_fallback(text)
        return self._reply("Shall I fill your form and make the PDF? Say yes." if en
                           else "Kya main aapka form bharkar PDF bana doon? Boliye 'haan'.",
                           options=_form_options(self.language))

    def _ask_name(self) -> dict:
        en = self.language == "en"
        return self._reply("First, what is your name?" if en
                           else "Shuruaat mein apna naam bataiye.",
                           state="PROFILE", profile_step="name")

    def _handle_profile(self, text: str) -> dict:
        en = self.language == "en"
        step = self.ctx.get("profile_step", "name")
        val = text.strip()
        if step == "name":
            self._remember(p_name=val.title(), profile_step="phone")
            return self._reply("Thank you. Now your mobile number (10 digits)." if en
                               else "Shukriya. Ab mobile number bataiye (10 digit).")
        if step == "phone":
            digits = re.sub(r"\D", "", text)
            if len(digits) < 10:
                return self._reply("Please give a 10-digit number - like 9 8 7 6 5 4 3 2 1 0." if en
                                   else "10 digit ka number bataiye - jaise 9 8 7 6 5 4 3 2 1 0.")
            self._remember(p_phone=digits[-10:], profile_step="state")
            return self._reply("Your state / district - like 'Rajasthan Barmer'?" if en
                               else "Aapka rajya / district bataiye - jaise 'Rajasthan Barmer'.")
        # state -> generate form + SMS
        self._remember(p_state=val.title(), profile_step="done")
        return self._generate_form()

    def _generate_form(self) -> dict:
        slug = self.ctx["scheme"]
        scheme = SCHEMES[slug]
        profile = {"name": self.ctx.get("p_name", ""), "phone": self.ctx.get("p_phone", ""),
                   "state": self.ctx.get("p_state", ""), "district": "",
                   "facts": self.ctx.get("facts", {})}
        phone = profile["phone"] or "9999999999"
        # One authoritative record -> PDF, SMS and tracking all share the ID
        rec = db.create_application(phone, slug, self.language, profile, True,
                                    scheme["benefit_inr"], "")
        tracking = rec["tracking_id"]
        green = impact.green_receipt(phone, slug, tracking, scheme["benefit_inr"])
        pdf_path = generate_form_pdf(scheme, self.language, profile, tracking, green)
        db.set_application_pdf(tracking, pdf_path)
        db.set_application_status(tracking, "FORM_GENERATED")
        if profile["name"]:
            db.upsert_user(phone, name=profile["name"], language=self.language)
        sms.send_sms(phone, f"SAHAYI: {scheme['name']} form ready. ID: {tracking}. "
                            f"PDF: {settings.BASE_URL}/pdf/{tracking}.pdf - Green receipt: "
                            f"{green['co2_kg']}kg CO2 saved. Bharosa kariye, SAHAYI.")
        sms.send_sms(phone, f"Tracking ID: {tracking}. Status sunne ke liye boliye ya "
                            f"SMS kariye 'SAH' + ID.")
        self._remember(tracking_id=tracking)
        return self._reply_tracking()

    def _reply_tracking(self) -> dict:
        tid = self.ctx.get("tracking_id", "")
        st = _status_payload(tid)
        if st:
            text = (_t("form_ready", self.language) + " " +
                    _t("tracking_msg", self.language, tid=tid) + " " +
                    _STEPS_EN.get(st["status"], ""))
        else:
            text = _t("form_ready", self.language) + (
                " Tracking ID galat hai, dobara boliye.")
        return self._reply(text, state="TRACKING", options=_post_form_options(),
                           tracking=st)

    def _handle_tracking(self, text: str) -> dict:
        en = self.language == "en"
        norm = normalize(text)
        if "csc" in norm or "center" in norm or "office" in norm:
            return self._reply("Your state or district? I will find the nearest CSC." if en
                               else "Apna rajya ya district bataiye - main sabse najdiki "
                                    "CSC dhoondhungi.", state="CSC")
        key, _ = kb_match(text)
        if key:
            return self._kb_or_fallback(text)
        if "sms" in norm or "message" in norm or nlu.detect_yes_no(text) is True:
            return self._reply("SMS sent, with your Green Receipt. Anything else? Say 'CSC' to find a centre." if en
                               else "SMS bhej diya. Green receipt bhi usme hai. "
                                    "Kuch aur? 'CSC' boliye toh najdiki kendra dhoondhungi.",
                               state="CLOSED")
        return self._reply("Say 'CSC' (find a centre) or 'thank you' to finish." if en
                           else "Boliye 'CSC' (kendra dhoondo) ya 'dhanyavaad' (band kariye).")

    def _handle_csc(self, text: str) -> dict:
        en = self.language == "en"
        res = locate(text)
        c = res["results"][0]
        self._remember(csc=c["name"])
        sms.send_sms(self.ctx.get("phone", "9999999999"),
                     f"SAHAYI: Nearest CSC - {c['name']}, {c['address']}, "
                     f"{c['district']}. Open 9am-6pm.")
        dist = c.get("distance_km")
        where = (f"in your district ({c['distance_km']} km)" if dist == 0
                 else f"- {dist} km away" if en
                 else f"({c['distance_km']} km)")
        return self._reply(
            (f"Nearest CSC: {c['name']}, {c['address']}, {c['district']} {where}. "
             "Address sent by SMS. Anything else?" if en else
             f"Najdiki CSC: {c['name']}, {c['address']}, {c['district']} {where}. "
             "Address SMS par bhej diya. Aur madad?"),
            state="CLOSED", csc=res["results"])

    # exported for API layer
    def options_for_state(self) -> list:
        return {
            "LANGUAGE": _language_options(),
            "SCHEME": _scheme_options(self.language),
            "TRACKING": _post_form_options(self.language),
        }.get(self.state, [])


def _spoken(q: dict) -> str:
    return q["q"]


def _exact_scheme_keyword(text: str) -> str | None:
    """True verbatim scheme keyword in the utterance (not fuzzy)."""
    from .languages import content_tokens
    toks = set(content_tokens(text))
    for kws in nlu.LEXICON["schemes"].values():
        for kw in kws:
            if " " not in kw and kw.lower() in toks:
                return kw
    return None


def _language_options():
    return [{"label": f"{LANGUAGES[c]['native']} ({LANGUAGES[c]['name']})",
             "value": c, "action": "language"} for c in LANGUAGES]


def _scheme_options(lang: str = "hi"):
    return [{"label": f"{s['emoji']} {s['name']} - {_fmt_benefit(s['benefit_inr'])}",
             "value": slug, "action": "scheme"} for slug, s in SCHEMES.items()]


def _scheme_chips():
    return ["kisan", "ghar", "gas", "kaam", "scholarship", "pension", "ebike"]


def _form_options(lang: str = "hi"):
    return [{"label": "Yes, make my form (PDF + SMS)" if lang == "en"
                    else "Haan, form banao (PDF + SMS)",
             "value": "form", "action": "form"}]


def _post_form_options(lang: str = "hi"):
    en = lang == "en"
    return [{"label": "Find nearest CSC" if en else "Najdiki CSC dhoondo",
             "value": "csc", "action": "csc"},
            {"label": "Speak status" if en else "Status sunao",
             "value": "status", "action": "status"}]


def _status_payload(tid: str):
    from .services.tracking import status_of
    return status_of(tid)
