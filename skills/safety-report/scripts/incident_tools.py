#!/usr/bin/env python3
"""
incident_tools.py - turn a messy incident export into clean, analysable data.

Works with SafetyCulture / Mitti exports, SAP/Enablon/Cority exports and home-made spreadsheets.
Everything here is a starting point: always eyeball the printed mapping and fix anything odd
before trusting the numbers.

Usage (CLI):
  python incident_tools.py profile <incidents.csv|xlsx> [--dayfirst|--monthfirst]
  python incident_tools.py clean   <incidents.csv|xlsx> <out.csv> [--site-map map.json] [--dayfirst|--monthfirst]
  python incident_tools.py rates   <clean.csv> <hours.csv|xlsx> [--convention au|us|uk] [--by site] [--period month|quarter]

Python:
  from incident_tools import load_table, clean_incidents, rates_table, flag_review_candidates
"""
import json, re, sys
from difflib import SequenceMatcher

import pandas as pd

# ---------------------------------------------------------------- loading
def load_table(path, sheet=None):
    """Load csv/xlsx and find the real header row (exports often have title rows above it)."""
    if str(path).lower().endswith((".xlsx", ".xlsm", ".xls")):
        raw = pd.read_excel(path, sheet_name=sheet or 0, header=None, dtype=str)
    else:
        raw = pd.read_csv(path, header=None, dtype=str, keep_default_na=False, encoding_errors="replace")
    raw = raw.fillna("")
    best, best_score = 0, -1
    for i in range(min(15, len(raw))):
        vals = [str(v).strip() for v in raw.iloc[i].tolist()]
        filled = sum(1 for v in vals if v)
        texty = sum(1 for v in vals if v and not re.fullmatch(r"[\d./\-: ]+", v))
        score = filled + texty
        if score > best_score:
            best, best_score = i, score
    df = raw.iloc[best + 1:].copy()
    df.columns = [str(c).strip() or f"col{j}" for j, c in enumerate(raw.iloc[best].tolist())]
    df = df[(df != "").any(axis=1)].reset_index(drop=True)
    return df

# ---------------------------------------------------------------- column mapping
COLUMN_HINTS = {
    "date": ["date of incident", "incident date", "event date", "date occurred", "occurred", "date reported", "date", "conducted on", "created"],
    "site": ["site", "location", "facility", "business unit", "project", "workplace", "branch", "plant"],
    "event_type": ["event type", "incident type", "classification", "injury classification", "type", "outcome", "treatment"],
    "category": ["category", "mechanism", "hazard type", "injury type", "nature", "subcategory"],
    "description": ["what happened", "description", "details", "summary", "narrative", "comments", "event description"],
    "area": ["area", "department", "zone", "work area"],
    "shift": ["shift", "time of day"],
    "severity": ["severity", "risk rating", "actual severity", "consequence"],
    "potential_severity": ["potential severity", "potential", "worst credible"],
    "notified": ["regulator notified", "notified", "notifiable", "reported to regulator"],
    "status": ["status", "state"],
    "id": ["audit id", "incident id", "id", "reference", "ref", "number", "#"],
    "days_lost": ["days lost", "lost days", "days away", "time lost"],
    "person_type": ["employee type", "person type", "worker type", "contractor", "employment"],
}

def map_columns(df):
    mapping, used = {}, set()
    cols = list(df.columns)
    for field, hints in COLUMN_HINTS.items():
        best, score = None, 0.0
        for c in cols:
            if c in used:
                continue
            cl = c.lower().strip(" ?:")
            for h in hints:
                s = 1.0 if cl == h else (0.9 if h in cl else SequenceMatcher(None, cl, h).ratio() * 0.8)
                if s > score:
                    best, score = c, s
        if best is not None and score >= 0.6:
            mapping[field] = best
            used.add(best)
    return mapping

# ---------------------------------------------------------------- dates
def parse_dates(series, dayfirst=True):
    """Parse mixed formats. AU/NZ/UK default to day-first; pass dayfirst=False for US data."""
    s = series.astype(str).str.strip()
    out = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y" if dayfirst else "%m/%d/%Y", "%d/%m/%y" if dayfirst else "%m/%d/%y",
                "%d-%m-%Y" if dayfirst else "%m-%d-%Y", "%b %d %Y", "%d %b %Y", "%d %B %Y", "%B %d %Y", "%d-%b-%y", "%b-%y"):
        miss = out.isna()
        if not miss.any():
            break
        out[miss] = pd.to_datetime(s[miss], format=fmt, errors="coerce")
    miss = out.isna()
    if miss.any():
        out[miss] = pd.to_datetime(s[miss], dayfirst=dayfirst, errors="coerce")
    return out

