"""
TithiScanner — Core Algorithm for Hindu Festival Date Calculation

Scans date ranges using Brahmakaal's Kaal engine to find exact dates
when specific tithis, nakshatras, or sankrantis occur.

This replaces the placeholder month-map approach in FestivalEngine with
real astronomical computation.

Phase 1 deliverable from FESTIVAL_CALENDAR_PLAN.md
"""

from datetime import datetime, timedelta, date
from typing import Optional, List, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class TithiScanner:
    """
    Scans date ranges to find when specific tithis occur.
    
    Uses Brahmakaal's own Kaal.get_panchang() to compute tithi for each
    candidate date, then matches against the target tithi name.
    
    Default location: center of India (23°N, 77°E) — tithi is location-
    independent for the same timezone, but sunrise-based panchang
    calculation can shift by ~1 day near boundaries.
    """
    
    # Hindu month → (index, approx_start_greg_month, approx_end_greg_month)
    # The "start" of a Hindu lunar month is Shukla Pratipada (day after Amavasya).
    # Approximate mapping using the amanta (ending with Amavasya) calendar.
    HINDU_MONTH_MAP: Dict[str, Tuple[int, int, int]] = {
        "Chaitra":     (1, 3, 4),     # Mar-Apr
        "Vaishakha":   (2, 4, 5),     # Apr-May
        "Jyeshtha":    (3, 5, 6),     # May-Jun
        "Ashadha":     (4, 6, 7),     # Jun-Jul
        "Shravana":    (5, 7, 8),     # Jul-Aug
        "Bhadrapada":  (6, 8, 9),     # Aug-Sep
        "Ashwin":      (7, 9, 10),    # Sep-Oct
        "Kartik":      (8, 10, 11),   # Oct-Nov
        "Margashirsha":(9, 11, 12),   # Nov-Dec
        "Pausha":      (10, 12, 1),   # Dec-Jan
        "Magha":       (11, 1, 2),    # Jan-Feb
        "Phalguna":    (12, 2, 3),    # Feb-Mar
    }
    
    # Index by month name for quick lookup
    MONTH_NAME_TO_INDEX = {v[0]: k for k, v in HINDU_MONTH_MAP.items()}
    
    # Sun rashi (solar month) to Hindu lunar month mapping (Amanta system).
    # The lunar month is named after the solar month in which its ending
    # Amavasya falls. A lunar month spans two solar months, so we allow
    # a tolerance of ±1 rashi when validating.
    RASHI_TO_HINDU_MONTH = {
        "Mesha":      "Chaitra",
        "Vrishabha":  "Vaishakha",
        "Mithuna":    "Jyeshtha",
        "Karka":      "Ashadha",
        "Simha":      "Shravana",
        "Kanya":      "Bhadrapada",
        "Tula":       "Ashwin",
        "Vrishchika": "Kartik",
        "Dhanu":      "Margashirsha",
        "Makara":     "Pausha",
        "Kumbha":     "Magha",
        "Meena":      "Phalguna",
    }
    
    # Reverse mapping: Hindu month → Sun rashi
    HINDU_MONTH_TO_RASHI = {v: k for k, v in RASHI_TO_HINDU_MONTH.items()}
    
    # All rashi names in order (for index-based tolerance check)
    RASHI_ORDER = [
        "Mesha", "Vrishabha", "Mithuna", "Karka",
        "Simha", "Kanya", "Tula", "Vrishchika",
        "Dhanu", "Makara", "Kumbha", "Meena"
    ]
    
    # For month validation: the two adjacent rashis that correspond to each month
    # (the month's own rashi and the previous rashi, since Shukla Paksha
    #  can fall in the previous solar month)
    @classmethod
    def get_valid_rashis_for_month(cls, hindu_month: str) -> List[str]:
        """
        Get the valid Sun rashis for a given Hindu month.
        Returns [prev_rashi, current_rashi] to handle month-spanning.
        """
        target_rashi = cls.HINDU_MONTH_TO_RASHI.get(hindu_month)
        if not target_rashi:
            return []
        
        target_idx = cls.RASHI_ORDER.index(target_rashi)
        # Previous rashi (wrapping around)
        prev_idx = (target_idx - 1) % 12
        prev_rashi = cls.RASHI_ORDER[prev_idx]
        
        return [prev_rashi, target_rashi]  # Return in chronological order
    
    # Tithi names for indexing (1-based)
    SHUKLA_TITHI_NAMES = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"
    ]
    
    KRISHNA_TITHI_NAMES = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
    ]
    
    def __init__(self, kaal_engine, lat: float = 23.0, lon: float = 77.0,
                 elevation: float = 0.0, ayanamsha: str = "LAHIRI",
                 timezone_offset: float = 5.5):
        """
        Initialize TithiScanner with a Kaal engine instance.
        
        Args:
            kaal_engine: Initialized Kaal() instance
            lat: Latitude (default: center of India)
            lon: Longitude (default: center of India)
            elevation: Elevation in meters
            ayanamsha: Ayanamsha system ("LAHIRI" or "RAMAN")
            timezone_offset: IST = UTC+5:30
        """
        self.kaal = kaal_engine
        self.lat = lat
        self.lon = lon
        self.elevation = elevation
        self.ayanamsha = ayanamsha
        self.timezone_offset = timezone_offset
    
    def find_tithi_date(self, year: int, hindu_month: str,
                        paksha: str, tithi_num: int,
                        search_padding_days: int = 30,
                        evening_start: bool = False) -> Optional[date]:
        """
        Find the Gregorian date when a specific tithi occurs.
        
        Uses the anchor-based approach:
        1. Find the month anchor (Shukla Pratipada for Shukla tithis,
           or the Amavasya that ends the month for Krishna tithis)
        2. Derive the target tithi date from the anchor
        3. Validate by checking actual tithi_name on the derived date
        
        This is more robust than direct tithi scanning because it avoids
        ambiguity between adjacent months' same-named tithis.
        
        Args:
            year: Gregorian year
            hindu_month: Hindu month name (e.g., "Kartik", "Magha")
            paksha: "shukla" or "krishna"
            tithi_num: 1-15 (15 = Purnima for shukla, Amavasya for krishna)
            search_padding_days: Days to search on each side of the mid-point
        
        Returns:
            date object of the tithi occurrence, or None if not found
        
        Example:
            # Diwali = Kartik Krishna Amavasya (tithi 15 of Krishna Paksha)
            diwali_date = scanner.find_tithi_date(2026, "Kartik", "krishna", 15)
        """
        # Validate inputs
        month_info = self.HINDU_MONTH_MAP.get(hindu_month)
        if not month_info:
            logger.error(f"Unknown Hindu month: {hindu_month}")
            return None
        
        if paksha not in ("shukla", "krishna"):
            logger.error(f"Invalid paksha: {paksha} (must be 'shukla' or 'krishna')")
            return None
        
        if tithi_num < 1 or tithi_num > 15:
            logger.error(f"Invalid tithi number: {tithi_num} (must be 1-15)")
            return None
        
        # ── Step 1: Find the month anchor ──────────────────────
        
        if paksha == "shukla":
            # Anchor = Shukla Pratipada (tithi 1) which marks month start.
            # Search for 'Shukla Pratipada' starting from the BEGINNING
            # of the month's Gregorian range to avoid catching the
            # previous month's Shukla 1.
            anchor_date = self._find_shukla_pratipada(
                year, hindu_month, month_info, search_padding_days
            )
            if anchor_date is None:
                return None
            # Derive target date: Shukla tithi N ≈ anchor + (N-1) days
            derived_date = anchor_date + timedelta(days=tithi_num - 1)
            
        else:  # krishna
            # Anchor = Amavasya (tithi 15 of Krishna Paksha) which ENDS the month.
            # Search for 'Krishna Amavasya' near the END of the month's range.
            anchor_date = self._find_krishna_amavasya(
                year, hindu_month, month_info, search_padding_days
            )
            if anchor_date is None:
                return None
            # Derive target date: Krishna tithi N ≈ anchor - (15 - N) days
            derived_date = anchor_date - timedelta(days=15 - tithi_num)
        
        # ── Step 2: Validate the derived date ───────────────────
        target_name = self._construct_tithi_name(paksha, tithi_num)
        
        # Check derived_date and ±3 days for boundary cases
        # Tithis vary in length (18-26h), so over 14 tithis the
        # cumulative error can be 2+ days from the simple derivation.
        for offset_days in (0, -1, 1, -2, 2, -3, 3):
            check_date = derived_date + timedelta(days=offset_days)
            check_dt = datetime(
                check_date.year, check_date.month, check_date.day,
                12, 0, 0
            )
            try:
                panchang = self.kaal.get_panchang(
                    self.lat, self.lon, check_dt,
                    elevation=self.elevation,
                    ayanamsha=self.ayanamsha,
                    timezone_offset=self.timezone_offset
                )
                if panchang.get('tithi_name') == target_name:
                    # Validate month using Sun's rashi
                    sun_rashi = panchang.get('rashi_of_sun')
                    valid_rashis = self.get_valid_rashis_for_month(hindu_month)
                    if sun_rashi in valid_rashis:
                        # Evening-start convention: Purnima (Shukla 15) and
                        # Amavasya (Krishna 15) often start after sunset, so
                        # DP assigns them to the PREVIOUS day.
                        if evening_start:
                            ev_date = check_date - timedelta(days=1)
                            try:
                                ev_dt = datetime(ev_date.year, ev_date.month, ev_date.day, 12, 0, 0)
                                ev_p = self.kaal.get_panchang(self.lat, self.lon, ev_dt, elevation=self.elevation, ayanamsha=self.ayanamsha, timezone_offset=self.timezone_offset)
                                ev_name = ev_p.get('tithi_name', '')
                                ev_rashi = ev_p.get('rashi_of_sun', '')
                                # Check if ev_date has the PRIOR tithi
                                ti = self._tithi_seq_index(target_name)
                                ev_idx = self._tithi_seq_index(ev_name)
                                if ti >= 0 and ev_idx >= 0 and ti == (ev_idx + 1) % 30:
                                    if ev_rashi in valid_rashis:
                                        logger.info(f"✓ '{target_name}' on {ev_date} "
                                                    f"(evening-start tithi 15)")
                                        return ev_date
                            except Exception:
                                pass
                        logger.info(
                            f"✓ Found '{target_name}' ({hindu_month} {year}) on {check_date}"
                        )
                        return check_date
                    else:
                        logger.debug(f"  tithi matched but month wrong on {check_date}: "
                                    f"Sun in {sun_rashi}, expected {valid_rashis}")
            except Exception:
                continue
        
        # Focused missed-tithi check: handle tithis that span sunrises
        today = derived_date
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        try:
            today_dt = datetime(today.year, today.month, today.day, 12, 0, 0)
            panchang = self.kaal.get_panchang(
                self.lat, self.lon, today_dt,
                elevation=self.elevation,
                ayanamsha=self.ayanamsha,
                timezone_offset=self.timezone_offset
            )
            next_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 0, 0)
            next_p = self.kaal.get_panchang(
                self.lat, self.lon, next_dt,
                elevation=self.elevation,
                ayanamsha=self.ayanamsha,
                timezone_offset=self.timezone_offset
            )
            curr_name = panchang.get('tithi_name', '')
            next_name = next_p.get('tithi_name', '')
            if self._is_missed_tithi(target_name, curr_name, next_name):
                sun_rashi = panchang.get('rashi_of_sun')
                valid_rashis = self.get_valid_rashis_for_month(hindu_month)
                if sun_rashi in valid_rashis:
                    logger.info(f"✓ Found '{target_name}' on {today} (missed tithi)")
                    return today
            # Check yesterday: handles 'evening-start' convention where a tithi
            # starts after sunset on day D and is active at sunrise on D+1.
            # DP assigns the festival to D (when the tithi STARTED).
            yest_dt = datetime(yesterday.year, yesterday.month, yesterday.day, 12, 0, 0)
            panchang2 = self.kaal.get_panchang(
                self.lat, self.lon, yest_dt,
                elevation=self.elevation,
                ayanamsha=self.ayanamsha,
                timezone_offset=self.timezone_offset
            )
            next2_dt = datetime(today.year, today.month, today.day, 12, 0, 0)
            next_p2 = self.kaal.get_panchang(
                self.lat, self.lon, next2_dt,
                elevation=self.elevation,
                ayanamsha=self.ayanamsha,
                timezone_offset=self.timezone_offset
            )
            curr2 = panchang2.get('tithi_name', '')
            next2_name = next_p2.get('tithi_name', '')
            if self._is_missed_tithi(target_name, curr2, next2_name):
                sun_rashi = panchang2.get('rashi_of_sun')
                valid_rashis = self.get_valid_rashis_for_month(hindu_month)
                if sun_rashi in valid_rashis:
                    logger.info(f"✓ Found '{target_name}' on {yesterday} (missed tithi)")
                    return yesterday
        except Exception:
            pass
        
        # Special case: Shukla Pratipada can be a kshaya tithi (skipped).
        # In this case, return the anchor date (day after Amavasya) anyway.
        if paksha == "shukla" and tithi_num == 1:
            logger.info(
                f"  Shukla Pratipada is kshaya, using anchor day {derived_date}"
            )
            return derived_date
        
        # Fallback: if derivation fails, do direct scan
        logger.info(f"Derived date {derived_date} didn't match '{target_name}', "
                    f"falling back to direct scan...")
        return self._direct_scan(year, hindu_month, paksha, tithi_num,
                                 month_info, search_padding_days)
    
    def _find_amavasya_anchor(self, search_center: date,
                                search_padding: int = 20) -> Optional[date]:
        """
        Find the nearest Amavasya before a reference date.
        
        Searches backward from search_center up to search_padding days.
        This Amavasya can anchor Shukla Paksha tithis (day after = Shukla 1).
        """
        current = search_center
        for _ in range(search_padding):
            dt = datetime(current.year, current.month, current.day, 12, 0, 0)
            try:
                panchang = self.kaal.get_panchang(
                    self.lat, self.lon, dt,
                    elevation=self.elevation,
                    ayanamsha=self.ayanamsha,
                    timezone_offset=self.timezone_offset
                )
                if panchang.get('tithi_name') == 'Krishna Amavasya':
                    return current
            except Exception:
                pass
            current -= timedelta(days=1)
        return None
    
    def _find_shukla_pratipada(self, year: int, hindu_month: str,
                                month_info: Tuple, search_padding_days: int) -> Optional[date]:
        """
        Find the start of Shukla Paksha for the target Hindu month.
        
        Finds the Amavasya that ENDS the PREVIOUS month. Day after = Shukla 1.
        Searches backward from end_greg_month with a wide window (55 days)
        to handle Adhika months and missed Amavasyas.
        Validates Sun rashi to skip Adhika month Amavasyas.
        """
        _, start_greg_month, end_greg_month = month_info
        
        # Search backward from the START of end_greg_month (e.g., Apr 1 for Chaitra)
        # with a 55-day window to handle Adhika months
        # For non-wrap months, reference is the end_greg_month of the target year.
        # For wrap months (start > end, e.g., Pausha: Dec-Jan, Margashirsha: Nov-Dec):
        # the month spans the year boundary. We search from BOTH:
        #   (A) end of year (year, 12) — catches Dec Purnimas
        #   (B) start of year (year, 1)  — catches Jan Purnimas
        # This handles all wrap-month cases regardless of which Gregorian year the
        # festival falls in.
        references = []
        if start_greg_month <= end_greg_month:
            # Non-wrap: simple case
            references.append(date(year, end_greg_month, 1))
        else:
            # Wrap: search both Dec of year and Jan of year
            references.append(date(year, 12, 1))   # Dec Purnima case
            references.append(date(year, 1, 1))     # Jan Purnima case
        
        valid_rashis = self.get_valid_rashis_for_month(hindu_month)
        
        best_amavasya = None
        best_festival_year = None
        for reference in references:
            for direction in (-1, 1):
                limit = 55 if direction == -1 else 30
                current = reference
                for _ in range(limit):
                    dt = datetime(current.year, current.month, current.day, 12, 0, 0)
                    try:
                        panchang = self.kaal.get_panchang(
                            self.lat, self.lon, dt,
                            elevation=self.elevation,
                            ayanamsha=self.ayanamsha,
                            timezone_offset=self.timezone_offset
                        )
                        tithi_name = panchang.get('tithi_name', '')
                        if tithi_name == 'Krishna Amavasya':
                            sun_rashi = panchang.get('rashi_of_sun')
                            if sun_rashi in valid_rashis:
                                month_start = current + timedelta(days=1)
                                # Compute when tithi 15 would fall (Purnima)
                                festival_date = month_start + timedelta(days=14)
                                fy = festival_date.year
                                if best_amavasya is None or (
                                    best_festival_year != year and fy == year
                                ):
                                    best_amavasya = month_start
                                    best_festival_year = fy
                                break
                            else:
                                logger.debug(f"  Skipping Adhika Amavasya {current}: "
                                            f"Sun in {sun_rashi}, expected {valid_rashis}")
                    except Exception:
                        pass
                    current += timedelta(days=direction)
        
        if best_amavasya:
            logger.info(
                f"  Shukla anchor Amavasya: {best_amavasya - timedelta(days=1)},"
                f" {hindu_month} Shukla 1 ~ {best_amavasya}"
            )
            return best_amavasya
        
        logger.warning(f"No Amavasya anchor found for {hindu_month} {year}")
        return None
        
        # Phase 2: Handle 'missed' Amavasya with rashi validation
        if last_chaturdashi_date:
            month_start = last_chaturdashi_date + timedelta(days=1)
            check_dt = datetime(
                month_start.year, month_start.month, month_start.day,
                12, 0, 0
            )
            try:
                panchang = self.kaal.get_panchang(
                    self.lat, self.lon, check_dt,
                    elevation=self.elevation,
                    ayanamsha=self.ayanamsha,
                    timezone_offset=self.timezone_offset
                )
                if panchang.get('tithi_name') == 'Shukla Pratipada':
                    sun_rashi = panchang.get('rashi_of_sun')
                    if sun_rashi in valid_rashis:
                        logger.info(
                            f"  Shukla anchor (missed Amavasya after "
                            f"{last_chaturdashi_date}, Sun in {sun_rashi}): "
                            f"{hindu_month} Shukla 1 ~ {month_start}"
                        )
                        return month_start
                    else:
                        logger.debug(f"  Skipping missed-Adhika Amavasya: "
                                    f"Sun in {sun_rashi}, expected {valid_rashis}")
            except Exception:
                pass
        
        logger.warning(f"No Amavasya anchor found for {hindu_month} {year}")
        return None
    
    def _find_krishna_amavasya(self, year: int, hindu_month: str,
                                month_info: Tuple, search_padding_days: int) -> Optional[date]:
        """
        Find Krishna Amavasya (month end) for the target Hindu month.
        
        Searches from the MIDDLE of the START month to well past the END month
        to handle early Amavasyas (e.g., Kartik Amavasya falling in late October).
        """
        _, start_greg_month, end_greg_month = month_info
        
        # Search from the middle of the START month, well into the next month
        # This catches Amavasyas that fall early (e.g., Kartik Amavasya in Oct)
        if start_greg_month <= end_greg_month:
            # E.g., Kartik (Oct-Nov): search from Oct 15 to Dec 10
            search_start = date(year, start_greg_month, 15)
            search_end = date(year, end_greg_month, 1) + timedelta(days=60)
        else:
            # Wrap case: e.g., Pausha (Dec-Jan): search from Dec 15 to Feb 10
            search_start = date(year, start_greg_month, 15)
            search_end = date(year + 1, end_greg_month, 1) + timedelta(days=60)
        
        logger.info(
            f"  Krishna anchor: searching for 1st Amavasya "
            f"between {search_start} and {search_end}"
        )
        
        # Find the FIRST Amavasya in the window
        current = search_start
        while current <= search_end:
            dt = datetime(current.year, current.month, current.day, 12, 0, 0)
            try:
                panchang = self.kaal.get_panchang(
                    self.lat, self.lon, dt,
                    elevation=self.elevation,
                    ayanamsha=self.ayanamsha,
                    timezone_offset=self.timezone_offset
                )
                if panchang.get('tithi_name') == 'Krishna Amavasya':
                    # Validate by Sun rashi: for the Amavasya that ENDS the
                    # target month, Sun should be in the month's OWN rashi
                    # or the NEXT month's rashi (never the previous month's).
                    rashi = panchang.get('rashi_of_sun', '')
                    target_rashi = self.HINDU_MONTH_TO_RASHI.get(hindu_month, '')
                    next_rashi = ''
                    if target_rashi and target_rashi in self.RASHI_ORDER:
                        idx = self.RASHI_ORDER.index(target_rashi)
                        next_rashi = self.RASHI_ORDER[(idx + 1) % 12]
                    if rashi in (target_rashi, next_rashi):
                        logger.info(f"  {hindu_month} Krishna Amavasya: {current} (Sun={rashi})")
                        return current
                    else:
                        logger.debug(f"  Skipping Amavasya {current}: Sun={rashi}, "
                                    f"expected {target_rashi} or {next_rashi} for {hindu_month}")
            except Exception:
                pass
            current += timedelta(days=1)
        
        logger.warning(f"Krishna Amavasya not found for {hindu_month} {year}")
        return None
    
    def _direct_scan(self, year: int, hindu_month: str,
                      paksha: str, tithi_num: int,
                      month_info: Tuple, search_padding_days: int) -> Optional[date]:
        """Fallback: direct day-by-day scan (same as original approach)."""
        _, start_greg_month, end_greg_month = month_info
        
        if paksha == "shukla":
            search_center_month = start_greg_month
            search_center_day = 12
            search_year = year
        else:
            if start_greg_month <= end_greg_month:
                search_center_month = end_greg_month
                search_center_day = 18
                search_year = year
            else:
                search_center_month = end_greg_month
                search_center_day = 18
                search_year = year + 1
        
        try:
            center_date = datetime(search_year, search_center_month, search_center_day, 12, 0, 0)
        except ValueError:
            center_date = datetime(search_year, search_center_month, 15, 12, 0, 0)
        
        start_search = center_date - timedelta(days=search_padding_days)
        end_search = center_date + timedelta(days=search_padding_days)
        
        target_name = self._construct_tithi_name(paksha, tithi_num)
        
        current = start_search
        while current <= end_search:
            try:
                panchang = self.kaal.get_panchang(
                    self.lat, self.lon, current,
                    elevation=self.elevation,
                    ayanamsha=self.ayanamsha,
                    timezone_offset=self.timezone_offset
                )
                if panchang.get('tithi_name') == target_name:
                    # Validate month using Sun's rashi to avoid
                    # picking a matching tithi from the wrong month
                    sun_rashi = panchang.get('rashi_of_sun')
                    valid_rashis = self.get_valid_rashis_for_month(hindu_month)
                    if sun_rashi in valid_rashis:
                        logger.info(f"✓ Found '{target_name}' on {current.date()} (direct scan)")
                        return current.date()
                    else:
                        logger.debug(f"  tithi matched but month wrong: "
                                    f"Sun in {sun_rashi}, expected {valid_rashis}")
            except Exception as e:
                logger.debug(f"Error at {current.date()}: {e}")
            current += timedelta(days=1)
        
        return None
    
    def find_all_ekadashis(self, year: int) -> List[Tuple[str, str, date]]:
        """
        Find all 24 Ekadashis in a Gregorian year.
        
        Returns:
            List of (hindu_month, paksha, date) tuples sorted by date.
            E.g., [("Chaitra", "krishna", date(2026, 3, 14)), ...]
        """
        ekadashis = []
        
        for month_name in self.HINDU_MONTH_MAP:
            for paksha in ("krishna", "shukla"):
                ekadashi_date = self.find_tithi_date(year, month_name, paksha, 11)
                if ekadashi_date:
                    ekadashis.append((month_name, paksha, ekadashi_date))
        
        # Sort by date
        ekadashis.sort(key=lambda x: x[2])
        return ekadashis
    
    def find_all_amavasyas(self, year: int) -> List[Tuple[str, date]]:
        """
        Find all 12-13 Amavasyas (Krishna Amavasya = tithi 15 of Krishna Paksha).
        
        Returns:
            List of (hindu_month, date) tuples sorted by date
        """
        amavasyas = []
        for month_name in self.HINDU_MONTH_MAP:
            amavasya_date = self.find_tithi_date(year, month_name, "krishna", 15)
            if amavasya_date:
                amavasyas.append((month_name, amavasya_date))
        
        amavasyas.sort(key=lambda x: x[1])
        return amavasyas
    
    def find_all_purnimas(self, year: int) -> List[Tuple[str, date]]:
        """
        Find all 12-13 Purnimas (Shukla Purnima = tithi 15 of Shukla Paksha).
        
        Returns:
            List of (hindu_month, date) tuples sorted by date
        """
        purnimas = []
        for month_name in self.HINDU_MONTH_MAP:
            purnima_date = self.find_tithi_date(year, month_name, "shukla", 15)
            if purnima_date:
                purnimas.append((month_name, purnima_date))
        
        purnimas.sort(key=lambda x: x[1])
        return purnimas
    
    def _construct_tithi_name(self, paksha: str, tithi_num: int) -> str:
        """
        Construct the tithi_name string that get_panchang() returns,
        so we can match against it.
        
        Matches the naming convention in kaal._get_tithi_name():
        - Shukla 1-14 → "Shukla {name}" (Pratipada through Chaturdashi)
        - Shukla 15   → "Shukla Purnima"
        - Krishna 1-14 → "Krishna {name}" (Pratipada through Chaturdashi)
        - Krishna 15   → "Krishna Amavasya"
        """
        if paksha == "shukla":
            if tithi_num == 15:
                return "Shukla Purnima"
            return f"Shukla {self.SHUKLA_TITHI_NAMES[tithi_num - 1]}"
        else:  # krishna
            if tithi_num == 15:
                return "Krishna Amavasya"
            return f"Krishna {self.KRISHNA_TITHI_NAMES[tithi_num - 1]}"
    
    # Ordered tithi sequence (30 tithis, starting from Shukla Pratipada)
    TITHI_SEQUENCE = [
        "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya",
        "Shukla Chaturthi", "Shukla Panchami", "Shukla Shashthi",
        "Shukla Saptami", "Shukla Ashtami", "Shukla Navami",
        "Shukla Dashami", "Shukla Ekadashi", "Shukla Dwadashi",
        "Shukla Trayodashi", "Shukla Chaturdashi", "Shukla Purnima",
        "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya",
        "Krishna Chaturthi", "Krishna Panchami", "Krishna Shashthi",
        "Krishna Saptami", "Krishna Ashtami", "Krishna Navami",
        "Krishna Dashami", "Krishna Ekadashi", "Krishna Dwadashi",
        "Krishna Trayodashi", "Krishna Chaturdashi", "Krishna Amavasya",
    ]
    
    def _tithi_seq_index(self, name: str) -> int:
        """Get index in 30-tithi sequence. Shukla Pratipada=0, ..., Krishna Amavasya=29."""
        try:
            return self.TITHI_SEQUENCE.index(name)
        except ValueError:
            return -1
    
    def _next_tithi(self, name: str) -> Optional[str]:
        """Get the next tithi name in the 30-cycle."""
        idx = self._tithi_seq_index(name)
        if idx < 0:
            return None
        return self.TITHI_SEQUENCE[(idx + 1) % 30]
    
    def _is_missed_tithi(self, target: str, current: str, next_day: str) -> bool:
        """Check if target tithi started between current sunrise and next sunrise.
        
        Handles two cases:
        1. 'Missed' tithi: target starts after sunrise D and ends before sunrise D+1.
           Detection: current → target → next_day (consecutive in 30-cycle).
        2. 'Evening-start' tithi: target starts after sunset (but before midnight)
           and is active at next sunrise. Detection: currently next_day==target,
           and current is the tithi BEFORE target in the cycle.
        """
        curr_idx = self._tithi_seq_index(current)
        tgt_idx = self._tithi_seq_index(target)
        nxt_idx = self._tithi_seq_index(next_day)
        
        if curr_idx < 0 or tgt_idx < 0 or nxt_idx < 0:
            return False
        
        # Case 1: consecutive sequence curr → target → next
        if tgt_idx == (curr_idx + 1) % 30 and nxt_idx == (curr_idx + 2) % 30:
            return True
        
        # Case 2: target IS next (active at next sunrise), and current is prev
        if tgt_idx == nxt_idx and curr_idx == (tgt_idx - 1) % 30:
            return True
        
        return False
    
    def get_approximate_gregorian_range(self, hindu_month: str, year: int) -> Tuple[date, date]:
        """
        Get the approximate Gregorian date range for a Hindu month.
        
        Returns (start_date, end_date) in Gregorian calendar.
        """
        month_info = self.HINDU_MONTH_MAP.get(hindu_month)
        if not month_info:
            return (date(year, 1, 1), date(year, 12, 31))
        
        _, start_m, end_m = month_info
        
        if start_m <= end_m:
            start_date = date(year, start_m, 1)
            end_date = date(year, end_m, 28)  # Safe end
        else:
            start_date = date(year, start_m, 1)
            end_date = date(year + 1, end_m, 28)
        
        return (start_date, end_date)
    
    def find_next_amavasya(self, from_date: date, direction: int = 1) -> Optional[date]:
        """
        Find the next (or previous) Amavasya from a reference date.
        
        Args:
            from_date: Starting date
            direction: 1 for forward, -1 for backward
        
        Returns:
            date of the nearest Amavasya in the given direction
        """
        # Scan up to 40 days in the given direction
        for offset in range(1, 41):
            check_date = from_date + timedelta(days=offset * direction)
            check_dt = datetime(check_date.year, check_date.month, check_date.day, 12, 0, 0)
            
            try:
                panchang = self.kaal.get_panchang(
                    self.lat, self.lon, check_dt,
                    elevation=self.elevation,
                    ayanamsha=self.ayanamsha,
                    timezone_offset=self.timezone_offset
                )
                
                if panchang.get('tithi_name') == 'Krishna Amavasya':
                    return check_date
            except Exception:
                continue
        
        return None
    
    def find_lunar_month_boundaries(self, year: int) -> Dict[str, Tuple[date, date]]:
        """
        Map all Hindu lunar months for a Gregorian year.
        
        A Hindu lunar month runs from Shukla Pratipada (day after Amavasya)
        to the next Amavasya.
        
        Returns:
            Dict of {hindu_month_name: (start_date, end_date)}
            where start_date is Shukla Pratipada and end_date is Amavasya.
        """
        # Find all Amavasyas in this year (and one extra)
        boundaries = {}
        
        # Scan extended range to catch Amavasyas near year boundaries
        all_amavasyas = []
        for month_name in self.HINDU_MONTH_MAP:
            amavasya = self.find_tithi_date(year, month_name, "krishna", 15)
            if amavasya:
                all_amavasyas.append((month_name, amavasya))
        
        # Also check previous year's last months and next year's first months
        for month_name in ["Margashirsha", "Pausha", "Magha", "Phalguna"]:
            amavasya = self.find_tithi_date(year - 1, month_name, "krishna", 15)
            if amavasya:
                all_amavasyas.append((month_name, amavasya))
        
        for month_name in ["Chaitra", "Vaishakha"]:
            amavasya = self.find_tithi_date(year + 1, month_name, "krishna", 15)
            if amavasya:
                all_amavasyas.append((month_name, amavasya))
        
        all_amavasyas.sort(key=lambda x: x[1])
        
        # Build month boundaries
        # Hindu month N starts at Shukla Pratipada = day after Amavasya of month N-1
        # Hindu month N ends at Amavasya of month N
        for i, (month_name, amavasya_date) in enumerate(all_amavasyas):
            # Find the Amavasya for the previous month
            prev_amavasya_date = None
            if i > 0:
                prev_amavasya_date = all_amavasyas[i - 1][1]
            else:
                # Search backward
                prev_amavasya_date = self.find_next_amavasya(amavasya_date, direction=-1)
            
            if prev_amavasya_date:
                # Month starts day after previous Amavasya
                month_start = prev_amavasya_date + timedelta(days=1)
                month_end = amavasya_date
                
                boundaries[month_name] = (month_start, month_end)
        
        return boundaries


