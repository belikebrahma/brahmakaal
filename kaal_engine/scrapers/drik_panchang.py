"""
Drik Panchang Scraper

A scraper for extracting panchang data and festival dates from drikpanchang.com.
The site embeds data in JavaScript variables which are rendered client-side.
This module provides:

1. requests + beautifulsoup fallback: extracts data from HTML meta/structure
2. selenium-based scraper: uses headless Chrome to extract JS-embedded data
3. Manual data entry interface: for when scraping fails

Usage:
    from kaal_engine.scrapers.drik_panchang import DrikPanchangScraper
    scraper = DrikPanchangScraper()
    data = scraper.scrape_festival_list(2026)
"""

import json
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime

logger = logging.getLogger(__name__)


class DrikPanchangScraper:
    """Scrape Drik Panchang for festival and panchang data."""

    BASE_URL = "https://www.drikpanchang.com"

    FESTIVAL_URLS = {
        "ekadashi": "/vrats/ekadashidates.html",
        "purnima": "/vrats/purnimasidates.html",
        "amavasya": "/vrats/amavasyadates.html",
        "sankranti": "/festivals/sankranti/sankranti-calendar.html",
        "festivals": "/festivals/hindu-festivals.html",
    }

    def __init__(self, use_selenium: bool = False, headless: bool = True):
        self.use_selenium = use_selenium
        self.headless = headless
        self._driver = None

    def _get_selenium_driver(self):
        """Lazy-init selenium WebDriver."""
        if self._driver is not None:
            return self._driver
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self._driver = webdriver.Chrome(options=options)
            return self._driver
        except Exception as e:
            logger.warning(f"Selenium not available: {e}")
            return None

    def scrape_festival_list(self, year: int = 2026) -> List[Dict]:
        """
        Scrape the Hindu festival list page for a given year.

        Returns a list of {name, date, description} dicts.
        """
        url = f"{self.BASE_URL}{self.FESTIVAL_URLS['festivals']}?year={year}"

        if self.use_selenium:
            return self._scrape_with_selenium(url, year)
        else:
            return self._scrape_with_requests(url, year)

    def scrape_ekadashis(self, year: int = 2026) -> List[Dict]:
        """Scrape Ekadashi dates for a given year."""
        url = f"{self.BASE_URL}{self.FESTIVAL_URLS['ekadashi']}?year={year}"
        return self._scrape_table_page(url, "ekadashi", year)

    def scrape_purnimas(self, year: int = 2026) -> List[Dict]:
        """Scrape Purnima dates for a given year."""
        url = f"{self.BASE_URL}{self.FESTIVAL_URLS['purnima']}?year={year}"
        return self._scrape_table_page(url, "purnima", year)

    def scrape_amavasya(self, year: int = 2026) -> List[Dict]:
        """Scrape Amavasya dates for a given year."""
        url = f"{self.BASE_URL}{self.FESTIVAL_URLS['amavasya']}?year={year}"
        return self._scrape_table_page(url, "amavasya", year)

    def scrape_panchang(self, lat: float, lon: float, target_date: date,
                        timezone_offset: float = 5.5) -> Optional[Dict]:
        """
        Scrape the Drik Panchang panchang page for a specific date/location.
        
        The panchang data is embedded in JavaScript variables in the page.
        This method extracts those variables using regex.
        """
        url = (
            f"{self.BASE_URL}/panchang/day-panchang.html"
            f"?date={target_date.strftime('%Y%m%d')}"
        )

        try:
            import urllib.request
            import ssl

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Brahmakaal/1.0)"},
            )
            resp = urllib.request.urlopen(req, context=ctx, timeout=20)
            html = resp.read().decode("utf-8")

            return self._extract_panchang_vars(html, target_date)
        except Exception as e:
            logger.error(f"Failed to scrape panchang: {e}")
            return None

    def _scrape_with_requests(self, url: str, year: int) -> List[Dict]:
        """Fallback scraper using requests + regex for JS-extracted data."""
        import urllib.request
        import ssl

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Brahmakaal/1.0)"},
            )
            resp = urllib.request.urlopen(req, context=ctx, timeout=20)
            html = resp.read().decode("utf-8")

            # Extract dates embedded in HTML (look for date patterns)
            date_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d+"
            dates_found = re.findall(date_pattern, html)

            results = []
            for d in set(dates_found):  # deduplicate
                results.append({
                    "raw_text": d,
                    "year": year,
                    "source": "drikpanchang_regex",
                    "confidence": "low",
                })
            return results
        except Exception as e:
            logger.warning(f"Requests scraper failed: {e}")
            return []

    def _scrape_with_selenium(self, url: str, year: int) -> List[Dict]:
        """Full scraper using headless Chrome to execute JS."""
        driver = self._get_selenium_driver()
        if driver is None:
            logger.warning("Selenium not available, falling back to requests")
            return self._scrape_with_requests(url, year)

        try:
            driver.get(url)
            import time
            time.sleep(3)  # wait for JS to render

            # Try to find festival list elements
            elements = driver.find_elements_by_css_selector(
                ".festival-item, .festival-name, .dp-event, tr"
            )

            results = []
            for el in elements:
                text = el.text.strip()
                if text and len(text) > 5:
                    results.append({
                        "raw_text": text,
                        "year": year,
                        "source": "drikpanchang_selenium",
                        "confidence": "high",
                    })
            return results
        except Exception as e:
            logger.error(f"Selenium scraper failed: {e}")
            return []

    def _scrape_table_page(self, url: str, page_type: str,
                           year: int) -> List[Dict]:
        """Scrape a page with tabular date data."""
        if self.use_selenium:
            return self._scrape_with_selenium(url, year)
        return self._scrape_with_requests(url, year)

    def _extract_panchang_vars(self, html: str,
                               target_date: date) -> Optional[Dict]:
        """Extract panchang data from JavaScript variables embedded in HTML."""
        variables = {}

        # Extract all var assignments
        patterns = [
            r"var\s+(dp_\w+)\s*=\s*['\"]([^'\"]+)['\"]\s*;",
            r"var\s+(\w+)\s*=\s*['\"]([^'\"]+)['\"]\s*;",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, html):
                var_name = match.group(1)
                var_value = match.group(2)
                if "panchang" in var_name.lower() or any(
                    k in var_name.lower()
                    for k in ["tithi", "nakshatra", "yoga", "karana", "sunrise", "sunset"]
                ):
                    variables[var_name] = var_value

        # Try JSON data blocks
        json_pattern = r"var\s+dpPanchang\s*=\s*({[^;]+});"
        json_match = re.search(json_pattern, html, re.DOTALL)
        if json_match:
            try:
                import json as json_mod
                data = json_mod.loads(json_match.group(1))
                variables.update(data)
            except json_mod.JSONDecodeError:
                pass

        return {
            "date": str(target_date),
            "extracted_vars": variables,
            "var_count": len(variables),
            "source": "drikpanchang_regex",
        }

    def close(self):
        """Clean up selenium driver if used."""
        if self._driver:
            self._driver.quit()
            self._driver = None


def validate_against_reference(
    computed: Dict[str, str],
    drik_data: Dict[str, str],
) -> Dict:
    """
    Cross-validate computed festival dates against Drik Panchang data.

    Args:
        computed: {festival_name: date_str} from Brahmakaal
        drik_data: {festival_name: date_str} from Drik Panchang

    Returns:
        {festival_name: {computed, drik, match, diff_days}}
    """
    results = {}
    for name, comp_date in computed.items():
        dp_date = drik_data.get(name)
        if dp_date:
            try:
                d1 = datetime.strptime(comp_date, "%Y-%m-%d").date()
                d2 = datetime.strptime(dp_date, "%Y-%m-%d").date()
                diff = abs((d1 - d2).days)
                results[name] = {
                    "computed": comp_date,
                    "drik_panchang": dp_date,
                    "match": diff == 0,
                    "diff_days": diff,
                }
            except ValueError:
                results[name] = {
                    "computed": comp_date,
                    "drik_panchang": dp_date,
                    "match": "unknown",
                    "diff_days": -1,
                }
        else:
            results[name] = {
                "computed": comp_date,
                "drik_panchang": None,
                "match": "no_dp_data",
                "diff_days": -1,
            }
    return results
