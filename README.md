# 🌿 SAHAYI — सहायी (The Helper)

**Government Services in Your Language, One Voice Call Away.**

A voice-first, 13-language assistant (12 Indian languages + English) that takes a woman from
*"kisan ke liye paisa chahiye"* to an approved government scheme application — including the
filled PDF, the SMS confirmation, the nearest CSC, and a **Green Receipt** proving the carbon
saved — in under 3 minutes, on a ₹1,000 phone.

**Ask Anything:** outside the 7 full-application schemes, SAHAYI answers questions about
e-bike subsidies, free phones (and scam warnings), scholarships, pensions, solar, free
treatment, drones and business loans — honestly, with official sources, in both Hindi and
English. No dead ends, ever.

---

## ⚡ 60-second summary (for judges)

| | |
|---|---|
| **Who** | 400M Indian women locked out of govt schemes by language + tech + distance |
| **What** | Voice AI that interviews, checks eligibility, fills the form, sends SMS, tracks status |
| **Ask** | Ask-Anything knowledge base: e-bikes, phones, scholarships, pensions — with sources |
| **Wow #1** | One brain powers IVR calls, WhatsApp **and** a live web dashboard — same conversation, same SMS |
| **Wow #2** | **Green Receipt**: every application stamps 32 kg CO₂ / 20 sheets / 42 km saved onto the PDF |
| **Wow #3** | **Fraud Shield**: warns about OTP scams on first contact — govt tech that *protects* |
| **Wow #4** | Speak a Tracking ID (`SAH-XXXXXX`) anytime, any channel → live status |
| **Zero keys** | Runs fully offline-demoable: browser voice, mock SMS inbox, local PDF engine |

## 🧠 Why it wins (the USPs, stacked)

1. **One brain, three channels.** The same state machine drives a phone call (Twilio IVR),
   WhatsApp, and the dashboard. During Q&A, switch channels live — nothing else to demo.
2. **Never a dead end.** Rejected applicants are re-routed to alternative schemes automatically,
   in their own language. Most hacks dead-end at "not eligible."
3. **Green Receipt.** Sustainability is not a slide here — it's a *receipt*, cryptographically
   simple, auditable, printed on every form. Sourced numbers: 20 sheets, 42 km, 32 kg CO₂ per application.
4. **Fraud Shield.** 1930 cyber-helpline PSA built into the greeting. First govt-tech project
   that *fights* the scams plaguing its own users.
5. **Explainable NLU.** A transparent fuzzy-lexicon engine (12 scripts, ~200 keywords) with an
   honest `/api/nlu/status` endpoint describing the IndicBERT upgrade path. Judges can't
   black-box-shame you.
6. **Returning-caller memory.** Come back by phone → greeted by name. Dignity, not demos.

## 🚀 Run it (60 seconds)

```bash
./run.sh                      # or: pip install -r requirements.txt && uvicorn app.main:app --reload
```

Open the dashboard → pick a language (English included) or tap **▶️ Auto-play Lakshmi's journey**.
Quick chips let you ask about **e-bikes, scholarships, pensions**, then jump into a full scheme
application — exactly the flow judges will test.

- 🎤 Mic button uses Chrome/Edge built-in speech recognition (no keys, no cost).
- 📞 Every "SMS" the system sends lands on the **Judge's Phone** on the right.
- 🌱 Impact Wall updates live as applications complete.
- ⚙️ Hit **Simulate govt verification** to walk the tracking pipeline to APPROVED on stage.

## 🔌 API surface (all channels)

| Endpoint | Purpose |
|---|---|
| `POST /api/start` | Begin conversation (greeting + language picker) |
| `POST /api/message` | Any utterance, any state — the single brain entry point |
| `POST /api/voice` | Audio upload → Google STT → brain (auto-enabled with creds) |
| `GET /api/impact` | Green Receipt totals (seeded pilot + live events) |
| `GET /api/sms/{phone}` | Mock inbox powering the on-screen phone |
| `GET /api/track/{tid}` | Live application status |
| `POST /api/track/{tid}/advance` | Demo control: move govt pipeline |
| `GET /api/csc?loc=madurai` | Nearest Common Service Centre |
| `GET /api/nlu/status` | Explainability report for judges |
| `POST /ivr/voice`, `/ivr/sms` | Twilio IVR + SMS webhooks (TwML) |
| `POST /whatsapp` | Twilio WhatsApp webhook (TwML) |
| `GET /pdf/{tid}.pdf` | The generated application PDF |