# ---------------------------------------------------------------- classification
# Standard classes (AS 1885.1 style, mapped to US where relevant)
CLASS_RULES = [
    ("Fatality", r"fatal|death|died|deceased"),
    ("LTI", r"\blti\b|lost ?time|days? (away|off)|time lost"),
    ("RWI", r"\brwi\b|restricted|alternate dut|suitable dut|light dut|modified dut"),
    ("MTI", r"\bmti\b|medical treat|\bmedical\b|doctor|\bgp\b|hospital|physio|stitch|suture|x-?ray"),
    ("FAI", r"\bfai\b|first ?aid"),
    ("Near miss", r"near ?miss|close call|near hit"),
    ("Hazard", r"hazard|observation|unsafe (act|condition)|report only"),
    ("Property damage", r"property|damage|vehicle damage|equipment damage"),
    ("Environmental", r"environment|spill(?!.*walkway)|emission"),
]
RECORDABLE = {"Fatality", "LTI", "RWI", "MTI"}

def classify_event(text):
    t = str(text).lower()
    for cls, pat in CLASS_RULES:
        if re.search(pat, t):
            return cls
    return "Unclassified"

THEMES = {
    "Plant-pedestrian interaction": r"forklift|reach truck|pallet jack|telehandler|excavator|reversing|pedestrian|mobile plant|struck by|truck|vehicle|loader",
    "Manual handling": r"lift|lifting|carry|push|pull|twist|strain|sprain|back|shoulder|repetitive|wrist|body stress|manual handling",
    "Slips, trips, falls (same level)": r"slip|trip|wet floor|uneven|fell over|tripped",
    "Falls from height / falling objects": r"from height|ladder|scaffold|roof|fell from|fall from|racking|dropped object|falling object|fell .*rack",
    "Machinery and guarding": r"guard|interlock|slicer|conveyor|caught|entangle|nip point|jam|machine|bypass|amputat",
    "Cuts and lacerations": r"cut|lacerat|knife|blade|sharp|box cutter",
    "Hazardous substances and energy": r"ammonia|chemical|gas|leak|fume|burn|scald|hot oil|steam|electric|shock|arc|silica|dust",
    "Housekeeping and access": r"housekeeping|spill|obstruct|blocked|clutter|cable across|walkway|exit",
    "Psychosocial and violence": r"aggress|abuse|bully|harass|assault|threat|stress|fatigue|violence",
}

def theme_of(text):
    t = str(text).lower()
    hits = [k for k, p in THEMES.items() if re.search(p, t)]
    return hits[0] if hits else "Other"

# Words that suggest serious potential or notifiable events. These are review FLAGS, not decisions.
SERIOUS_CUES = {
    "amputation": r"amputat|severed|fingertip",
    "fracture": r"fractur|broken bone|broke (his|her|their)",
    "hospital admission": r"admitted|hospital|ambulance|in-?patient",
    "serious burn": r"burn|scald",
    "eye injury": r"\beye\b",
    "crush / struck by plant": r"crush|run over|ran over|struck by|pinned",
    "fall from height": r"fell from|fall from|from height|roof|scaffold|ladder",
    "falling object from height": r"fell from (top )?rack|fell .*racking|dropped from height|load fell|falling object",
    "uncontrolled release / gas": r"ammonia|gas leak|leak|uncontrolled release|chlorine|fumes?|evacuat",
    "electric shock": r"electric shock|shocked|electrocut|live wire",
    "collapse": r"collapse|structural failure|trench",
    "fire / explosion": r"caught fire|fire (broke|started|occurred)|flash fire|explosion|ignit",
    "guard bypass / energy isolation": r"bypass|isolation|lock ?out|interlock",
}

def flag_review_candidates(df):
    """Rows whose words suggest notifiable / dangerous / HiPo potential, especially if logged as minor."""
    out = []
    for i, r in df.iterrows():
        text = f"{r.get('description','')} {r.get('category','')}".lower()
        cues = [k for k, p in SERIOUS_CUES.items() if re.search(p, text)]
        if cues:
            out.append({"row": int(i), "id": r.get("id", ""), "date": str(r.get("date", ""))[:10], "site": r.get("site", ""),
                        "logged_as": r.get("event_class", ""), "logged_severity": r.get("severity", ""),
                        "cues": cues, "description": str(r.get("description", ""))[:220]})
    return out

