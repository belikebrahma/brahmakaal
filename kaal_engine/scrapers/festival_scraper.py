"""
Festival Date Scraper — Scrapes Drik Panchang to build ground-truth reference data.

Strategy:
  For each of our 37 festival rules, we:
    1. Compute the predicted date using our engine (TithiScanner)
    2. Fetch DP panchang for that date (±2 day window) 
    3. Check whether DP's tithi matches the expected festival tithi
    4. Build a comprehensive reference dataset from DP-verified dates

Usage:
    from kaal_engine.scrapers.festival_scraper import FestivalScraper
    from kaal_engine.kaal import Kaal
    from kaal_engine.core.festivals import FestivalEngine

    k = Kaal("de421.bsp")
    fe = FestivalEngine(k, lat=28.6139, lod=77.2090, timezone_offset=5.5, elevation=0)
    scraper = FestivalScraper(fe)

    # Scrape all festivals for 2026
    results = scraper.scrape_year(2026)
    scraper.save_results("data/reference/dp_scraped_festivals.json")
"""

import logging
import time
import json
import os
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from kaal_engine.scrapers.dp_fetcher import fetch_dp_panchang, decode_tithi, extract_data_attrs, _get_html
from kaal_engine.core.festivals import FestivalEngine, FestivalType

logger = logging.getLogger(__name__)

# Tithi name lookup for matching
TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
]


def tithi_key(paksha: str, tithi_num: int) -> str:
    """Canonical key for a tithi, e.g. 'krishna_15' = Krishna Amavasya."""
    return f"{paksha}_{tithi_num}"


def expected_tithi_for_rule(rule) -> List[str]:
    """
    Return the expected DP tithi key(s) for a festival rule.
    
    Returns list of 'paksha_num' strings, e.g. ['krishna_15'] for Amavasya.
    Multiple entries for multi-day or ambiguous festivals (e.g. Ganesh Chaturthi vs Vinayaka).
    """
    from kaal_engine.core.festivals import FestivalType

    if rule.festival_type == FestivalType.LUNAR:
        return [tithi_key(rule.paksha, rule.tithi)]
    
    elif rule.festival_type == FestivalType.SOLAR:
        if rule.special_rules.get("summer_solstice") or rule.special_rules.get("winter_solstice"):
            return ["solar_solstice"]
        return [f"solar_month_{rule.solar_month}_day_{rule.solar_day}"]
    
    elif rule.festival_type == FestivalType.NAKSHATRA:
        return [f"nakshatra_{rule.nakshatra}"]
    
    elif rule.festival_type == FestivalType.CALCULATED:
        if rule.tithi == 11:
            return [f"shukla_11", f"krishna_11"]  # Ekadashi - can be either paksha
        return [f"calculated_{rule.name.lower().replace(' ', '_')}"]
    
    return []


def get_dp_tithi_for_date(year: int, month: int, day: int) -> Optional[Dict]:
    """
    Fetch a single date from DP and extract tithi info.
    Returns dict with tithi_key, tithi_name, or None on failure.
    """
    result = fetch_dp_panchang(year, month, day)
    if not result.get("success"):
        return None
    
    tithi_info = result.get("tithi", {})
    decoded = tithi_info.get("decoded")
    if not decoded:
        return None
    
    dp_tithi_num = decoded.get("tithi_num", 0)  # 1-30
    dp_paksha = decoded.get("paksha", "")
    dp_tithi_index = decoded.get("tithi_index", 0)  # 1-15 within paksha
    
    if dp_tithi_num <= 15:
        key = f"shukla_{dp_tithi_num}"
    else:
        key = f"krishna_{dp_tithi_num - 15}"
    
    return {
        "date": f"{year}-{month:02d}-{day:02d}",
        "tithi_key": key,
        "tithi_name": decoded.get("name", ""),
        "dp_encoded": dp_tithi_num,
        "dp_tithi_index": dp_tithi_index,
        "dp_paksha": dp_paksha,
        "raw": tithi_info,
    }


def find_best_dp_date_for_tithi(target_tithi_key: str, year: int, 
                                  approx_month: int = 6, search_window: int = 45) -> Optional[date]:
    """
    Find the exact date in a window where DP shows the target tithi.
    
    Args:
        target_tithi_key: e.g. 'krishna_15' for Amavasya
        year: Target year
        approx_month: Approximate month (1-12) to center the search
        search_window: ± days around approx date
    
    Returns:
        date object if found, None otherwise
    """
    from datetime import date, timedelta
    
    center_date = date(year, approx_month, 15)
    start = center_date - timedelta(days=search_window)
    end = center_date + timedelta(days=search_window)
    
    current = start
    while current <= end:
        result = get_dp_tithi_for_date(current.year, current.month, current.day)
        if result and result.get("tithi_key") == target_tithi_key:
            return current
        current += timedelta(days=1)
        time.sleep(0.3)  # Be polite to DP
    
    return None


