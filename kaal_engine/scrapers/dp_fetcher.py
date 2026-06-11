"""
Drik Panchang Data Fetcher

Fetches and decodes hex-embedded panchang data from drikpanchang.com
for building validation reference datasets.

Usage:
    from kaal_engine.scrapers.dp_fetcher import fetch_dp_panchang, decode_dp_tithi
    
    data = fetch_dp_panchang(2026, 11, 9)  # Diwali
    tithi = decode_dp_tithi(data)  # Returns: {'tithi_num': 30, 'name': 'Krishna Amavasya', ...}
"""

import re
import json
import logging
from datetime import date, datetime
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)

BASE_URL = "https://www.drikpanchang.com"
PANCHANG_URL = "/panchang/day-panchang.html?date={day:02d}/{month:02d}/{year}"

# Card classes for text extraction
CARD_CLASSES = {
    "dpCorePanchangCardWrapper": "core_panchang",
    "dpLunarDateCardWrapper": "lunar_calendar",
    "dpRashiNakshatraCardWrapper": "rashi_nakshatra",
    "dpSunriseMoonriseCardWrapper": "sun_moon_timings",
    "dpAuspiciousCardWrapper": "auspicious_times",
    "dpInauspiciousCardWrapper": "inauspicious_times",
    "dpPanchakaCardWrapper": "panchaka",
    "dpAyanaRituCardWrapper": "ayana_ritu",
    "dpDayEventCardWrapper": "day_events",
}


def _get_html(year: int, month: int, day: int) -> Optional[str]:
    """Fetch the Drik Panchang page HTML."""
    import urllib.request
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = BASE_URL + PANCHANG_URL.format(year=year, month=month, day=day)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; Brahmakaal/1.0)"},
        )
        resp = urllib.request.urlopen(req, context=ctx, timeout=20)
        return resp.read().decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None


def extract_data_attrs(html: str) -> Dict[str, str]:
    """Extract key=value pairs from data-element-info attrs."""
    data = {}
    for info in re.findall(r'data-element-info="([^"]+)"', html):
        for part in info.split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                data[k.strip()] = v.strip()
    return data


def extract_card_texts(html: str) -> Dict[str, List[str]]:
    """Extract visible text from panchang card sections."""
    cards = {}
    for card_class, card_name in CARD_CLASSES.items():
        pattern = f'class="[^"]*?{card_class}[^"]*"'
        for m in re.finditer(pattern, html):
            snippet = html[m.start() : m.start() + 2000]
            texts = re.findall(r">([^<]{3,120})<", snippet)
            clean = [
                t.strip()
                for t in texts
                if t.strip() and not t.strip().startswith("<") and len(t.strip()) > 2
            ][:15]
            if clean:
                cards[card_name] = clean
            break
    return cards


def decode_tithi(data_vals: Dict[str, str]) -> Dict:
    """
    Decode tithi from DP hex-encoded data.
    
    DP encodes tithi as a 1-30 number in data_vals['0x30bb0006']:
      1-15 = Shukla Paksha (waxing)
      16-30 = Krishna Paksha (waning), where 16=Krishna 1, 30=Krishna 15 (Amavasya)
    """
    raw = data_vals.get("0x30bb0006", "")
    try:
        dp_tithi = int(raw.split()[0])  # Handle "26" or "26 something"
    except (ValueError, IndexError):
        return {"dp_raw": raw, "decoded": None}

    if dp_tithi <= 0 or dp_tithi > 30:
        return {"dp_raw": raw, "decoded": None}

    if dp_tithi <= 15:
        paksha = "shukla"
        tithi_num = dp_tithi
    else:
        paksha = "krishna"
        tithi_num = dp_tithi - 15

    # Build tithi name
    TITHI_NAMES = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
    ]
    if tithi_num <= 14:
        name = f"{paksha.title()} {TITHI_NAMES[tithi_num - 1]}"
    elif tithi_num == 15:
        if paksha == "shukla":
            name = "Shukla Purnima"
        else:
            name = "Krishna Amavasya"
    else:
        name = "Unknown"

    return {
        "dp_raw": raw,
        "dp_encoded": dp_tithi,
        "decoded": {
            "tithi_num": dp_tithi,
            "paksha": paksha,
            "tithi_index": tithi_num,
            "name": name,
        },
    }


def decode_sunrise_sunset(data_vals: Dict[str, str]) -> Dict:
    """Extract sunrise/sunset times. Hex keys 0x30bb0009 = sunrise, 0x30bb000a = sunset."""
    sunrise = data_vals.get("0x30bb0009", "")
    sunset = data_vals.get("0x30bb000a", "")

    def extract_time(val: str) -> str:
        parts = val.split()
        return parts[0] if parts else ""

    return {
        "sunrise_raw": sunrise,
        "sunset_raw": sunset,
        "sunrise": extract_time(sunrise),
        "sunset": extract_time(sunset),
    }


