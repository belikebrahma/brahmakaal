"""
Fast festival cross-validation. Uses TithiScanner directly (not calculate_festival_dates).
Processes one festival at a time with caching. Suppresses 🌅🌇 noise.
"""

import sys, json, os, re, time
from collections import Counter, defaultdict
from datetime import datetime, date
from typing import Dict, List, Optional

DATA_DIR = "data/reference"
PIPELINE_DIR = os.path.join(DATA_DIR, "pipeline")
CACHE_FILE = os.path.join(PIPELINE_DIR, "festival_scans_cache.json")
RESULT_FILE = os.path.join(PIPELINE_DIR, "validation_results.json")
REPORT_FILE = os.path.join(PIPELINE_DIR, "cross_validation_report.md")
os.makedirs(PIPELINE_DIR, exist_ok=True)

# ── Suppress 🌅🌇 noise ──────────────────────────────────
import builtins
_original_print = builtins.print
def _quiet_print(*args, **kwargs):
    if args and isinstance(args[0], str) and ('🌅' in args[0] or '🌇' in args[0] or '⚠️' in args[0]):
        return
    _original_print(*args, **kwargs)
builtins.print = _quiet_print

# ── Helpers ──────────────────────────────────────────────

def festival_id(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r'\*[a-z]+', '', s)
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', '_', s).strip('_')
    return s or name.lower().replace(' ', '_')


def load_dp_data() -> List[Dict]:
    with open(os.path.join(DATA_DIR, "dp_festivals_merged.json")) as f:
        return json.load(f)["festivals"]