# ─── Convenience Functions for FestivalEngine Integration ──────────────

def scan_festival(scanner: TithiScanner, rule, year: int) -> Optional[date]:
    """
    Compute a single festival date from a FestivalRule.
    
    This is the bridge between FestivalEngine's FestivalRule objects
    and the TithiScanner's tithi-finding capability.
    
    Args:
        scanner: Initialized TithiScanner
        rule: A FestivalRule instance (from festivals.py)
        year: Gregorian year
    
    Returns:
        date or None if calculation fails
    """
    from .festivals import FestivalType  # noqa
    
    festival_type = rule.festival_type.value if hasattr(rule.festival_type, 'value') else str(rule.festival_type)
    
    if festival_type in ("lunar", "LUNAR"):
        if rule.month and rule.tithi is not None:
            paksha = rule.paksha or "shukla"
            evening_start = getattr(rule, 'evening_start', False)
            return scanner.find_tithi_date(year, rule.month, paksha, rule.tithi,
                                           evening_start=evening_start)
    
    elif festival_type in ("solar", "SOLAR"):
        # Solar festivals: find the date of Sun's ingress into a specific rashi
        if rule.month:
            # Map Hindu month to its corresponding Sun rashi
            target_rashi = scanner.HINDU_MONTH_TO_RASHI.get(rule.month)
            if target_rashi:
                from kaal_engine.kaal import Kaal
                # Use the kaal engine to find when Sun enters the target rashi
                try:
                    sankranti_date = scanner.kaal.find_sankranti_date(
                        scanner.lat, scanner.lon, target_rashi, year,
                        elevation=scanner.elevation,
                        ayanamsha=scanner.ayanamsha,
                        timezone_offset=scanner.timezone_offset
                    )
                    return sankranti_date
                except (AttributeError, Exception):
                    # Fallback: scan for the date using rashi info from panchang
                    return _scan_solar_festival(scanner, rule, year)
    
    elif festival_type in ("nakshatra", "NAKSHATRA"):
        # Nakshatra festivals: find the date when a specific nakshatra occurs
        # at sunrise (or the tithi+nakshatra combination)
        if rule.month and rule.tithi is not None and hasattr(rule, 'nakshatra') and rule.nakshatra:
            return _scan_nakshatra_festival(scanner, rule, year)
    
    elif festival_type in ("calculated", "CALCULATED"):
        # Calculated festivals (e.g., Ekadashi, eclipses) - handled separately
        if rule.tithi is not None:
            # Try as a lunar tithi first
            if rule.month and rule.paksha:
                return scanner.find_tithi_date(year, rule.month, rule.paksha, rule.tithi)
    
    return None


