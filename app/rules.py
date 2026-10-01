"""Declarative eligibility engine. Rules are data, not code.

evaluate() returns (eligible, failures) where failures carry human-readable
reasons SAHAYI speaks back to the user - "not eligible" is never a dead end.
"""

_OPS = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "gte": lambda a, b: _num(a) >= _num(b),
    "lte": lambda a, b: _num(a) <= _num(b),
    "gt": lambda a, b: _num(a) > _num(b),
}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def evaluate(rules: list, facts: dict):
    """Return (eligible: bool, failures) where failures is a list of
    (fact, actual, expected) tuples - formatting into user language happens
    in the conversation layer via reason_text()."""
    failures = []
    for r in rules:
        fact = r["fact"]
        op = _OPS[r["op"]]
        actual = facts.get(fact)
        expected = r["value"]
        if not op(actual, expected):
            failures.append((fact, actual, expected))
    return (len(failures) == 0), failures


REASONS_HI = {
    "is_farmer": "aap kisan parivar se nahi hain",
    "has_land": "zameen ka record aapke naam nahi hai",
    "is_taxpayer": "aap income tax dete hain (is yojana ke liye not allowed)",
    "has_bank": "aapke paas pehle se bank khata hai",
    "has_aadhaar": "Aadhaar card nahi hai",
    "age": "umar ki shart puri nahi hui",
    "is_woman": "yeh yojana sirf mahilao ke liye hai",
    "has_gas": "ghar mein pehle se LPG connection hai",
    "is_bpl": "BPL/Antyodaya list mein naam nahi hai",
    "no_pucca_house": "aapke paas pehle se pucca ghar hai",
    "owns_land": "ghar ke liye zameen nahi hai",
    "is_adult": "umar 18 saal kam hai",
    "wants_work": "aap haath ka kaam nahi karna chahti",
    "is_artisan": "haath ka kaam/artisan shart puri nahi hui",
    "wants_training": "training ki iccha nahi hai",
}

REASONS_EN = {
    "is_farmer": "your family is not a farming household",
    "has_land": "the land record is not in your name",
    "is_taxpayer": "you pay income tax (not allowed for this scheme)",
    "has_bank": "you already have a bank account",
    "has_aadhaar": "you do not have an Aadhaar card",
    "age": "the age condition is not met",
    "is_woman": "this scheme is only for women",
    "has_gas": "your household already has an LPG connection",
    "is_bpl": "your name is not on the BPL/Antyodaya list",
    "no_pucca_house": "you already have a pucca house",
    "owns_land": "you do not have land to build a house",
    "is_adult": "you are under 18 years of age",
    "wants_work": "you do not want manual work",
    "is_artisan": "the artisan condition is not met",
    "wants_training": "you declined the training",
}


def reason_text(failure: tuple, lang: str = "hi") -> str:
    fact, actual, _expected = failure
    if lang == "en":
        return REASONS_EN.get(fact, f"condition '{fact}' not met")
    if fact == "age":
        return f"umar shart puri nahi hui (aapne {actual} bataya)"
    return REASONS_HI.get(fact, f"{fact} shart puri nahi hui")
