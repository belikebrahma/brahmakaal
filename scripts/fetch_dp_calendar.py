"""
Batch DP Calendar Fetcher — fetches all years and builds the complete reference dataset.
"""

import re as _re
import json
import os
import urllib.request
import ssl
from datetime import date
from typing import List, Dict

CALENDAR_URL = "https://www.drikpanchang.com/calendars/hindu/hinducalendar.html?year={year}"

MONTH_NAMES = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12,
}


def _parse_date(date_str):
    """Parse 'January 3, 2026, Saturday' → date(2026, 1, 3)"""
    # Split on commas: ['January 3', ' 2026', ' Saturday']
    parts = [p.strip() for p in date_str.split(",")]
    if len(parts) < 2:
        return None
    month_day = parts[0]  # "January 3"
    year_str = parts[1]   # "2026"
    # Parse month and day
    md = month_day.split()
    if len(md) < 2:
        return None
    month = MONTH_NAMES.get(md[0])
    day = int(md[1])
    year = int(year_str)
    return date(year, month, day)


def fetch_year(year: int) -> List[Dict]:
    """Fetch festival calendar for one year."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    url = CALENDAR_URL.format(year=year)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    html = resp.read().decode("utf-8")
    
    names = _re.findall(r'dpEventName[^"]*"[^>]*>\s*([^<]+?)\s*<', html)
    dates = _re.findall(r'dpEventGregDate[^"]*"[^>]*>\s*([^<]+?)\s*<', html)
    
    festivals = []
    for name, date_text in zip(names, dates):
        name = name.strip()
        if "Hindu Festivals" in name:
            continue
        d = _parse_date(date_text.strip())
        if d:
            festivals.append({"name": name, "date": str(d), "year": year})
        else:
            print(f"  WARNING: Could not parse date '{date_text}' for '{name}'")
    
    return festivals


def fetch_all_years(years: List[int] = None) -> Dict[int, List[Dict]]:
    """Fetch festival calendars for multiple years."""
    if years is None:
        years = [2025, 2026, 2027]
    all_data = {}
    for year in years:
        print(f"Fetching {year}...")
        festivals = fetch_year(year)
        all_data[year] = festivals
        print(f"  -> {len(festivals)} festivals")
    return all_data


def save_all(data: Dict[int, List[Dict]], output_dir: str = "data/reference"):
    """Save individual year files and a merged file."""
    os.makedirs(output_dir, exist_ok=True)
    
    for year, festivals in data.items():
        path = os.path.join(output_dir, f"dp_calendar_{year}.json")
        with open(path, "w") as f:
            json.dump(festivals, f, indent=2)
        print(f"Saved {path} ({len(festivals)} festivals)")

    # Merged dataset — one entry per unique festival name
    merged = {}
    for year, festivals in data.items():
        for f in festivals:
            key = f["name"]
            if key not in merged:
                merged[key] = {"name": key}
            merged[key][str(year)] = f["date"]
    
    merged_path = os.path.join(output_dir, "dp_festivals_merged.json")
    meta = {
        "_meta": {
            "description": "Merged Drik Panchang festival calendar",
            "years": list(data.keys()),
            "total_unique": len(merged),
            "source": "drikpanchang.com",
        }
    }
    with open(merged_path, "w") as f:
        json.dump(meta | {"festivals": list(merged.values())}, f, indent=2)
    print(f"Saved {merged_path} ({len(merged)} unique festivals)")


def summarize(data: Dict[int, List[Dict]]):
    """Print summary by month."""
    for year, festivals in sorted(data.items()):
        months = {}
        for f in festivals:
            m = f["date"][:7]
            months[m] = months.get(m, 0) + 1
        print(f"\n{year}: {len(festivals)} festivals")
        for m in sorted(months.keys()):
            print(f"  {m}: {months[m]}")


if __name__ == "__main__":
    data = fetch_all_years([2025, 2026, 2027])
    save_all(data)
    summarize(data)
