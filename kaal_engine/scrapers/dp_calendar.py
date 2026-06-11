"""
Full Drik Panchang Festival Calendar Scraper.

Scrapes the complete Hindu calendar for a given year from drikpanchang.com,
extracting ALL festivals with their dates. No pre-defined rule list needed.

Usage:
    from kaal_engine.scrapers.dp_calendar import fetch_festival_calendar
    festivals = fetch_festival_calendar(2026)
    # Returns list of {"name": "Diwali", "date": "2026-11-09", ...}
"""

import re
import json
import os
import time
import urllib.request
import ssl
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = __import__('logging').getLogger(__name__)

CALENDAR_URL = "https://www.drikpanchang.com/calendars/hindu/hinducalendar.html?year={year}"

# Month name mapping (DP uses full month names like "January")
MONTH_NAMES = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}


def _fetch_html(year: int) -> Optional[str]:
    """Fetch the DP Hindu calendar page."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = CALENDAR_URL.format(year=year)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        return resp.read().decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def _parse_festival_date(date_str: str):
    """Parse 'January 3, 2026, Saturday' → date(2026, 1, 3)"""
    parts = [p.strip() for p in date_str.strip().split(",")]
    if len(parts) < 2:
        return None
    month_day = parts[0]  # "January 3"
    year_str = parts[1]   # "2026"
    md = month_day.split()
    if len(md) < 2:
        return None
    month_num = MONTH_NAMES.get(md[0])
    if not month_num:
        return None
    day = int(md[1])
    return date(int(year_str), month_num, day)


def parse_festival_html(html: str) -> List[Dict]:
    """
    Parse the DP Hindu calendar HTML to extract festivals.
    
    The HTML has a repeating pattern:
      <div class="dpEventName ...">Festival Name</div>
      <div class="dpEventDate ...">January 3, 2026, Saturday</div>
    
    Returns:
        List of dicts: [{"name": "Diwali", "date": "2026-11-09", ...}]
    """
    # Find all dpEvent elements in order
    # Pattern: dpEventName or dpEventGregDate divs
    all_events = re.findall(
        r'class="([^"]*dpEvent(?:Name|GregDate)[^"]*)"[^>]*>\s*([^<]+?)\s*<',
        html
    )
    
    festivals = []
    current_name = None
    
    for css_class, text in all_events:
        text = text.strip()
        if not text:
            continue
        
        if "dpEventName" in css_class:
            # Skip the header "2026 Hindu Festivals"
            if text == f"2026 Hindu Festivals":
                continue
            current_name = text
        
        elif "dpEventGregDate" in css_class and current_name:
            parsed = _parse_festival_date(text)
            if parsed:
                festivals.append({
                    "name": current_name,
                    "date": str(parsed),
                    "date_obj": parsed,
                    "original_date_text": text,
                })
            else:
                logger.warning(f"Could not parse date '{text}' for '{current_name}'")
            current_name = None
    
    return festivals


# ─── Festival-specific page scraper ──────────────────────────────────

def fetch_festival_details(name: str, dt: date) -> Dict:
    """
    Fetch details about a specific festival from DP's panchang page.
    Returns tithi, sunrise, nakshatra etc.
    """
    from kaal_engine.scrapers.dp_fetcher import fetch_dp_panchang
    
    result = fetch_dp_panchang(dt.year, dt.month, dt.day)
    
    tithi_info = result.get("tithi", {}).get("decoded", {})
    sunrise = result.get("sunrise_sunset", {}).get("sunrise", "")
    nakshatra = result.get("nakshatra", {}).get("name", "")
    
    return {
        "tithi_name": tithi_info.get("name", ""),
        "tithi_encoded": tithi_info.get("tithi_num", 0),
        "sunrise": sunrise,
        "nakshatra": nakshatra,
    }


def fetch_festival_calendar(year: int, with_details: bool = False) -> List[Dict]:
    """
    Fetch the complete festival calendar for a year.
    
    Args:
        year: Gregorian year (e.g., 2026)
        with_details: If True, also fetch tithi/sunrise for each festival date
    
    Returns:
        List of festival dicts sorted by date
    """
    html = _fetch_html(year)
    if not html:
        return []
    
    festivals = parse_festival_html(html)
    
    # Sort by date
    festivals.sort(key=lambda x: x["date_obj"])
    
    # Add IDs
    for i, f in enumerate(festivals):
        f["id"] = i + 1
        # Remove date_obj (not JSON serializable)
        del f["date_obj"]
    
    # Optionally fetch details
    if with_details:
        logger.info(f"Fetching details for {len(festivals)} festivals...")
        for f in festivals:
            dt_parts = f["date"].split("-")
            dt = date(int(dt_parts[0]), int(dt_parts[1]), int(dt_parts[2]))
            details = fetch_festival_details(f["name"], dt)
            f.update(details)
            time.sleep(0.5)
    
    return festivals


def save_festival_calendar(festivals: List[Dict], path: str):
    """Save festival calendar to JSON file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(festivals, f, indent=2)
    logger.info(f"Saved {len(festivals)} festivals to {path}")