# ---------------------------------------------------------------- sites
def suggest_site_map(values, threshold=0.55):
    """Cluster spelling variants (e.g. 'DAN', 'Dandenong DC', 'dandenong'). Review before using."""
    vals = sorted({str(v).strip() for v in values if str(v).strip()}, key=lambda v: (-len(v), v))
    canon, mapping = [], {}
    def norm(v): return re.sub(r"\b(dc|plant|site|depot|warehouse|pk|park)\b", "", v.lower()).strip()
    for v in vals:
        best, score = None, 0.0
        for c in canon:
            a, b = norm(v), norm(c)
            s = SequenceMatcher(None, a, b).ratio()
            initials = "".join(w[0] for w in re.findall(r"[a-z]+", c.lower()))
            if a and b and (a in b or b in a or (len(a) <= 4 and b.startswith(a[:2]) and a.isalpha())):
                s = max(s, 0.9)
            elif len(v) <= 4 and v.isalpha() and v.lower() == initials:
                s = max(s, 0.9)
            if s > score:
                best, score = c, s
        if best and score >= threshold:
            mapping[v] = best
        else:
            canon.append(v)
            mapping[v] = v
    return mapping

# ---------------------------------------------------------------- clean
def clean_incidents(df, site_map=None, dayfirst=True):
    m = map_columns(df)
    out = pd.DataFrame()
    for field, col in m.items():
        out[field] = df[col].astype(str).str.strip()
    if "date" in out:
        out["date"] = parse_dates(out["date"], dayfirst=dayfirst)
    if "site" in out:
        smap = site_map or suggest_site_map(out["site"])
        out["site"] = out["site"].map(lambda v: smap.get(str(v).strip(), v))
    src = out.get("event_type", pd.Series([""] * len(out))).astype(str) + " " + out.get("category", pd.Series([""] * len(out))).astype(str)
    out["event_class"] = src.map(classify_event)
    out["recordable"] = out["event_class"].isin(RECORDABLE)
    out["theme"] = (out.get("description", "").astype(str) + " " + out.get("category", "").astype(str)).map(theme_of)
    if "date" in out:
        out["month"] = out["date"].dt.to_period("M").astype(str)
        out["weekday"] = out["date"].dt.day_name()
    return out, m

# ---------------------------------------------------------------- rates
CONVENTIONS = {
    "au": {"base": 1_000_000, "label": "per 1,000,000 hours", "names": {"rec": "TRIFR", "lti": "LTIFR", "mti": "MTIFR", "all": "AIFR"}},
    "nz": {"base": 1_000_000, "label": "per 1,000,000 hours", "names": {"rec": "TRIFR", "lti": "LTIFR", "mti": "MTIFR", "all": "AIFR"}},
    "us": {"base": 200_000, "label": "per 200,000 hours (100 FTE)", "names": {"rec": "TRIR", "lti": "LTIR", "dart": "DART"}},
    "uk": {"base": 100_000, "label": "per 100,000 hours", "names": {"rec": "Recordable rate", "lti": "AFR (lost time)"}},
}

def load_hours(path):
    h = load_table(path)
    cols = {c.lower(): c for c in h.columns}
    def pick(*keys):
        for k in keys:
            for cl, c in cols.items():
                if k in cl:
                    return c
    mcol, scol, hcol = pick("month", "period", "date"), pick("site", "location"), pick("hours")
    hh = pd.DataFrame({"period": h[mcol], "hours": pd.to_numeric(h[hcol].astype(str).str.replace(",", ""), errors="coerce")})
    if scol:
        hh["site"] = h[scol].astype(str).str.strip()
    p = parse_dates(hh["period"], dayfirst=True)
    hh["month"] = p.dt.to_period("M").astype(str)
    return hh

