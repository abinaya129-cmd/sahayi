"""7 MVP schemes: benefits, eligibility rules, documents, interview questions.

Rules are declarative dicts evaluated by rules.py, so adding a scheme is
pure data - no code changes (that's the hackathon scalability story).
Question keys are stable ids; NLU lexicon covers answers in 12 languages.
"""

SCHEMES = {
    "pm_kisan": {
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "emoji": "🌾",
        "benefit_inr": 6000,
        "benefit_text": "Rs 6,000 per year (3 installments of Rs 2,000)",
        "questions": [
            {"id": "is_farmer", "q": "Kya aap ya aapke parivar kheti karte hain?", "type": "bool"},
            {"id": "has_land", "q": "Kya aapke naam zameen ka record hai?", "type": "bool"},
            {"id": "is_taxpayer", "q": "Kya aap income tax dete hain?", "type": "bool"},
        ],
        "rules": [
            {"fact": "is_farmer", "op": "eq", "value": True},
            {"fact": "has_land", "op": "eq", "value": True},
            {"fact": "is_taxpayer", "op": "eq", "value": False},
        ],
        "documents": ["Aadhaar card", "Khasra/khatauni (land record)", "Bank passbook"],
        "form_title": "PM-KISAN Application",
        "questions_en": [
            {"id": "is_farmer", "q": "Do you or your family do farming?", "type": "bool"},
            {"id": "has_land", "q": "Is the land record in your name?", "type": "bool"},
            {"id": "is_taxpayer", "q": "Do you pay income tax?", "type": "bool"},
        ],
    },
    "pmjdy": {
        "name": "PM Jan Dhan Yojana",
        "full_name": "Pradhan Mantri Jan Dhan Yojana",
        "emoji": "🏦",
        "benefit_inr": 200000,
        "benefit_text": "Zero-balance account + Rs 2 lakh accident insurance",
        "questions": [
            {"id": "has_bank", "q": "Kya aapke paas bank khata hai?", "type": "bool"},
            {"id": "has_aadhaar", "q": "Kya aapke paas Aadhaar hai?", "type": "bool"},
            {"id": "age", "q": "Aapki umar kitni hai?", "type": "number", "min": 10, "max": 99},
        ],
        "rules": [
            {"fact": "has_bank", "op": "eq", "value": False},
            {"fact": "has_aadhaar", "op": "eq", "value": True},
            {"fact": "age", "op": "gte", "value": 10},
        ],
        "documents": ["Aadhaar card", "Passport photo", "PAN ya Form-60"],
        "form_title": "Jan Dhan Account Opening Form",
        "questions_en": [
            {"id": "has_bank", "q": "Do you already have a bank account?", "type": "bool"},
            {"id": "has_aadhaar", "q": "Do you have an Aadhaar card?", "type": "bool"},
            {"id": "age", "q": "What is your age?", "type": "number", "min": 10, "max": 99},
        ],
    },
    "ujjwala": {
        "name": "PM Ujjwala",
        "full_name": "Pradhan Mantri Ujjwala Yojana",
        "emoji": "🔥",
        "benefit_inr": 5300,
        "benefit_text": "Free LPG gas connection (Rs 5,300 subsidy)",
        "questions": [
            {"id": "is_woman", "q": "Kya aap mahila hain?", "type": "bool"},
            {"id": "has_gas", "q": "Kya ghar mein pehle se LPG hai?", "type": "bool"},
            {"id": "is_bpl", "q": "Kya aapka parivar BPL/Antyodaya list mein hai?", "type": "bool"},
            {"id": "age", "q": "Aapki umar kitni hai?", "type": "number", "min": 18, "max": 99},
        ],
        "rules": [
            {"fact": "is_woman", "op": "eq", "value": True},
            {"fact": "has_gas", "op": "eq", "value": False},
            {"fact": "is_bpl", "op": "eq", "value": True},
            {"fact": "age", "op": "gte", "value": 18},
        ],
        "documents": ["Aadhaar card", "BPL/Antyodaya ration card", "Bank passbook", "Passport photo"],
        "form_title": "Ujjwala Connection Application",
        "questions_en": [
            {"id": "is_woman", "q": "Are you a woman?", "type": "bool"},
            {"id": "has_gas", "q": "Does your home already have an LPG connection?", "type": "bool"},
            {"id": "is_bpl", "q": "Is your family on the BPL/Antyodaya list?", "type": "bool"},
            {"id": "age", "q": "What is your age?", "type": "number", "min": 18, "max": 99},
        ],
    },
    "awas": {
        "name": "PM Awas Yojana",
        "full_name": "Pradhan Mantri Awas Yojana (Gramin)",
        "emoji": "🏠",
        "benefit_inr": 120000,
        "benefit_text": "Rs 1.2 lakh pucca ghar banane ke liye (Rs 1.3 lakh hill states)",
        "questions": [
            {"id": "no_pucca_house", "q": "Kya aapke paas pucca ghar nahi hai?", "type": "bool"},
            {"id": "is_bpl", "q": "Kya aapka parivar SECC/BPL list mein hai?", "type": "bool"},
            {"id": "owns_land", "q": "Kya ghar banane ke liye zameen hai?", "type": "bool"},
        ],
        "rules": [
            {"fact": "no_pucca_house", "op": "eq", "value": True},
            {"fact": "is_bpl", "op": "eq", "value": True},
            {"fact": "owns_land", "op": "eq", "value": True},
        ],
        "documents": ["Aadhaar card", "Job card", "Bank passbook", "SECC verification"],
        "form_title": "PMAY-G Application",
        "questions_en": [
            {"id": "no_pucca_house", "q": "Do you NOT have a pucca house?", "type": "bool"},
            {"id": "is_bpl", "q": "Is your family on the SECC/BPL list?", "type": "bool"},
            {"id": "owns_land", "q": "Do you have land to build the house on?", "type": "bool"},
        ],
    },
    "mgnrega": {
        "name": "MGNREGA",
        "full_name": "Mahatma Gandhi National Rural Employment Guarantee",
        "emoji": "👷",
        "benefit_inr": 22000,
        "benefit_text": "100 din ka Rozgar (approx Rs 22,000/year)",
        "questions": [
            {"id": "is_adult", "q": "Kya aapki umar 18 saal se zyada hai?", "type": "bool"},
            {"id": "wants_work", "q": "Kya aap haath se kaam karna chahti hain?", "type": "bool"},
            {"id": "has_jobcard", "q": "Kya aapke paas job card hai?", "type": "bool"},
        ],
        "rules": [
            {"fact": "is_adult", "op": "eq", "value": True},
            {"fact": "wants_work", "op": "eq", "value": True},
        ],
        "documents": ["Aadhaar card", "Job card (agar hai)", "Bank/post office passbook"],
        "form_title": "MGNREGA Job Card / Work Demand",
        "questions_en": [
            {"id": "is_adult", "q": "Are you above 18 years of age?", "type": "bool"},
            {"id": "wants_work", "q": "Do you want manual work?", "type": "bool"},
            {"id": "has_jobcard", "q": "Do you have a job card?", "type": "bool"},
        ],
    },
    "vishwakarma": {
        "name": "PM Vishwakarma",
        "full_name": "PM Vishwakarma Artisan Scheme",
        "emoji": "🔨",
        "benefit_inr": 300000,
        "benefit_text": "Rs 3 lakh tak loan @5% + free toolkit Rs 15,000",
        "questions": [
            {"id": "is_artisan", "q": "Kya aap koi haath ka kaam karti hain - silai, lohar, mochi, carpenter?", "type": "bool"},
            {"id": "age", "q": "Aapki umar kitni hai?", "type": "number", "min": 18, "max": 59},
        ],
        "rules": [
            {"fact": "is_artisan", "op": "eq", "value": True},
            {"fact": "age", "op": "gte", "value": 18},
            {"fact": "age", "op": "lte", "value": 59},
        ],
        "documents": ["Aadhaar card", "Udyam/artisan certificate", "Bank passbook"],
        "form_title": "PM Vishwakarma Registration",
        "questions_en": [
            {"id": "is_artisan", "q": "Do you do handiwork - tailoring, blacksmith, cobbler, carpentry?", "type": "bool"},
            {"id": "age", "q": "What is your age?", "type": "number", "min": 18, "max": 59},
        ],
    },
    "skill_india": {
        "name": "Skill India",
        "full_name": "Pradhan Mantri Kaushal Vikas Yojana",
        "emoji": "🎓",
        "benefit_inr": 8000,
        "benefit_text": "Free skill training + certificate + job help",
        "questions": [
            {"id": "wants_training", "q": "Kya aap free training lena chahti hain?", "type": "bool"},
            {"id": "age", "q": "Aapki umar kitni hai?", "type": "number", "min": 15, "max": 45},
        ],
        "rules": [
            {"fact": "wants_training", "op": "eq", "value": True},
            {"fact": "age", "op": "gte", "value": 15},
            {"fact": "age", "op": "lte", "value": 45},
        ],
        "documents": ["Aadhaar card", "Aadhaar-linked bank account", "Education certificate (if any)"],
        "form_title": "PMKVY Enrollment",
        "questions_en": [
            {"id": "wants_training", "q": "Do you want free skill training?", "type": "bool"},
            {"id": "age", "q": "What is your age?", "type": "number", "min": 15, "max": 45},
        ],
    },
}

# Simple ranker fallback: which facts make each scheme worth suggesting next.
SUGGESTION_HINTS = {
    "pm_kisan": ["is_farmer"],
    "ujjwala": ["is_woman", "is_bpl"],
    "awas": ["is_bpl", "no_pucca_house"],
    "mgnrega": ["wants_work"],
    "vishwakarma": ["is_artisan"],
    "pmjdy": ["has_aadhaar"],
    "skill_india": ["wants_training"],
}