# ─── Summary / Statistics ─────────────────────────────────────────

def festival_summary(festivals: List[Dict]) -> str:
    """Generate a summary of the festival calendar."""
    months = {}
    for f in festivals:
        month = f["date"][:7]
        if month not in months:
            months[month] = []
        months[month].append(f["name"])
    
    lines = [f"Total festivals: {len(festivals)}"]
    for month in sorted(months.keys()):
        names = months[month]
        lines.append(f"  {month}: {len(names)} festivals")
        for n in names[:5]:
            lines.append(f"    - {n}")
        if len(names) > 5:
            lines.append(f"    ... and {len(names)-5} more")
    
    return "\n".join(lines)


# ─── Cross-validate against Kaal engine ──────────────────────────

def cross_validate(kaal_engine, festivals: List[Dict],
                   lat: float = 28.6139, lon: float = 77.2090,
                   tz: float = 5.5) -> List[Dict]:
    """
    Cross-validate Kaal engine festival dates against DP calendar.
    
    For each festival in the DP calendar, checks:
    1. What tithi does Kaal compute for that date?
    2. Does the date match our FestivalEngine prediction (if we have one)?
    
    Returns:
        List of comparison results
    """
    from datetime import datetime
    from kaal_engine.core.festivals import FestivalEngine
    
    fe = FestivalEngine(kaal_engine, lat=lat, lod=lon, 
                        timezone_offset=tz, elevation=0)
    
    # Compute our festival dates for the year
    year = int(festivals[0]["date"][:4])
    our_festivals = fe.calculate_festival_dates(year)
    our_map = {}
    for fd in our_festivals:
        key = fd.festival_rule.name.lower().replace(" ", "_").replace("-", "_")
        our_map[fd.festival_rule.name] = str(fd.date)
    
    comparisons = []
    for f in festivals:
        dt_parts = f["date"].split("-")
        d = date(int(dt_parts[0]), int(dt_parts[1]), int(dt_parts[2]))
        query_dt = datetime(d.year, d.month, d.day, 12, 0, 0)
        
        panchang = kaal_engine.get_panchang(lat, lon, query_dt, timezone_offset=tz)
        
        # Check if we have this festival in our engine
        our_date = None
        for our_name, od in our_map.items():
            if f["name"].lower() in our_name.lower() or our_name.lower() in f["name"].lower():
                our_date = od
                break
        
        comparisons.append({
            "dp_festival": f["name"],
            "dp_date": f["date"],
            "dp_tithi": f.get("tithi_name", panchang.get("tithi_name", "")),
            "kaal_tithi": panchang.get("tithi_name", ""),
            "kaal_raw_tithi": round(panchang.get("tithi", 0), 4),
            "our_festival_date": our_date,
            "date_match": our_date == f["date"] if our_date else None,
        })
    
    return comparisons


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    
    print(f"Fetching festival calendar for {year}...")
    festivals = fetch_festival_calendar(year, with_details=False)
    
    if festivals:
        print(f"\nFound {len(festivals)} festivals:\n")
        for f in festivals:
            print(f"  {f['date']}  {f['name']}")
        
        save_festival_calendar(festivals, f"data/reference/dp_calendar_{year}.json")
    else:
        print("No festivals found!")
