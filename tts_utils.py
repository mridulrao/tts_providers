
import json

def load_catalog(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def filter_tts(catalog, language=None, country=None, provider=None):
    """
    Returns a list of providers that satisfy all specified filters.
    - language: exact language string match (case-sensitive by design)
    - country: exact country string match
    - provider: exact provider name match
    """
    hits = []
    for row in catalog:
        if language and row["language"] != language:
            continue
        if country and (country not in row["countries"]):
            continue
        if provider and row["provider"] != provider:
            continue
        hits.append(row["provider"])
    # unique, preserve relative order
    out = list(dict.fromkeys(hits))
    return out

def find_records(catalog, language=None, country=None, provider=None):
    """
    Returns matching catalog rows for more detailed inspection.
    """
    rows = []
    for row in catalog:
        if language and row["language"] != language:
            continue
        if country and (country not in row["countries"]):
            continue
        if provider and row["provider"] != provider:
            continue
        rows.append(row)
    return rows