def compute_festival_date(engine: FestivalEngine, rule) -> Optional[date]:
    """Compute a single festival date using our engine."""
    try:
        if rule.festival_type == FestivalType.LUNAR:
            dates = engine._calculate_lunar_festival(rule, 2026)
        elif rule.festival_type == FestivalType.SOLAR:
            dates = engine._calculate_solar_festival(rule, 2026)
        elif rule.festival_type == FestivalType.NAKSHATRA:
            dates = engine._calculate_nakshatra_festival(rule, 2026)
        elif rule.festival_type == FestivalType.CALCULATED:
            dates = engine._calculate_special_festival(rule, 2026)
        else:
            return None
        
        if dates:
            d = dates[0].date
            if isinstance(d, str):
                from datetime import datetime
                return datetime.strptime(d, "%Y-%m-%d").date()
            return d
        return None
    except Exception as e:
        logger.error(f"Error computing {rule.name}: {e}")
        return None


def estimate_lunar_month_date(year: int, month_name: str) -> int:
    """Estimate Gregorian month number for a Hindu lunar month."""
    hindu_months = [
        "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
        "Shravana", "Bhadrapada", "Ashwin", "Kartik",
        "Margashirsha", "Pausha", "Magha", "Phalguna"
    ]
    try:
        idx = hindu_months.index(month_name)
        # Hindu months start ~mid-March (Gregorian month 3)
        greg_month = (idx + 3) % 12
        if greg_month == 0:
            greg_month = 12
        return greg_month
    except ValueError:
        return 6