def expand_rows(festivals: List[Dict]) -> List[Dict]:
    rows = []
    for f in festivals:
        for y in [2025, 2026, 2027]:
            ds = f.get(str(y))
            if ds:
                rows.append({"festival_id": festival_id(f["name"]),
                             "name": f["name"], "year": y, "dp_date": ds})
    # Deduplicate
    seen = set()
    deduped = []
    for r in rows:
        key = (r["festival_id"], r["year"], r["dp_date"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


# ── Initialize engine ───────────────────────────────────

sys.stderr.write("Initializing Kaal engine...\n")
sys.stderr.flush()
t0 = time.time()
from kaal_engine.kaal import Kaal
from kaal_engine.core.festivals import FestivalEngine, FestivalRule, FestivalType
from kaal_engine.core.festival_scanner import TithiScanner, scan_festival

kaal = Kaal(de441_path="de421.bsp")
fe = FestivalEngine(kaal)
scanner = TithiScanner(kaal)
sys.stderr.write(f"  Done ({time.time()-t0:.1f}s)\n")
sys.stderr.flush()

# Build our rules dict
OUR_RULES = {}  # festival_id -> rule_name
for r in fe.festival_rules:
    OUR_RULES[festival_id(r.name)] = r.name
    OUR_RULES[festival_id(r.english_name)] = r.name

# Manual mappings for DP -> our rules
MANUAL = {
    "diwali": "Diwali", "deepavali": "Diwali", "lakshmi_puja": "Diwali",
    "narak_chaturdashi": "Naraka Chaturdashi",
    "govardhan_puja": "Govardhan Puja", "bhaiya_dooj": "Bhai Dooj", "bhai_dooj": "Bhai Dooj",
    "dhanteras": "Dhanteras", "kali_chaudas": "Kali Puja",
    "dussehra": "Dussehra", "vijayadashami": "Dussehra", "maha_navami": "Navratri",
    "durga_ashtami": "Durga Puja",
    "navratri_begins": "Sharad Navaratri", "sharad_navratri": "Sharad Navaratri",
    "navratri": "Sharad Navaratri",
    "saraswati_puja": "Saraswati Puja", "saraswati_avahan": "Saraswati Puja",
    "karwa_chauth": "Karva Chauth",
    "chhoti_holi": "Holika Dahan", "holika_dahan": "Holika Dahan",
    "holi": "Holi", "guru_purnima": "Guru Purnima",
    "raksha_bandhan": "Varalakshmi Vratam", "rakhi": "Varalakshmi Vratam",
    "krishna_janmashtami": "Krishna Janmashtami", "ganesh_chaturthi": "Ganesh Chaturthi",
    "ganesh_visarjan": "Ganesh Chaturthi",
    "onam": "Onam", "pongal": "Pongal", "makara_sankranti": "Makar Sankranti",
    "mahashivaratri": "Maha Shivaratri", "maha_shivaratri": "Maha Shivaratri",
    "shivaratri": "Maha Shivaratri",
    "ram_navami": "Ram Navami", "rama_navami": "Ram Navami",
    "rama_navami_smarta": "Ram Navami", "rama_navami_iskcon": "Ram Navami",
    "hanuman_jayanti": "Hanuman Jayanti",
    "chaitra_navratri": "Chaitra Navaratri",
    "gudi_padwa": "Gudi Padwa", "ugadi": "Gudi Padwa",
    "vasant_panchami": "Vasant Panchami",
    "teej": "Teej", "hartalika_teej": "Teej",
    "hariyali_teej": "Hariyali Teej", "kajari_teej": "Teej",
    "lohri": "Lohri", "baisakhi": "Baisakhi",
    "kartik_purnima": "Kartik Purnima", "kartika_purnima": "Kartik Purnima",
    "mahalaya": "Mahalaya",
    "dakshinayana": "Dakshinayana", "uttarayana": "Uttarayana",
}
FULL_MAP = OUR_RULES | MANUAL


# ── Computations ────────────────────────────────────────

def compute_festival_date(rule_name: str, year: int) -> Optional[str]:
    """Compute one festival date using scanner directly."""
    # Find the rule
    rule = None
    for r in fe.festival_rules:
        if r.name == rule_name:
            rule = r
            break
    
    if rule is None:
        return None
    
    # Compute using scan_festival
    try:
        d = scan_festival(scanner, rule, year)
        return str(d) if d else None
    except Exception as e:
        sys.stderr.write(f"    ERROR {rule_name} {year}: {e}\n")
        return None


def compute_lunar_tithi(year: int, month: str, paksha: str, tithi: int) -> Optional[str]:
    """Direct tithi computation for festivals not in rules."""
    try:
        d = scanner.find_tithi_date(year, month, paksha, tithi)
        return str(d) if d else None
    except Exception as e:
        sys.stderr.write(f"    ERROR {month} {paksha} {tithi} {year}: {e}\n")
        return None


# ── Main pipeline ───────────────────────────────────────

def run():
    # Load cache if exists
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        sys.stderr.write(f"Loaded cache: {len(cache)} entries\n")
    
    # Load and expand DP data
    festivals = load_dp_data()
    rows = expand_rows(festivals)
    sys.stderr.write(f"Total rows: {len(rows)}\n")
    sys.stderr.flush()
    
    # Phase 1: Map names
    for row in rows:
        fn = FULL_MAP.get(row["festival_id"])
        row["our_rule"] = fn
        row["mapped"] = fn is not None
    
    mapped = sum(1 for r in rows if r["mapped"])
    unmapped = sum(1 for r in rows if not r["mapped"])
    sys.stderr.write(f"Mapped: {mapped}, Unmapped: {unmapped}\n")
    sys.stderr.flush()
    
    # Phase 2: Compute engine dates (only for mapped)
    # Track festival-year combinations we need to compute
    needed = set()
    for row in rows:
        if row["mapped"]:
            key = f"{row['our_rule']}|{row['year']}"
            needed.add(key)
    
    sys.stderr.write(f"Unique festival-year combos to compute: {len(needed)}\n")
    sys.stderr.flush()
    
    # Compute any uncached entries
    for key in sorted(needed):
        if key in cache:
            continue
        rule_name, year_str = key.split("|")
        year = int(year_str)
        
        sys.stderr.write(f"  Computing {rule_name} {year}...\n")
        sys.stderr.flush()
        t0 = time.time()
        result = compute_festival_date(rule_name, year)
        elapsed = time.time() - t0
        cache[key] = result
        sys.stderr.write(f"    -> {result} ({elapsed:.1f}s)\n")
        sys.stderr.flush()
        
        # Save cache periodically
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    
    # Fill in our_date for each row
    for row in rows:
        if row["mapped"]:
            key = f"{row['our_rule']}|{row['year']}"
            row["our_date"] = cache.get(key)
            row["our_error"] = None if row.get("our_date") else "Engine failed"
    
    # Phase 3: Categorize
    for row in rows:
        if not row["mapped"]:
            row["category"] = "NOT_MAPPED"
        elif not row["our_date"]:
            row["category"] = "ENGINE_ERROR"
        elif row["our_date"] == row["dp_date"]:
            row["category"] = "EXACT_MATCH"
        else:
            try:
                dp = datetime.strptime(row["dp_date"], "%Y-%m-%d").date()
                our = datetime.strptime(row["our_date"], "%Y-%m-%d").date()
                diff = abs((our - dp).days)
                if diff <= 1: row["category"] = "OFF_BY_1"
                elif diff <= 3: row["category"] = "OFF_BY_X"
                else: row["category"] = "MISMATCH"
            except:
                row["category"] = "MISMATCH"
    
    # Phase 4: Compute stats
    cats = Counter(r["category"] for r in rows)
    fest_stats = defaultdict(lambda: {"t": 0, "e": 0, "o1": 0, "ox": 0, "m": 0, "er": 0, "nm": 0})
    for row in rows:
        fs = fest_stats[row["name"]]
        fs["t"] += 1
        c = row["category"]
        if c == "EXACT_MATCH": fs["e"] += 1
        elif c == "OFF_BY_1": fs["o1"] += 1
        elif c == "OFF_BY_X": fs["ox"] += 1
        elif c == "MISMATCH": fs["m"] += 1
        elif c == "ENGINE_ERROR": fs["er"] += 1
        elif c == "NOT_MAPPED": fs["nm"] += 1
    
    # Save results
    clean_rows = [{k: v for k, v in r.items()} for r in rows]
    with open(RESULT_FILE, "w") as f:
        json.dump(clean_rows, f, indent=2)
    sys.stderr.write(f"Saved {RESULT_FILE}\n")
    
    # ── Generate Report ──
    lines = []
    lines.append("# Festival Cross-Validation Report")
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Location: New Delhi (28.61°N, 77.21°E, IST)")
    lines.append(f"Source: DP calendar (2025-2027) × Kaal engine ({len(needed)} unique computations)")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total DP entries | {len(rows)} |")
    lines.append(f"| Mapped to engine rules | {mapped} |")
    lines.append(f"| Not mapped | {unmapped} |")
    lines.append(f"| Exact match | {cats.get('EXACT_MATCH', 0)} |")
    lines.append(f"| Off by 1 day | {cats.get('OFF_BY_1', 0)} |")
    lines.append(f"| Off by 2-3 days | {cats.get('OFF_BY_X', 0)} |")
    lines.append(f"| Mismatch (>3 days) | {cats.get('MISMATCH', 0)} |")
    lines.append(f"| Engine error | {cats.get('ENGINE_ERROR', 0)} |")
    total_accounted = cats.get('EXACT_MATCH',0) + cats.get('OFF_BY_1',0)
    pct = 100 * total_accounted // max(mapped, 1)
    lines.append(f"| **Within ±1 day** | **{total_accounted}/{mapped} = {pct}%** |")
    lines.append("")
    
    # EXACT MATCHES
    exact = [r for r in rows if r["category"] == "EXACT_MATCH"]
    lines.append(f"## Exact Matches ({len(exact)} entries)")
    lines.append("")
    lines.append("| Year | Festival | Date | Rule |")
    lines.append("|------|----------|------|------|")
    for r in sorted(exact, key=lambda x: (x["year"], x["dp_date"])):
        lines.append(f"| {r['year']} | {r['name']} | {r['dp_date']} | {r['our_rule']} |")
    lines.append("")
    
    # OFF BY 1
    off1 = [r for r in rows if r["category"] == "OFF_BY_1"]
    lines.append(f"## Off by 1 Day ({len(off1)} entries)")
    lines.append("")
    lines.append("| Year | Festival | DP Date | Our Date | Diff | Rule |")
    lines.append("|------|----------|---------|----------|------|------|")
    for r in sorted(off1, key=lambda x: (x["year"], x["dp_date"])):
        dp, our = r["dp_date"], r["our_date"]
        diff = (datetime.strptime(our, "%Y-%m-%d") - datetime.strptime(dp, "%Y-%m-%d")).days
        lines.append(f"| {r['year']} | {r['name']} | {dp} | {our} | {diff:+d} | {r['our_rule']} |")
    lines.append("")
    
    # OFF BY X
    offx = [r for r in rows if r["category"] == "OFF_BY_X"]
    if offx:
        lines.append(f"## Off by 2-3 Days ({len(offx)} entries)")
        lines.append("")
        lines.append("| Year | Festival | DP Date | Our Date | Diff | Rule |")
        lines.append("|------|----------|---------|----------|------|------|")
        for r in sorted(offx, key=lambda x: (x["year"], x["dp_date"])):
            dp, our = r["dp_date"], r["our_date"]
            diff = (datetime.strptime(our, "%Y-%m-%d") - datetime.strptime(dp, "%Y-%m-%d")).days
            lines.append(f"| {r['year']} | {r['name']} | {dp} | {our} | {diff:+d} | {r['our_rule']} |")
        lines.append("")
    
    # MISMATCHES
    mism = [r for r in rows if r["category"] == "MISMATCH"]
    if mism:
        lines.append(f"## Mismatches ({len(mism)} entries)")
        lines.append("")
        lines.append("| Year | Festival | DP Date | Our Date | Rule |")
        lines.append("|------|----------|---------|----------|------|")
        for r in sorted(mism, key=lambda x: (x["year"], x["dp_date"])):
            lines.append(f"| {r['year']} | {r['name']} | {r['dp_date']} | {r['our_date']} | {r['our_rule']} |")
        lines.append("")
    
    # ENGINE ERRORS
    errs = [r for r in rows if r["category"] == "ENGINE_ERROR"]
    if errs:
        lines.append(f"## Engine Errors ({len(errs)} entries)")
        lines.append("")
        lines.append("| Year | Festival | DP Date | Mapped Rule |")
        lines.append("|------|----------|---------|-------------|")
        for r in sorted(errs, key=lambda x: (x["year"], x["name"])):
            lines.append(f"| {r['year']} | {r['name']} | {r['dp_date']} | {r.get('our_rule', '?')} |")
        lines.append("")
    
    # NOT MAPPED
    nm = [r for r in rows if r["category"] == "NOT_MAPPED"]
    if nm:
        lines.append(f"## Not Mapped ({len(nm)} entries)")
        lines.append("")
        lines.append("| Year | Festival | DP Date | Notes |")
        lines.append("|------|----------|---------|-------|")
        nm_names = set((r["name"], r["year"], r["dp_date"]) for r in nm)
        for name, y, d in sorted(nm_names, key=lambda x: (x[1], x[2])):
            # Note type
            fid = festival_id(name)
            if "ekadashi" in fid:
                note = "Ekadashi variant (general rule exists)"
            elif "purnima" in fid:
                note = "Purnima (no specific rule)"
            elif "sankranti" in fid:
                note = "Sankranti (solar event)"
            elif "grahan" in fid:
                note = "Eclipse"
            elif "gauna" in fid:
                note = "Alternate date"
            elif "amavas" in fid:
                note = "Amavasya"
            elif "parikrama" in fid or "kumbha" in fid:
                note = "Religious event"
            elif "solar" in name.lower() or "new year" in name.lower():
                note = "Solar event"
            else:
                note = "Uncategorized"
            lines.append(f"| {y} | {name} | {d} | {note} |")
        lines.append("")
    
    # PER-FESTIVAL ACCURACY TABLE
    lines.append("## Per-Festival Accuracy")
    lines.append("")
    lines.append("| Festival | Total | Exact | Off-1 | Off-X | Mismatch | Error | Unmapped |")
    lines.append("|----------|-------|-------|-------|-------|----------|-------|----------|")
    for name in sorted(fest_stats.keys()):
        fs = fest_stats[name]
        lines.append(f"| {name} | {fs['t']} | {fs['e']} | {fs['o1']} | {fs['ox']} | {fs['m']} | {fs['er']} | {fs['nm']} |")
    lines.append("")
    
    # ACTION ITEMS
    lines.append("## Action Items")
    lines.append("")
    
    # Off-by-1 pattern investigation
    off1_rules = Counter(r["our_rule"] for r in off1)
    if off1_rules:
        lines.append("### 1. Investigate ±1 Day Pattern")
        lines.append("")
        lines.append("The following rules consistently differ by 1 day from DP:")
        for rule, count in off1_rules.most_common():
            entries = [r for r in off1 if r["our_rule"] == rule]
            lines.append(f"- **{rule}** ({count} occurrences)")
            for e in entries[:3]:
                dp, our = e["dp_date"], e["our_date"]
                diff = (datetime.strptime(our, "%Y-%m-%d") - datetime.strptime(dp, "%Y-%m-%d")).days
                lines.append(f"  - {e['year']}: DP={dp}, Our={our} (diff={diff:+d})")
        lines.append("")
    
    # Engine errors
    if errs:
        lines.append("### 2. Fix Engine Errors")
        lines.append("")
        for r in errs:
            lines.append(f"- **{r['name']}** ({r['year']}): mapped to **{r['our_rule']}**")
        lines.append("")
    
    # Add missing rules
    if nm:
        purnimas = set(r["name"] for r in nm if festival_id(r["name"]).endswith("purnima"))
        sankrantis = set(r["name"] for r in nm if "sankranti" in festival_id(r["name"]))
        others = set(r["name"] for r in nm) - purnimas - sankrantis
        
        lines.append("### 3. Add Missing Festival Rules")
        lines.append("")
        if purnimas:
            lines.append(f"- Add **Purnima** rules: {', '.join(sorted(purnimas))}")
        if sankrantis:
            lines.append(f"- Add **Sankranti** rules: {', '.join(sorted(sankrantis))}")
        for name in sorted(others):
            fid = festival_id(name)
            if "ekadashi" not in fid and "gauna" not in fid and "kumbha" not in fid and "parikrama" not in fid:
                lines.append(f"- Add rule for **{name}**")
        lines.append("")
    
    # Save report
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(lines))
    sys.stderr.write(f"Saved {REPORT_FILE}\n")
    
    # ── Print summary ──
    sys.stderr.write(f"\n{'='*60}\n")
    sys.stderr.write(f"RESULTS:\n")
    sys.stderr.write(f"  Total: {len(rows)}\n")
    sys.stderr.write(f"  Mapped: {mapped}\n")
    sys.stderr.write(f"  Exact: {cats.get('EXACT_MATCH',0)}\n")
    sys.stderr.write(f"  Off-1: {cats.get('OFF_BY_1',0)}\n")
    sys.stderr.write(f"  Off-X: {cats.get('OFF_BY_X',0)}\n")
    sys.stderr.write(f"  Mismatch: {cats.get('MISMATCH',0)}\n")
    sys.stderr.write(f"  Engine err: {cats.get('ENGINE_ERROR',0)}\n")
    sys.stderr.write(f"  Unmapped: {cats.get('NOT_MAPPED',0)}\n")
    
    # Off-by-1 details
    if off1_rules:
        sys.stderr.write(f"\nOFF-BY-1 by rule:\n")
        for rule, count in off1_rules.most_common(10):
            sys.stderr.write(f"  {rule}: {count}\n")
    
    sys.stderr.write(f"\nSee {REPORT_FILE} for full details\n")
    sys.stderr.flush()


if __name__ == "__main__":
    run()
