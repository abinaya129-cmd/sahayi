"""SAHAYI configuration. Everything degrades gracefully: no API keys = full demo mode."""
import os


class Settings:
    APP_NAME = "SAHAYI"
    VERSION = "1.0.0"
    TAGLINE = "Government Services in Your Language, One Voice Call Away"

    # --- Server ---
    HOST = os.getenv("SAHAYI_HOST", "0.0.0.0")
    PORT = int(os.getenv("SAHAYI_PORT", "8000"))
    BASE_URL = os.getenv("SAHAYI_BASE_URL", "http://localhost:8000")

    # --- Database ---
    # Vercel/lambda filesystems are read-only except /tmp - redirect there
    # automatically when running on Vercel (data resets per instance: fine
    # for a live demo, use a real DB for production).
    _on_vercel = bool(os.getenv("VERCEL")) or os.getenv("VERCEL_ENV") is not None
    DB_PATH = os.getenv("SAHAYI_DB", "/tmp/sahayi.db" if _on_vercel else "sahayi.db")

    # --- SMS: real Twilio only when BOTH creds and a sender number exist ---
    TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM = os.getenv("TWILIO_FROM_NUMBER", "")

    # --- Speech: real Google Cloud only when a service-account JSON is set ---
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")

    # --- Generated artifacts ---
    PDF_DIR = os.getenv("SAHAYI_PDF_DIR",
                        "/tmp/pdfs" if _on_vercel else "static/generated")

    # --- Seeded pilot metrics (demo baseline; live events add on top) ---
    SEED_WOMEN_HELPED = 1847
    SEED_BENEFITS_INR = 110_000_000   # Rs 1.1 crore
    SEED_CO2_KG = 50_000              # 50 tonnes
    SEED_KM_AVOIDED = 8_500

    # Carbon math per completed application (cited ranges, see README)
    CO2_PER_APP_KG = 32.0             # paper + travel + printing avoided
    PAPER_SHEETS_PER_APP = 20
    KM_AVOIDED_PER_APP = 42.0         # avg round trip to a govt office


settings = Settings()
