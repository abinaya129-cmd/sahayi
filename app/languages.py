"""12 Indian languages: names, hello-strings and NLU lexicons.

LANGUAGES drives /languages endpoint and the dashboard picker.
HELLO drives TTS + spoken greetings.
LEXICON drives fuzzy intent + scheme matching across all languages
(mostly transliterated English + the user's own script - matching is
script-agnostic at the character level via normalize()).
"""
import unicodedata

LANGUAGES = {
    "en": {"name": "English", "native": "English", "hello": "Hello"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "hello": "नमस्ते"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "hello": "வணக்கம்"},
    "te": {"name": "Telugu", "native": "తెలుగు", "hello": "నమస్కారం"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "hello": "ನಮಸ್ಕಾರ"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "hello": "നമസ്കാരം"},
    "mr": {"name": "Marathi", "native": "मराठी", "hello": "नमस्कार"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "hello": "નમસ્તે"},
    "bn": {"name": "Bengali", "native": "বাংলা", "hello": "নমস্কার"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "hello": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ"},
    "ur": {"name": "Urdu", "native": "اردو", "hello": "سلام"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "hello": "ନମସ୍କାର"},
    "as": {"name": "Assamese", "native": "অসমীয়া", "hello": "নমস্কাৰ"},
}

# Template-strings for the conversation layer (Hindi default). {x} placeholders.
STRINGS = {
    "welcome": "{hello}! Main SAHAYI hoon. Sarkari seva ke liye apni zaroorat boliye.",
    "welcome_back": "{hello} {name}! Aap wapas aayi - SAHAYI yaad hai. Kya seva chahiye?",
    "heard_you": "Aapne kaha: \"{text}\"",
    "which_scheme": "Kaunsi yojana? Boliye - jaise kisan, ghar, gas, bank, kaam.",
    "not_understood": "Maaf kijiye, samajh nahi aaya. Phir boliye.",
    "language_set": "Theek hai, aage {lang} mein baat karenge.",
    "ask_question": "Sawal {n}/{total}: {q}",
    "yes_no": "Haan ya nahi mein jawab dijiye.",
    "eligible": "Badhai ho! Aap {scheme} ke liye PAATRI hain. Laabh: {benefit}",
    "not_eligible": "Aap abhi is yojana ke liye paatri nahi hain. Wajah: {reason}",
    "docs_msg": "Zaroori documents: {docs}",
    "form_ready": "Aapka form taiyaar hai. PDF link SMS mein bhej diya.",
    "sms_sent": "SMS bhej diya {phone} par.",
    "tracking_msg": "Tracking ID: {tid}. Kisi bhi CSC par dikhaiye.",
    "replay": "Pichhla jawab dohraane ke liye 9 dabaiye ya boliye 'dobara'.",
    "fraud": "Dhyan dijiye: Sarkar kabhi OTP ya paisa nahi maangti. Yeh call SAHAYI se hai.",
}

# English overrides - SAHAYI's full personality in English. Any key not
# listed here falls back to the Hindi default (graceful, never empty).
STRINGS_EN = {
    "welcome": "{hello}! I am SAHAYI, your helper. Tell me which government service you need.",
    "welcome_back": "{hello} {name}! Welcome back - SAHAYI remembers you. What do you need today?",
    "which_scheme": "Which scheme? Say for example - farmer, house, gas, bank, work.",
    "not_understood": "Sorry, I did not understand. Please say it again.",
    "language_set": "Great, we will continue in {lang}.",
    "yes_no": "Please answer yes or no.",
    "eligible": "Congratulations! You are ELIGIBLE for {scheme}. Benefit: {benefit}",
    "not_eligible": "You are not eligible for this scheme right now. Reason: {reason}",
    "docs_msg": "Documents you need: {docs}",
    "form_ready": "Your form is ready. I have sent the PDF link by SMS.",
    "sms_sent": "SMS sent to {phone}.",
    "tracking_msg": "Tracking ID: {tid}. Show it at any CSC centre.",
    "replay": "Say 'repeat' anytime to hear that again.",
    "fraud": "Remember: the government never asks for OTP or money. This call is from SAHAYI.",
}

# Tamil + Telugu: the most-heard strings so a Tamil user never hears Hindi.
# Missing keys fall back to Hindi (graceful, never empty).
STRINGS_TA = {
    "welcome": "{hello}! நான் SAHAYI. எந்த அரசு திட்டம் வேண்டும் சொல்லுங்கள்.",
    "welcome_back": "{hello} {name}! மீண்டும் வருகைக்கு வரவேற்கிறேன். என்ன உதவி வேண்டும்?",
    "which_scheme": "எந்த திட்டம்? சொல்லுங்கள் - விவசாயம், வீடு, கேஸ், வங்கி, வேலை.",
    "not_understood": "மன்னிக்கவும், புரியவில்லை. மீண்டும் சொல்லுங்கள்.",
    "language_set": "சரி, இனி {lang} -ல் பேசுவோம்.",
    "yes_no": "ஆம் அல்லது இல்லை என பதில் சொல்லுங்கள்.",
    "eligible": "வாழ்த்துகள்! நீங்கள் {scheme} -க்கு தகுதியுடையவர். பலன்: {benefit}",
    "not_eligible": "இந்த திட்டத்திற்கு தற்போது தகுதி இல்லை. காரணம்: {reason}",
    "docs_msg": "தேவையான ஆவணங்கள்: {docs}",
    "form_ready": "உங்கள் விண்ணப்பம் தயார். PDF லிங்க் SMS-ல் அனுப்பிவிட்டேன்.",
    "tracking_msg": "கண்காணிப்பு எண்: {tid}. எந்த CSC-லும் காட்டுங்கள்.",
    "replay": "மீண்டும் கேட்க 'repeat' என்று சொல்லுங்கள்.",
    "fraud": "எச்சரிக்கை: அரசு ஒருபோதும் OTP அல்லது பணம் கேட்காது. இது SAHAYI அழைப்பு.",
}

STRINGS_TE = {
    "welcome": "{hello}! నేను SAHAYI. ఏ ప్రభుత్వ పథకం కావాలో చెప్పండి.",
    "welcome_back": "{hello} {name}! తిరిగి రావడం చాలా సంతోషం. ఏమి సహాయం కావాలి?",
    "which_scheme": "ఏ పథకం? చెప్పండి - వ్యవసాయం, ఇల్లు, గ్యాస్, బ్యాంక్, పని.",
    "not_understood": "క్షమించండి, అర్థం కాలేదు. మళ్లీ చెప్పండి.",
    "language_set": "సరే, ఇకపై {lang}లో మాట్లాడతాం.",
    "yes_no": "అవును లేదా కాదు అని చెప్పండి.",
    "eligible": "అభినందనలు! మీరు {scheme}కి అర్హులు. లబ్ధి: {benefit}",
    "not_eligible": "ఈ పథకానికి ప్రస్తుతం అర్హత లేదు. కారణం: {reason}",
    "docs_msg": "కావలసిన డాక్యుమెంట్లు: {docs}",
    "form_ready": "మీ ఫారం సిద్ధం. PDF లింక్ SMSలో పంపాను.",
    "tracking_msg": "ట్రాకింగ్ ID: {tid}. ఏ CSCలో అయినా చూపించండి.",
    "replay": "మళ్లీ వినడానికి 'repeat' అని చెప్పండి.",
    "fraud": "జాగ్రత్త: ప్రభుత్వం ఎప్పుడూ OTP లేదా డబ్బు అడగదు. ఇది SAHAYI కాల్.",
}


def strings_for(lang: str) -> dict:
    """Best string table for a language, Hindi as final fallback."""
    return {"en": STRINGS_EN, "ta": STRINGS_TA, "te": STRINGS_TE}.get(lang, STRINGS)

# Fuzzy lexicons. Keys: intents & scheme slugs. Values: keyword variants
# across scripts + romanizations. Matched with token-level fuzzy ratio.
LEXICON = {
    "schemes": {
        "pm_kisan": ["kisan", "किसान", "farmer", "खेत", "kheti", "రైతు", "விவசாய", "ರೈತ", "কৃষক", "ખેડૂત", "ਕਿਸਾਨ", "کسان", "କୃଷକ", "কৃষক"],
        "pmjdy": ["bank", "बैंक", "khata", "खाता", "account", "கணக்கு", "ఖాతా", "ಖಾತೆ", "ব্যাঙ্ক", "બેંક", "ਬੈਂਕ", "بینک", "ବ୍ୟାଙ୍କ", "বেংক"],
        "ujjwala": ["gas", "गैस", "lpg", "chulha", "चूल्हा", "சமையல்", "గ్యాస్", "ಅನಿಲ", "গ্যাস", "ગેસ", "ਗੈਸ", "گیس", "ଗ୍ୟାସ୍", "গেছ"],
        "awas": ["ghar", "घर", "makan", "मकान", "house", "வீடு", "ఇల్లు", "ಮನೆ", "বাড়ি", "ઘર", "ਘਰ", "گھر", "ଘର", "ঘৰ"],
        "mgnrega": ["kaam", "काम", "rozgar", "रोजगार", "job", "வேலை", "పని", "ಕೆಲಸ", "কাজ", "કામ", "ਕੰਮ", "کام", "କାମ", "কাম"],
        "vishwakarma": ["karigar", "कारीगर", "artisan", "लोहार", "मोची", "கைவினை", "కళాకారుడు", "ಕುಶಲಕರ್ಮಿ", "শিল্পী", "કારીગર", "ਕਾਰੀਗਰ", "کاریگر", "କାରିଗର", "কাৰিগৰ"],
        "skill_india": ["skill", "स्किल", "training", "प्रशिक्षण", "பயிற்சி", "శిక్షణ", "ತರಬೇತಿ", "প্রশিক্ষণ", "તાલીમ", "ਸਿਖਲਾਈ", "تربیت", "ତାଲିମ", "প্ৰশিক্ষণ"],
    },
    "intents": {
        "yes": ["haan", "हाँ", "ha", "yes", "हो", "ஆம்", "అవును", "ಹೌದು", "হ্যাঁ", "હા", "ਹਾਂ", "ہاں", "ହଁ", "হয়"],
        "no": ["nahi", "नहीं", "no", "இல்லை", "కాదు", "ಇಲ್ಲ", "না", "ના", "ਨਹੀਂ", "نہیں", "ନା", "নহে"],
        "repeat": ["dobara", "दोबारा", "repeat", "फिर", "மீண்டும்", "మళ్లీ", "ಪುನಃ", "আবার", "ફરી", "ਦੁਬਾਰਾ", "دوبارہ", "ପୁଣି", "আকৌ"],
        "help": ["madad", "मदद", "help", "உதவி", "సహాయం", "ಸಹಾಯ", "সাহায্য", "મદદ", "ਮਦਦ", "مدد", "ସହାୟତା", "সহায়"],
        "agent": ["inspector", " CSC", "office", "कार्यालय", "दुकान", "center", "केंद्र"],
    },
}


# Question/aux words that must never drive matching ('kaisa'≈'kisan' trap).
STOP_WORDS = {"kya", "kaisa", "kaise", "kab", "kahan", "kyun", "kyon", "hai",
              "hain", "tha", "thi", "mujhe", "mera", "meri", "chahiye", "karo",
              "karna", "kar", "batao", "dena", "lena", "the", "a", "an", "is",
              "am", "are", "my", "i", "me", "to", "for", "of", "do", "does",
              "how", "what", "when", "where", "why", "want", "need", "get",
              "give", "please"}


def content_tokens(text: str) -> list:
    """Normalized tokens minus question/aux words - what the user MEANS."""
    return [t for t in normalize(text).split() if t not in STOP_WORDS]


def normalize(text: str) -> str:
    """Lowercase ASCII, keep ALL Indic letters AND combining marks (matras,
    viramas, anusvara - Unicode categories L*/M*/N*), drop punctuation.
    naive isalnum() shreds Tamil/Devanagari: matras are category Mc/Mn,
    not alnum - that bug made every Indian script unmatchable.
    """
    out = []
    for ch in (text or ""):
        cat = unicodedata.category(ch)
        if cat[0] in ("L", "M", "N") or ch.isspace():
            out.append(ch.lower() if ch.isascii() else ch)
        else:
            out.append(" ")
    return "".join(out).strip()
