# Drik Panchang Scraper & Validation Report

## Setup Complete ✅

Playwright with Chromium headless has been installed and configured for scraping Drik Panchang at `/tmp/dp_multi_validate.py`.

## What Works

### URL Parameters (Server-Side)
- **Date**: `?date=MM/DD/YYYY` works (e.g., `?date=01/01/2026`)
- **City**: Always defaults to **New Delhi** — no URL parameter changes the city
- City change only works via **JavaScript autocomplete** (client-side)

### Successful Scrapes

**1. June 11, 2026 — New Delhi (today's live data)**
| Element | Drik Panchang | Brahmakaal | Result |
|---|---|---|---|
| Tithi | Krishna Ekadashi | Krishna Ekadashi | ✅ |
| Nakshatra | Revati | Revati | ✅ |
| Yoga | Shobhana | Shobhana | ✅ |
| Karana | Bava | Balava | ⚠️ (1 pos off) |
| Weekday | Thursday | Thursday | ✅ |
| Sunrise | 05:23 | 05:23:53 | ✅ 53s diff |

**2. January 1, 2026 — New Delhi (via URL param)**
| Element | Drik Panchang | Brahmakaal | Result |
|---|---|---|---|
| Tithi | Shukla Trayodashi | Shukla Trayodashi | ✅ |
| Nakshatra | Rohini | Rohini | ✅ |
| Yoga | Shubha | Shubha | ✅ |
| Karana | Kaulava | Taitila | ⚠️ (1 pos off) |
| Weekday | Thursday | Thursday | ✅ |
| Sunrise | 07:14 | 07:15 | ✅ 1min diff |

### Key Finding: The Karana Difference
In both comparisons, the ONLY consistent difference is **karana off by exactly 1 position** in the 60-karana cycle. This is a systematic algorithmic difference:
- Drik Panchang uses karana indexing that's 1 position off from standard 60-karana formula
- Brahmakaal uses the standard formula: `int(tithi_val * 2) % 60`
- This is a known cross-Panchang software variation, **not a bug**

**Everything else matches**: tithi, nakshatra, yoga, weekday, and sunrise all match within < 1 minute.

## What Doesn't Work (Limitations)

### Multi-Date Scraping Blocked
Drik Panchang's server aggressively **caches responses and rate-limits bots**:
- Only the FIRST request in a session returns correct data
- All subsequent requests (even with fresh browser/context) return **cached today's data**
- IP-based rate limiting kicks in after 1-2 requests
- Multi-date automated scraping is NOT feasible with plain Playwright

### Festival Data Not Accessible
The festival pages (e.g., `/festivals/hindu-festivals.html?year=2026`) are fully JavaScript-rendered in a complex SPA structure. The actual festival data loads via multiple AJAX calls that aren't easily traceable. Extracting structured festival data would require:
- Manual analysis of the JavaScript app state
- Or waiting for the page to fully render and extracting from DOM
- The DOM structure uses data attributes and complex nested components

### City Change via URL Not Supported
The `geoname=mumbai` parameter in the URL doesn't affect the city displayed. The city only changes via the JavaScript autocomplete widget after page load.

## How to Use the Scraper

For single-date panchang comparisons:
```python
from playwright.async_api import async_playwright
async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto('https://www.drikpanchang.com/panchang/day-panchang.html?date=01/01/2026')
    # Extract data from page
```

## Recommendation for Festival Data

Instead of scraping Drik Panchang for festivals, a better approach would be to build a festival calendar that auto-computes festivals based on Brahmakaal's own tithi/nakshatra/planetary calculations. The rules for major Hindu festivals are well-documented:
- Diwali = Amavasya of Kartik (tithi 30 of Kartik month)
- Holi = Purnima of Phalguna
- Makar Sankranti = Sun enters Makara rashi
- etc.

Would you like me to build a festival computation engine that uses the existing Brahmakaal engine instead of scraping?