def _scan_solar_festival(scanner: TithiScanner, rule, year: int) -> Optional[date]:
    """Find the date when Sun enters the rashi corresponding to rule.month."""
    target_rashi = scanner.HINDU_MONTH_TO_RASHI.get(rule.month)
    if not target_rashi:
        return None
    
    rashi_idx = scanner.RASHI_ORDER.index(target_rashi)
    
    # Scan the expected Gregorian range for the month
    month_info = scanner.HINDU_MONTH_MAP.get(rule.month)
    if not month_info:
        return None
    _, start_m, end_m = month_info
    
    if start_m <= end_m:
        search_start = date(year, start_m, 1)
        search_end = date(year, end_m, 28)
    else:
        search_start = date(year, start_m, 1)
        search_end = date(year + 1, end_m, 28)
    
    # Scan day by day looking for the first day where Sun has entered target rashi
    current = search_start
    found_first = None
    while current <= search_end:
        dt = datetime(current.year, current.month, current.day, 12, 0, 0)
        try:
            panchang = scanner.kaal.get_panchang(
                scanner.lat, scanner.lon, dt,
                elevation=scanner.elevation,
                ayanamsha=scanner.ayanamsha,
                timezone_offset=scanner.timezone_offset
            )
            sun_rashi = panchang.get('rashi_of_sun', '')
            if sun_rashi == target_rashi:
                if found_first is None:
                    found_first = current
            elif found_first is not None:
                # Sun just left the rashi — the date of ingress was the first day
                return found_first
        except Exception:
            pass
        current += timedelta(days=1)
    
    # If we never left the rashi, the ingress was at the start of our range
    return found_first


