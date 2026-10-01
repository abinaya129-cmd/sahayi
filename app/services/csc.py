"""CSC (Common Service Centre) locator.

Seed data covers one representative district per major state - enough for the
demo and honest for a hackathon. Real deployment would join the official CSC
registry; the API contract stays identical.
"""
import math

from ..languages import LANGUAGES

# (name, lat, lon, address, languages spoken) - seeded demo network
CSCS = [
    {"id": "csc1", "name": "Barmer CSC", "state": "Rajasthan", "district": "Barmer",
     "lat": 25.75, "lon": 71.39, "address": "Main Bazar Road, Barmer",
     "langs": ["hi", "mr"]},
    {"id": "csc2", "name": "Madurai CSC", "state": "Tamil Nadu", "district": "Madurai",
     "lat": 9.93, "lon": 78.12, "address": "Taluk Office Road, Madurai",
     "langs": ["ta", "en"]},
    {"id": "csc3", "name": "Guntur CSC", "state": "Andhra Pradesh", "district": "Guntur",
     "lat": 16.31, "lon": 80.44, "address": "Kothapet Main Road, Guntur",
     "langs": ["te", "en"]},
    {"id": "csc4", "name": "Mysuru CSC", "state": "Karnataka", "district": "Mysuru",
     "lat": 12.30, "lon": 76.65, "address": "Devaraj Market Road, Mysuru",
     "langs": ["kn", "hi"]},
    {"id": "csc5", "name": "Kozhikode CSC", "state": "Kerala", "district": "Kozhikode",
     "lat": 11.26, "lon": 75.78, "address": "SM Street, Kozhikode",
     "langs": ["ml", "en"]},
    {"id": "csc6", "name": "Nashik CSC", "state": "Maharashtra", "district": "Nashik",
     "lat": 20.00, "lon": 73.79, "address": "College Road, Nashik",
     "langs": ["mr", "hi"]},
    {"id": "csc7", "name": "Surat CSC", "state": "Gujarat", "district": "Surat",
     "lat": 21.17, "lon": 72.83, "address": "Ring Road, Surat",
     "langs": ["gu", "hi"]},
    {"id": "csc8", "name": "Bardhaman CSC", "state": "West Bengal", "district": "Bardhaman",
     "lat": 23.24, "lon": 87.86, "address": "G.T. Road, Bardhaman",
     "langs": ["bn", "hi"]},
    {"id": "csc9", "name": "Ludhiana CSC", "state": "Punjab", "district": "Ludhiana",
     "lat": 30.90, "lon": 75.85, "address": "Civil Lines, Ludhiana",
     "langs": ["pa", "hi"]},
    {"id": "csc10", "name": "Bareilly CSC", "state": "Uttar Pradesh", "district": "Bareilly",
     "lat": 28.37, "lon": 79.43, "address": "Civil Lines, Bareilly",
     "langs": ["hi", "ur"]},
    {"id": "csc11", "name": "Cuttack CSC", "state": "Odisha", "district": "Cuttack",
     "lat": 20.46, "lon": 85.88, "address": "Buxi Bazar, Cuttack",
     "langs": ["or", "hi"]},
    {"id": "csc12", "name": "Nagaon CSC", "state": "Assam", "district": "Nagaon",
     "lat": 26.35, "lon": 92.68, "address": "A.T. Road, Nagaon",
     "langs": ["as", "bn"]},
]

# Geocoding fallbacks for demo "state/district" voice input
_STATE_HINTS = {
    "rajasthan": ("Barmer", "Barmer"), "tamil": ("Madurai", "Madurai"),
    "nadu": ("Madurai", "Madurai"), "andhra": ("Guntur", "Guntur"),
    "karnatak": ("Mysuru", "Mysuru"), "mysore": ("Mysuru", "Mysuru"),
    "kerala": ("Kozhikode", "Kozhikode"), "maharashtra": ("Nashik", "Nashik"),
    "gujarat": ("Surat", "Surat"), "bengal": ("Bardhaman", "Bardhaman"),
    "punjab": ("Ludhiana", "Ludhiana"), "up": ("Bareilly", "Bareilly"),
    "uttar": ("Bareilly", "Bareilly"), "odisha": ("Cuttack", "Cuttack"),
    "orissa": ("Cuttack", "Cuttack"), "assam": ("Nagaon", "Nagaon"),
}


def _haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def locate(query: str, user_lat: float = None, user_lon: float = None, top: int = 3) -> dict:
    """Return nearest CSCs. Priority: GPS coords > fuzzy district/state text."""
    if user_lat is not None and user_lon is not None:
        scored = [{**c, "distance_km": round(_haversine_km(user_lat, user_lon, c["lat"], c["lon"]), 1)}
                  for c in CSCS]
        scored.sort(key=lambda c: c["distance_km"])
        return {"matched": "gps", "results": scored[:top]}
    q = (query or "").lower().strip()
    for hint, (district, _) in _STATE_HINTS.items():
        if hint in q:
            c = next(c for c in CSCS if c["district"] == district)
            near = [{**x, "distance_km": round(_haversine_km(c["lat"], c["lon"], x["lat"], x["lon"]), 1)}
                    for x in CSCS if x["id"] != c["id"]]
            near.sort(key=lambda x: x["distance_km"])
            # matched center itself always carries a distance (0 = user's own district)
            return {"matched": c["district"], "results": [{**c, "distance_km": 0.0}] + near[: top - 1]}
    # Default: show network overview
    return {"matched": "network", "results": CSCS[:top]}