## 🏗 Architecture

```
        ┌────────────┐   ┌────────────┐   ┌──────────────┐
        │ Twilio IVR │   │  WhatsApp  │   │   Dashboard  │
        └─────┬──────┘   └─────┬──────┘   └──────┬───────┘
              └──────────┬─────┴──────────────────┘
                         ▼
              ┌─────────────────────┐
              │  Conversation Brain │  state machine: greeting → language →
              │  (app/conversation) │  scheme → interview → verdict → docs →
              └──────────┬──────────┘  profile → form → tracking → CSC
                         ▼
   ┌─────────┬────────────┬──────────┬───────────┬──────────────┐
   │ NLU     │ Rules      │ Forms    │ Tracking  │ Green        │
   │ fuzzy   │ engine     │ PDF      │ SAH-XXXX  │ Receipts     │
   │ 12-lang │ (data)     │ engine   │ pipeline  │ + Fraud Wall │
   └─────────┴────────────┴──────────┴───────────┴──────────────┘
                         ▼
              sqlite (zero-dep) → mock SMS inbox / Twilio when keyed
```

**Graceful degradation:** set `TWILIO_*` env vars → real SMS to judges' phones.
Set `GOOGLE_APPLICATION_CREDENTIALS` → Google STT/TTS. Without either, the demo
still runs 100% (browser voice + on-screen phone). **A live demo that cannot fail.**

## 🎤 The 3-minute pitch (what to say on stage)

**0:00 — Lakshmi (30s).** *"Lakshmi, a farmer's widow in Barmer, lost ₹50,000 in benefits
she was entitled to — because every form spoke English and every office was 42 km away.
She's one of 400 million women. SAHAYI is her helper."*

**0:30 — Live call (90s).** Open the dashboard. Tap **Auto-play**. Narrate while it runs:
she speaks Hindi → SAHAYI interviews her → **PDF generated** → watch the **Judge's Phone**
get the SMS with the tracking ID → **Impact Wall ticks up**. Then speak the tracking ID
back to SAHAYI and show live status. Then hit **advance** → APPROVED.

**2:00 — Architecture (30s).** One brain, three channels (call + WhatsApp + web).
Explainable NLU, no black boxes. Zero API keys to demo; production upgrades are env vars.

**2:30 — Green Receipt close (30s).** *"Every application prints its own environmental
savings: 32 kg CO₂, 20 sheets, 42 km not traveled. A million Lakshmis = 32,000 tonnes of
CO₂ and ₹6,000 crore in unlocked benefits. SAHAYI doesn't just fill forms — it leaves a
receipt of dignity."*

### Backup plans (never freeze on stage)
- Mic fails → type the script lines; the flow is identical.
- Internet dies → the entire stack is local; nothing external is called in demo mode.
- Judge asks "is the NLU real?" → show `/api/nlu/status` and explain the IndicBERT path.

## ☁️ Deploy

**Vercel (easiest — free):**
```bash
# after pushing to GitHub: vercel.com → Add New → Project → import the repo → Deploy
# or from the project folder:
npx vercel
```
`vercel.json` + `api/index.py` are ready. Note: serverless storage is ephemeral
(demo data resets); set Twilio/Google env vars in Project Settings if you want
production integrations.

**Google Cloud Run (persistent disk):**
```bash
gcloud run deploy sahayi \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated
```

## 🧪 Tests

```bash
python -m pytest tests/ -q     # 9 end-to-end tests = the stage journey
```

## 📁 Structure

```
app/
  main.py          FastAPI: REST + IVR + WhatsApp + PDF serving
  conversation.py  THE BRAIN: state machine shared by all channels
  nlu.py           fuzzy 12-language intent/scheme matcher
  rules.py         declarative eligibility engine (data, not code)
  schemes.py       7 schemes × rules × questions × documents
  languages.py     13 languages (incl. English), greetings, lexicons, strings
  services/answers.py  Ask-Anything KB: e-bike, phone, scholarship, pension, solar, Ayushman…
  services/        sms · impact (Green Receipts) · forms (PDF) ·
                   csc locator · tracking · speech
  db.py            zero-dependency sqlite persistence
static/index.html  interactive dashboard: state rail, quick chips, rich cards, typing
                   indicator, SMS phone, Impact Wall, auto-demo
tests/test_e2e.py  14 end-to-end tests incl. English flow + Ask-Anything KB
```

---

*SAHAYI — because "not eligible" should never be the last word a woman hears.*
