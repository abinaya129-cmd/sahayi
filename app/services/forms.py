"""Multilingual PDF form generator (fpdf2, no external services).

Produces a government-style application PDF stamped with the tracking ID,
document checklist and a Green Receipt footer showing carbon saved.
Unicode text uses a bundled font; core-font fallback keeps the demo alive
if the font file is missing (shaping is imperfect but layout holds).
"""
import os
from fpdf import FPDF

from ..languages import LANGUAGES
from ..config import settings

_FONT_DIRS = [
    os.path.join(os.path.dirname(__file__), "..", "..", "fonts"),
    os.environ.get("SAHAYI_FONT_DIR", ""),
    "/usr/share/fonts/truetype/noto",
    "C:\\Windows\\Fonts",
]

HELVETICA_SAFE = set(LANGUAGES)  # all codes


def _find_font() -> str | None:
    for d in _FONT_DIRS:
        if not d:
            continue
        cand = os.path.join(d, "NotoSans-Regular.ttf")
        if os.path.exists(cand):
            return cand
    return None


def _clean(text: str) -> str:
    """Strip glyphs the PDF core fonts cannot encode."""
    return text.encode("latin-1", "replace").decode("latin-1")


def generate_form_pdf(scheme: dict, language: str, profile: dict, tracking_id: str,
                      green: dict) -> str:
    """Build the application PDF, return its path."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    # Header band
    pdf.set_fill_color(255, 111, 0)  # saffron
    pdf.rect(0, 0, 210, 26, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, _clean("SAHAYI"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, _clean("Government Services in Your Language, One Voice Call Away"),
             new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.cell(0, 6, _clean(f"Green Receipt - {tracking_id}"), new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_text_color(0, 0, 0)

    lang_name = LANGUAGES.get(language, {}).get("name", language)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, _clean(f"{scheme['emoji']} {scheme['name']} - {scheme['form_title']}"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _clean(f"Language: {lang_name}   |   Benefit: {scheme['benefit_text']}"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Profile fields
    pdf.set_draw_color(180, 180, 180)
    pdf.set_font("Helvetica", "", 11)
    for key in ("name", "phone", "state", "district"):
        label = {"name": "Name", "phone": "Phone", "state": "State", "district": "District"}[key]
        pdf.cell(38, 8, _clean(label), border=1)
        pdf.cell(0, 8, _clean(str(profile.get(key, ""))), border=1, new_x="LMARGIN", new_y="NEXT")

    # Eligibility facts
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Eligibility (self-declared, voice-verified)", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for k, v in (profile.get("facts") or {}).items():
        vv = "Yes" if v in (True, "1", "yes", "haan") else ("No" if v in (False, "0", "no", "nahi") else str(v))
        pdf.cell(0, 6, _clean(f"  - {k}: {vv}"), new_x="LMARGIN", new_y="NEXT")

    # Document checklist
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Documents to carry", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for d in scheme["documents"]:
        pdf.cell(0, 6, _clean(f"  [ ] {d}"), new_x="LMARGIN", new_y="NEXT")

    # Green receipt footer
    pdf.ln(4)
    pdf.set_fill_color(226, 240, 224)
    pdf.set_text_color(27, 94, 32)
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 6, _clean(
        f"GREEN RECEIPT  |  CO2 saved: {green['co2_kg']} kg  |  Paper saved: "
        f"{green['paper_sheets']} sheets  |  Travel avoided: {green['km_avoided']} km"
    ), fill=True)
    pdf.set_text_color(0, 0, 0)

    os.makedirs(settings.PDF_DIR, exist_ok=True)
    path = os.path.join(settings.PDF_DIR, f"{tracking_id}.pdf")
    pdf.output(path)
    return path
