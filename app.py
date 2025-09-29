# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
from tts_utils import load_catalog, filter_tts  # reuse your existing utils
from typing import Optional, Dict, Any, List, Mapping
from tts_utils import load_catalog, filter_tts, find_records

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to ["http://localhost:5500"] when ready
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG = load_catalog("tts_catalog.json")

# --- NEW: country normalization ---
_ALIAS = {
    # primary request
    "united states of america": "United States",
    "usa": "United States",
    "u.s.": "United States",
    "us": "United States",
    # a few common alternates you may want (optional)
    "russian federation": "Russia",
    "viet nam": "Vietnam",
    "syrian arab republic": "Syria",
    "democratic republic of the congo": "DR Congo",
    "lao people's democratic republic": "Laos",
    "iran (islamic republic of)": "Iran",
    "bolivia (plurinational state of)": "Bolivia",
    "venezuela (bolivarian republic of)": "Venezuela",
    "republic of korea": "South Korea",
    "korea, republic of": "South Korea",
}

def normalize_country(country: str) -> str:
    if not country:
        return country
    key = country.strip().lower()
    return _ALIAS.get(key, country.strip())

# Existing endpoint (kept, now normalizes country)
@app.get("/tts")
def get_tts(language: Optional[str] = "", country: Optional[str] = "", provider: Optional[str] = ""):
    country = normalize_country(country or "")
    results = filter_tts(CATALOG, language=language or "", country=country or "", provider=provider or "")
    return {"query": {"language": language, "country": country, "provider": provider}, "results": results}

# --- NEW: grouped endpoint ---
@app.get("/tts/by-language")
def tts_by_language(country: str, provider: Optional[str] = ""):
    """
    Build: language -> [providers] for the given country.
    Handles records that are dicts OR strings (defensive).
    """
    ctry = normalize_country(country)

    # 1) Prefer dict-shaped results
    try:
        records = find_records(CATALOG, country=ctry, provider=provider or "")
    except Exception:
        records = None

    # 2) Fallback if needed
    if not records:
        records = filter_tts(CATALOG, language="", country=ctry, provider=provider or "")

    lang_providers: Dict[str, set] = {}

    def add(lang: str, prov: Optional[str]):
        if not lang:
            return
        s = lang_providers.setdefault(lang, set())
        if prov:
            s.add(prov)

    # Helper to coerce a value into a list (handles str / list / None)
    def as_list(v):
        if v is None:
            return []
        if isinstance(v, (list, tuple, set)):
            return [x for x in v if x is not None and str(x).strip() != ""]
        s = str(v).strip()
        return [s] if s else []

    for rec in records or []:
        # Case A: dictionary-like record
        if isinstance(rec, Mapping):
            # Try common keys; accept singular or plural
            langs = as_list(rec.get("language") or rec.get("Language") or rec.get("languages"))
            provs = as_list(rec.get("provider") or rec.get("Provider") or rec.get("providers"))
            # If provider filter was passed in query, you might already be filtered,
            # but we keep the logic generic.
            if not langs and "lang" in rec:
                langs = as_list(rec.get("lang"))
            # If we somehow got no providers key, still register the language (empty provider list)
            if not provs:
                for lang in langs:
                    add(lang, None)
            else:
                for lang in langs:
                    for prov in provs:
                        add(lang, prov)

        # Case B: string record (e.g., just a provider name)
        elif isinstance(rec, str):
            # We can't infer the language from a bare provider string.
            # Put it under a neutral bucket so you still see something.
            add("All languages (unclassified)", rec)

        # Case C: anything else → ignore safely
        else:
            continue

    languages: List[Dict[str, Any]] = [
        {"language": lang, "providers": sorted(list(provs))}
        for lang, provs in sorted(lang_providers.items(), key=lambda x: x[0].lower())
    ]

    return {"country": ctry, "languages": languages, "count": len(records or [])}