def rates_table(clean, hours, convention="au", by=None, period="month"):
    """Counts + frequency rates per period (and optional site). Small denominators make monthly rates noisy:
    always report rolling / year-to-date alongside."""
    conv = CONVENTIONS[convention]
    c = clean.copy()
    c["period"] = c["date"].dt.to_period("Q" if period == "quarter" else "M").astype(str)
    hh = hours.copy()
    hh["period"] = pd.PeriodIndex(hh["month"], freq="M").asfreq("Q" if period == "quarter" else "M").astype(str)
    keys = ["period"] + ([by] if by else [])
    if by and by in hh and by in c:
        smap = suggest_site_map(list(c[by].unique()) + list(hh[by].unique()))
        c[by] = c[by].map(lambda v: smap.get(v, v)); hh[by] = hh[by].map(lambda v: smap.get(v, v))
    g = c.groupby(keys).agg(recordables=("recordable", "sum"),
                            lti=("event_class", lambda s: (s == "LTI").sum()),
                            mti=("event_class", lambda s: (s == "MTI").sum()),
                            rwi=("event_class", lambda s: (s == "RWI").sum()),
                            fai=("event_class", lambda s: (s == "FAI").sum()),
                            near_miss=("event_class", lambda s: (s == "Near miss").sum()),
                            hazards=("event_class", lambda s: (s == "Hazard").sum()),
                            fatalities=("event_class", lambda s: (s == "Fatality").sum())).reset_index()
    hrs = hh.groupby(keys)["hours"].sum().reset_index() if all(k in hh for k in keys) else hh.groupby(["period"])["hours"].sum().reset_index()
    t = hrs.merge(g, on=[k for k in keys if k in hrs.columns], how="left").fillna(0)
    b = conv["base"]
    n = conv["names"]
    t[n["rec"]] = (t["recordables"] / t["hours"] * b).round(1)
    t[n["lti"]] = (t["lti"] / t["hours"] * b).round(1)
    if convention == "us":
        t["DART"] = ((t["lti"] + t["rwi"]) / t["hours"] * b).round(2)
        t[n["rec"]] = (t["recordables"] / t["hours"] * b).round(2)
        t[n["lti"]] = (t["lti"] / t["hours"] * b).round(2)
    rr = t["recordables"].astype(float); t["near_miss_per_recordable"] = (t["near_miss"].astype(float) / rr.where(rr > 0)).round(1)
    return t, conv["label"]

def cumulative_rate(clean, hours, convention="au", months=None):
    """Rate over a span of months (e.g. last 12 = rolling 12-month, or YTD). Returns dict."""
    b = CONVENTIONS[convention]["base"]
    c, h = clean, hours
    if months:
        c = c[c["month"].isin(months)]; h = h[h["month"].isin(months)]
    rec, lti, hrs = int(c["recordable"].sum()), int((c["event_class"] == "LTI").sum()), float(h["hours"].sum())
    return {"months": months or "all", "recordables": rec, "ltis": lti, "hours": hrs,
            "recordable_rate": round(rec / hrs * b, 2 if convention == "us" else 1) if hrs else None,
            "lti_rate": round(lti / hrs * b, 2 if convention == "us" else 1) if hrs else None,
            "basis": CONVENTIONS[convention]["label"]}

# ---------------------------------------------------------------- CLI
def _cli():
    a = sys.argv[1:]
    if not a or a[0] not in ("profile", "clean", "rates"):
        print(__doc__); return
    dayfirst = "--monthfirst" not in a
    if a[0] == "profile":
        df = load_table(a[1]); m = map_columns(df)
        print("ROWS:", len(df)); print("COLUMNS:", list(df.columns)); print("MAPPING:", json.dumps(m, indent=1))
        if "site" in m: print("SITE MAP (review!):", json.dumps(suggest_site_map(df[m["site"]]), indent=1))
        cl, _ = clean_incidents(df, dayfirst=dayfirst)
        print("UNPARSED DATES:", int(cl["date"].isna().sum()) if "date" in cl else "no date column")
        print("EVENT CLASSES:", cl["event_class"].value_counts().to_dict())
        print("THEMES:", cl["theme"].value_counts().to_dict())
        print("REVIEW CANDIDATES:", json.dumps(flag_review_candidates(cl), indent=1, default=str))
    elif a[0] == "clean":
        df = load_table(a[1]); smap = None
        if "--site-map" in a: smap = json.load(open(a[a.index("--site-map") + 1]))
        cl, m = clean_incidents(df, site_map=smap, dayfirst=dayfirst)
        cl.to_csv(a[2], index=False); print("saved", a[2], len(cl), "rows; mapping", m)
    elif a[0] == "rates":
        cl = pd.read_csv(a[1], parse_dates=["date"]); h = load_hours(a[2])
        conv = a[a.index("--convention") + 1] if "--convention" in a else "au"
        by = a[a.index("--by") + 1] if "--by" in a else None
        per = a[a.index("--period") + 1] if "--period" in a else "month"
        t, label = rates_table(cl, h, conv, by, per)
        print("Basis:", label); print(t.to_string(index=False))

if __name__ == "__main__":
    _cli()
