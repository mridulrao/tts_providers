# app.py
import os
from pathlib import Path
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any, List, Mapping
from tts_utils import load_catalog, filter_tts, find_records

BASE = Path(__file__).resolve().parent
CATALOG = load_catalog(str(BASE / "tts_catalog.json"))

app = FastAPI()

# keep CORS permissive or lock later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

# ---------- your existing endpoints, now under /api ----------
api = APIRouter(prefix="/api")

_ALIAS = {
    "united states of america": "United States",
    "usa": "United States",
    "u.s.": "United States",
    "us": "United States",
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
    if not country: return country
    key = country.strip().lower()
    return _ALIAS.get(key, country.strip())

@api.get("/tts")
def get_tts(language: Optional[str] = "", country: Optional[str] = "", provider: Optional[str] = ""):
    country = normalize_country(country or "")
    results = filter_tts(CATALOG, language=language or "", country=country or "", provider=provider or "")
    return {"query": {"language": language, "country": country, "provider": provider}, "results": results}

@api.get("/tts/by-language")
def tts_by_language(country: str, provider: Optional[str] = ""):
    ctry = normalize_country(country)
    try:
        records = find_records(CATALOG, country=ctry, provider=provider or "")
    except Exception:
        records = None
    if not records:
        records = filter_tts(CATALOG, language="", country=ctry, provider=provider or "")

    def as_list(v):
        if v is None: return []
        if isinstance(v, (list, tuple, set)): return [x for x in v if x is not None and str(x).strip() != ""]
        s = str(v).strip(); return [s] if s else []

    from collections import defaultdict
    lang_providers = defaultdict(set)
    for rec in records or []:
        if isinstance(rec, Mapping):
            langs = as_list(rec.get("language") or rec.get("Language") or rec.get("languages") or rec.get("lang"))
            provs = as_list(rec.get("provider") or rec.get("Provider") or rec.get("providers"))
            if provs:
                for lang in langs: 
                    for prov in provs: lang_providers[lang].add(prov)
            else:
                for lang in langs: lang_providers[lang]  # create empty set
        elif isinstance(rec, str):
            lang_providers["All languages (unclassified)"].add(rec)

    languages = [{"language": lang, "providers": sorted(list(provs))}
                 for lang, provs in sorted(lang_providers.items(), key=lambda x: x[0].lower())]
    return {"country": ctry, "languages": languages, "count": len(records or [])}

app.include_router(api)

# ---------- serve frontend (put your index.html in ./frontend) ----------
app.mount("/", StaticFiles(directory=str(BASE / "frontend"), html=True), name="static")