def _scan_nakshatra_festival(scanner: TithiScanner, rule, year: int) -> Optional[date]:
    """Find the date when a specific nakshatra occurs at sunrise."""
    target_nakshatra = rule.nakshatra
    if not target_nakshatra:
        return None
    
    # Get the Gregorian range for the month
    month_info = scanner.HINDU_MONTH_MAP.get(rule.month)
    if not month_info:
        return None
    _, start_m, end_m = month_info
    
    if start_m <= end_m:
        search_start = date(year, start_m, 1)
        search_end = date(year, end_m, 28)
    else:
        search_start = date(year, start_m, 1)
        search_end = date(year + 1, end_m, 28)
    
    # Scan day by day looking for the target nakshatra at sunrise
    current = search_start
    while current <= search_end:
        dt = datetime(current.year, current.month, current.day, 12, 0, 0)
        try:
            panchang = scanner.kaal.get_panchang(
                scanner.lat, scanner.lon, dt,
                elevation=scanner.elevation,
                ayanamsha=scanner.ayanamsha,
                timezone_offset=scanner.timezone_offset
            )
            nakshatra = panchang.get('nakshatra', '')
            tithi_name = panchang.get('tithi_name', '')
            
            # Match by nakshatra (and optionally tithi)
            if nakshatra == target_nakshatra:
                if rule.tithi is not None:
                    # Also check the tithi matches
                    expected_tithi = scanner._construct_tithi_name(
                        rule.paksha or "shukla", rule.tithi
                    )
                    if tithi_name == expected_tithi:
                        return current
                else:
                    return current
        except Exception:
            pass
        current += timedelta(days=1)
    
    return None


def batch_scan_festivals(scanner: TithiScanner, rules: list, year: int) -> List[Tuple]:
    """
    Compute dates for a batch of festival rules.
    
    Args:
        scanner: Initialized TithiScanner
        rules: List of FestivalRule objects
        year: Gregorian year
    
    Returns:
        List of (rule, date_or_None) tuples
    """
    results = []
    for rule in rules:
        festival_date = scan_festival(scanner, rule, year)
        results.append((rule, festival_date))
    return results