class FestivalScraper:
    """
    Scrapes Drik Panchang to build a ground-truth reference dataset
    of festival dates, then compares against our computed values.
    """
    
    def __init__(self, festival_engine: FestivalEngine):
        self.engine = festival_engine
        self.results: Dict[str, Dict] = {}
        self._dp_cache: Dict[str, Dict] = {}
    
    def scrape_festival(self, rule, year: int = 2026) -> Dict:
        """
        Scrape DP for a single festival: compute our date, validate against DP.
        
        Returns dict with:
          - festival_name
          - our_computed_date
          - dp_date (ground truth from DP, if found)
          - dp_tithi_match: bool (does DP's tithi match our prediction?)
          - status: 'match' | 'mismatch' | 'not_found' | 'error'
        """
        logger.info(f"Scraping {rule.name} ({rule.festival_type.name})...")
        result = {
            "festival_name": rule.name,
            "type": rule.festival_type.name,
            "computed_date": None,
            "dp_date": None,
            "dp_tithi_match": False,
            "dp_tithi_at_computed": None,
            "status": "error",
            "notes": "",
        }
        
        # Step 1: Compute our date
        t0 = time.time()
        our_date = compute_festival_date(self.engine, rule)
        result["computation_time_s"] = round(time.time() - t0, 1)
        
        if our_date is None:
            result["notes"] = "Could not compute date"
            self.results[rule.name] = result
            return result
        
        result["computed_date"] = str(our_date)
        
        # Step 2: Get expected tithi key(s)
        expected = expected_tithi_for_rule(rule)
        
        # Step 3: Fetch DP data for our computed date
        dp_info = self._get_dp_cached(our_date.year, our_date.month, our_date.day)
        
        if dp_info is None:
            result["notes"] = "DP fetch failed"
            self.results[rule.name] = result
            return result
        
        dp_tithi_key = dp_info.get("tithi_key", "")
        result["dp_tithi_at_computed"] = dp_tithi_key
        result["dp_tithi_name_at_computed"] = dp_info.get("tithi_name", "")
        
        # Step 4: Check if tithi matches
        if dp_tithi_key in expected:
            result["dp_date"] = str(our_date)
            result["dp_tithi_match"] = True
            result["status"] = "match"
            result["notes"] = f"DP confirms {dp_info.get('tithi_name', '?')} on {our_date}"
        else:
            # Mismatch — expand search window to find the correct date
            logger.info(f"  DP shows {dp_tithi_key} on {our_date}, expected {expected}")
            result["status"] = "mismatch"
            result["notes"] = f"DP shows {dp_tithi_key} on computed date, expected {expected}"
            
            # Try ±5 days around our computed date
            for offset in range(1, 6):
                for sign in [1, -1]:
                    check = our_date + timedelta(days=sign * offset)
                    dp_check = self._get_dp_cached(check.year, check.month, check.day)
                    if dp_check and dp_check.get("tithi_key") in expected:
                        result["dp_date"] = str(check)
                        result["dp_tithi_match"] = True
                        result["status"] = "adjacent_found"
                        result["notes"] += f"; correct date found at {check} ({dp_check.get('tithi_name', '?')})"
                        break
                if result.get("dp_date"):
                    break
            
            if not result.get("dp_date"):
                result["notes"] += "; no adjacent date with correct tithi found in ±5 days"
        
        self.results[rule.name] = result
        return result
    
    def scrape_year(self, year: int = 2026, festival_names: List[str] = None) -> Dict:
        """
        Scrape all (or specified) festivals for a year.
        
        Args:
            year: Target year
            festival_names: If set, only scrape these festivals (by name)
        
        Returns:
            Dict of festival_name -> result
        """
        rules = self.engine.festival_rules
        if festival_names:
            rules = [r for r in rules if r.name in festival_names]
        
        matches = 0
        mismatches = 0
        errors = 0
        adjacent = 0
        
        for i, rule in enumerate(rules):
            logger.info(f"[{i+1}/{len(rules)}] {rule.name}...")
            r = self.scrape_festival(rule, year)
            
            if r["status"] == "match":
                matches += 1
            elif r["status"] == "adjacent_found":
                adjacent += 1
            elif r["status"] == "mismatch":
                mismatches += 1
            else:
                errors += 1
            
            status_icon = {"match": "✅", "adjacent_found": "🔶", "mismatch": "❌", "error": "⚠️"}.get(r["status"], "?")
            logger.info(f"  {status_icon} {rule.name}: our={r.get('computed_date','?')} dp={r.get('dp_date','?')} ({r.get('notes','')})")
        
        self.summary = {
            "year": year,
            "total": len(rules),
            "matches": matches,
            "adjacent_found": adjacent,
            "mismatches": mismatches,
            "errors": errors,
            "accuracy_pct": round((matches + adjacent) / max(len(rules), 1) * 100, 1),
        }
        
        return self.results
    
    def _get_dp_cached(self, year: int, month: int, day: int) -> Optional[Dict]:
        """Fetch DP data with in-memory cache."""
        key = f"{year}-{month:02d}-{day:02d}"
        if key in self._dp_cache:
            return self._dp_cache[key]
        
        result = get_dp_tithi_for_date(year, month, day)
        self._dp_cache[key] = result
        time.sleep(0.3)  # Polite delay
        return result
    
    def save_results(self, path: str):
        """Save scraping results to a JSON file."""
        output = {
            "_meta": {
                "generated_by": "FestivalScraper",
                "description": "Festival dates scraped from Drik Panchang with engine cross-validation",
                "location": "New Delhi, India (28.6139°N, 77.2090°E)",
                "engine_version": "kaal_engine",
            },
            "results": self.results,
            "summary": getattr(self, "summary", {}),
        }
        
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(output, f, indent=2)
        logger.info(f"Saved {len(self.results)} results to {path}")
    
    def generate_reference_dataset(self, year: int = 2026) -> Dict:
        """
        Generate a clean reference dataset from scraping results.
        
        Returns a dict suitable for merging into festival_dates.json:
        {
            "2026": {
                "Diwali": {"date": "2026-11-09", "source": "drik_panchang_scrape", ...},
                ...
            },
            "_meta": {...}
        }
        """
        if not self.results:
            logger.warning("No results yet. Run scrape_year() first.")
            return {}
        
        reference = {}
        for name, r in self.results.items():
            dp_date = r.get("dp_date")
            if dp_date:
                entry = {
                    "date": dp_date,
                    "source": "drik_panchang_scrape",
                    "method": "dp_fetch",
                    "engine_validation": r.get("status", ""),
                    "engine_date": r.get("computed_date"),
                }
                if r.get("dp_tithi_name_at_computed"):
                    entry["dp_tithi"] = r["dp_tithi_name_at_computed"]
                reference[name] = entry
        
        return {
            str(year): reference,
            "_meta": {
                "version": "2.0",
                "generated_by": "FestivalScraper.generate_reference_dataset()",
                "years_covered": [str(year)],
                "notes": "Dates confirmed via Drik Panchang HTML data extraction",
                "accuracy": getattr(self, "summary", {}).get("accuracy_pct", 0),
            },
        }


def merge_reference_datasets(existing_path: str, new_data: Dict, output_path: str):
    """Merge a generated reference dataset into the existing one."""
    if os.path.exists(existing_path):
        with open(existing_path) as f:
            existing = json.load(f)
    else:
        existing = {}
    
    # Merge year data
    for year_key, festivals in new_data.items():
        if year_key == "_meta":
            continue
        if year_key not in existing:
            existing[year_key] = {}
        existing[year_key].update(festivals)
    
    # Update meta
    if "_meta" in existing and "_meta" in new_data:
        existing["_meta"].update({
            k: v for k, v in new_data["_meta"].items()
            if k != "years_covered"
        })
        # Merge years_covered
        existing_years = set(existing["_meta"].get("years_covered", []))
        new_years = set(new_data["_meta"].get("years_covered", []))
        existing["_meta"]["years_covered"] = sorted(existing_years | new_years)
    elif "_meta" in new_data:
        existing["_meta"] = new_data["_meta"]
    
    with open(output_path, "w") as f:
        json.dump(existing, f, indent=2)
    logger.info(f"Merged reference dataset saved to {output_path}")