def decode_nakshatra(data_vals: Dict[str, str]) -> Dict:
    """Extract nakshatra from DP hex data. Key: 0x30bb000f"""
    raw = data_vals.get("0x30bb000f", "")
    try:
        nakshatra_num = int(raw.split()[0])
    except (ValueError, IndexError):
        return {"raw": raw, "nakshatra_num": None}

    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
        "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha",
        "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
        "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
    ]

    if 1 <= nakshatra_num <= 27:
        name = NAKSHATRAS[nakshatra_num - 1]
    else:
        name = None

    return {"raw": raw, "nakshatra_num": nakshatra_num, "name": name}


def fetch_dp_panchang(year: int, month: int, day: int) -> Dict:
    """
    Fetch and decode Drik Panchang data for a specific date.
    
    Returns:
        Dict with keys:
          - date: str
          - success: bool
          - tithi: decoded tithi info
          - sunrise_sunset: decoded timing info
          - nakshatra: decoded nakshatra info
          - card_texts: visible text from panchang cards
          - error: error message if failed
    """
    html = _get_html(year, month, day)
    if html is None:
        return {
            "date": f"{year}-{month:02d}-{day:02d}",
            "success": False,
            "error": "Failed to fetch page",
        }

    data_vals = extract_data_attrs(html)
    cards = extract_card_texts(html)

    result = {
        "date": f"{year}-{month:02d}-{day:02d}",
        "success": True,
        "tithi": decode_tithi(data_vals),
        "sunrise_sunset": decode_sunrise_sunset(data_vals),
        "nakshatra": decode_nakshatra(data_vals),
        "card_texts": cards,
        "raw_keys": list(data_vals.keys())[:5],
    }

    # Add additional raw values for debugging
    for key_prefix, label in [("0x30bb0014", "yoga"), ("0x30bb0015", "karana")]:
        if key_prefix in data_vals:
            result[f"{label}_raw"] = data_vals[key_prefix]

    return result


def batch_fetch(year: int, month: int = None, day: int = None) -> List[Dict]:
    """
    Batch fetch panchang data for a range of dates.
    
    Args:
        year: Target year
        month: If set, fetch all days in this month
        day: If set (with month), fetch single day. If neither, fetch all 365 days.
    
    Returns:
        List of decoded panchang dicts
    """
    from datetime import date, timedelta

    if month and day:
        dates = [date(year, month, day)]
    elif month:
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        dates = [date(year, month, d) for d in range(1, max_day + 1)]
    else:
        start = date(year, 1, 1)
        end = date(year, 12, 31)
        dates = [start + timedelta(days=i) for i in range((end - start).days + 1)]

    results = []
    for d in dates:
        result = fetch_dp_panchang(d.year, d.month, d.day)
        results.append(result)
        if result.get("success"):
            t = result.get("tithi", {}).get("decoded", {})
            ss = result.get("sunrise_sunset", {})
            logger.info(f"  {d}: T={t.get('tithi_num','?'):>2s} {t.get('name',''):25s} "
                       f"SR={ss.get('sunrise','?'):5s} SS={ss.get('sunset','?'):5s}")
        else:
            logger.warning(f"  {d}: FAILED")

    return results


def cross_validate_brahmakaal(dp_results: List[Dict], kaal_engine) -> List[Dict]:
    """
    Cross-validate Brahmakaal engine against Drik Panchang data.
    
    Args:
        dp_results: List from batch_fetch()
        kaal_engine: Instance of Kaal class
    
    Returns:
        List of comparison dicts
    """
    from datetime import datetime

    comparisons = []
    for dp in dp_results:
        if not dp.get("success"):
            continue

        # Parse date
        date_str = dp["date"]
        parts = date_str.split("-")
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])

        # Get Brahmakaal panchang at noon (closest to DP's computation epoch)
        dt = datetime(y, m, d, 12, 0, 0)
        our = kaal_engine.get_panchang(28.6139, 77.2090, dt, timezone_offset=5.5)

        dp_tithi = dp.get("tithi", {}).get("decoded", {})
        dp_sun = dp.get("sunrise_sunset", {})

        # Our tithi in 1-30 cycle
        our_t = our.get("tithi", 0)
        our_cycle = int(our_t) % 30
        if our_cycle == 0:
            our_cycle = 30

        comparisons.append({
            "date": date_str,
            "dp_tithi_encoded": dp.get("tithi", {}).get("dp_encoded"),
            "dp_tithi_name": dp_tithi.get("name"),
            "our_tithi": our_cycle,
            "our_tithi_name": our.get("tithi_name"),
            "tithi_name_match": (dp_tithi.get("name", "").lower()
                                 == our.get("tithi_name", "").lower()),
            "dp_sunrise": dp_sun.get("sunrise"),
            "dp_sunset": dp_sun.get("sunset"),
        })

    return comparisons
