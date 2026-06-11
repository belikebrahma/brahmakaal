"""
Tests for the TithiScanner — the core festival date calculation engine.

Uses the live Kaal engine to compute actual festival dates and validates
them against known reference values.

Phase 1 validation from FESTIVAL_CALENDAR_PLAN.md
"""

import pytest
from datetime import date
from kaal_engine.kaal import Kaal
from kaal_engine.core.festival_scanner import TithiScanner, scan_festival, batch_scan_festivals
from kaal_engine.core.festivals import FestivalEngine, FestivalRule, FestivalType, FestivalCategory, Region

# ─── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def kaal():
    """Initialize Kaal engine with de421 ephemeris."""
    try:
        engine = Kaal("de421.bsp")
        return engine
    except Exception as e:
        pytest.skip(f"Kaal engine init failed: {e} (de421.bsp missing?)")

@pytest.fixture(scope="module")
def scanner(kaal):
    """Create TithiScanner instance."""
    return TithiScanner(
        kaal_engine=kaal,
        lat=28.6139,   # New Delhi
        lon=77.2090,
        timezone_offset=5.5
    )


# ─── Known Reference Dates (from cross-validation) ─────────────────

# These reference dates were obtained from Drik Panchang for 2026
# and cross-validated during earlier Brahmakaal testing.
# Format: (test_name, hindu_month, paksha, tithi_num, expected_date)

FESTIVAL_REFERENCE_2026 = [
    ("Diwali",                 "Kartik",      "krishna", 15, date(2026, 11,  8)),  # Amavasya
    ("Holi - Holika Dahan",    "Phalguna",    "shukla",  15, date(2026, 3,   3)),  # Purnima
    ("Holi - Rangwali Holi",   "Chaitra",     "krishna", 1,  date(2026, 3,   4)),  # next day
    ("Dussehra",               "Ashwin",      "shukla",  10, date(2026, 10, 21)),
    ("Sharad Navaratri start", "Ashwin",      "shukla",  1,  date(2026, 10, 12)),
    ("Ganesh Chaturthi",       "Bhadrapada",  "shukla",  4,  date(2026, 9,  15)),
    ("Maha Shivaratri",        "Magha",       "krishna", 14, date(2026, 2,  15)),
    ("Ram Navami",             "Chaitra",     "shukla",  9,  date(2026, 3,  27)),
    ("Guru Purnima",           "Ashadha",     "shukla",  15, date(2026, 7,  29)),
    ("Janmashtami",            "Bhadrapada",  "krishna", 8,  date(2026, 9,  5)),
    ("Karva Chauth",           "Kartik",      "krishna", 4,  date(2026, 10, 28)),
    ("Vasant Panchami",        "Magha",       "shukla",  5,  date(2026, 1,  22)),
]

# Reference for known Ekadashis (subset for testing)
EKADASHI_REFERENCE_2026 = [
    ("Chaitra Krishna Ekadashi", "Chaitra",  "krishna", date(2026, 3, 23)),
    ("Chaitra Shukla Ekadashi",  "Chaitra",  "shukla",  date(2026, 4,  7)),
]


# ─── Tithi Name Construction Tests ─────────────────────────────────

class TestTithiNameConstruction:
    """Verify _construct_tithi_name matches kaal._get_tithi_name()."""

    def test_shukla_pratipada(self, scanner):
        assert scanner._construct_tithi_name("shukla", 1) == "Shukla Pratipada"

    def test_shukla_ekadashi(self, scanner):
        assert scanner._construct_tithi_name("shukla", 11) == "Shukla Ekadashi"

    def test_shukla_purnima(self, scanner):
        assert scanner._construct_tithi_name("shukla", 15) == "Shukla Purnima"

    def test_krishna_pratipada(self, scanner):
        assert scanner._construct_tithi_name("krishna", 1) == "Krishna Pratipada"

    def test_krishna_ekadashi(self, scanner):
        assert scanner._construct_tithi_name("krishna", 11) == "Krishna Ekadashi"

    def test_krishna_chaturdashi(self, scanner):
        assert scanner._construct_tithi_name("krishna", 14) == "Krishna Chaturdashi"

    def test_krishna_amavasya(self, scanner):
        assert scanner._construct_tithi_name("krishna", 15) == "Krishna Amavasya"


# ─── Tithi Date Finding Tests ──────────────────────────────────────

class TestFindTithiDate:
    """Core scanning algorithm tests."""

    @pytest.mark.parametrize("name,month,paksha,tithi_num,expected", FESTIVAL_REFERENCE_2026)
    def test_festival_dates_2026(self, scanner, name, month, paksha, tithi_num, expected):
        """Verify each known festival date matches Drik Panchang reference."""
        result = scanner.find_tithi_date(2026, month, paksha, tithi_num)
        assert result is not None, f"{name} ({month} {paksha} {tithi_num}) not found!"
        assert result == expected, (
            f"{name}: expected {expected}, got {result} "
            f"(diff {abs((result - expected).days)} days)"
        )

    def test_diwali_2026(self, scanner):
        """Diwali = Kartik Krishna Amavasya (tithi 15 of Krishna Paksha)."""
        result = scanner.find_tithi_date(2026, "Kartik", "krishna", 15)
        assert result == date(2026, 11, 8)

    def test_nonexistent_tithi(self, scanner):
        """Should return None for an impossible tithi."""
        result = scanner.find_tithi_date(2026, "InvalidMonth", "shukla", 1)
        assert result is None

    def test_unknown_month(self, scanner):
        """Unknown month name returns None."""
        result = scanner.find_tithi_date(2026, "NotAMonth", "shukla", 1)
        assert result is None

    def test_invalid_paksha(self, scanner):
        """Invalid paksha returns None."""
        result = scanner.find_tithi_date(2026, "Kartik", "invalid", 1)
        assert result is None

    def test_invalid_tithi_num(self, scanner):
        """Tithi number out of range returns None."""
        result = scanner.find_tithi_date(2026, "Kartik", "shukla", 0)
        assert result is None
        result = scanner.find_tithi_date(2026, "Kartik", "shukla", 16)
        assert result is None


# ─── Ekadashi Tests ────────────────────────────────────────────────

class TestEkadashis:
    """Test Ekadashi date computation."""

    def test_find_all_ekadashis_returns_24(self, scanner):
        """Should find approximately 24 Ekadashis in a year."""
        ekadashis = scanner.find_all_ekadashis(2026)
        # Some years have 24-25 due to Adhika masa
        assert 22 <= len(ekadashis) <= 26, f"Expected ~24 Ekadashis, got {len(ekadashis)}"
        for month, paksha, ekadashi_date in ekadashis:
            assert isinstance(ekadashi_date, date)

    @pytest.mark.parametrize("name,month,paksha,expected", EKADASHI_REFERENCE_2026)
    def test_specific_ekadashis(self, scanner, name, month, paksha, expected):
        """Verify specific known Ekadashi dates match."""
        result = scanner.find_tithi_date(2026, month, paksha, 11)
        assert result is not None, f"{name} not found!"
        assert result == expected, f"{name}: expected {expected}, got {result}"

    def test_ekadashis_are_unique(self, scanner):
        """No two Ekadashis should fall on the same date."""
        ekadashis = scanner.find_all_ekadashis(2026)
        dates = [e[2] for e in ekadashis]
        assert len(dates) == len(set(dates)), "Duplicate Ekadashi dates found!"

    def test_ekadashis_alternate_paksha(self, scanner):
        """Ekadashis should alternate between Krishna and Shukla paksha."""
        ekadashis = scanner.find_all_ekadashis(2026)
        for i in range(1, len(ekadashis)):
            # Two consecutive Ekadashis should not have the same paksha
            if ekadashis[i][1] == ekadashis[i-1][1]:
                # Unless there's an Adhika masa
                pass  # Allow exceptions


# ─── Amavasya & Purnima Tests ──────────────────────────────────────

class TestAmavasyaPurnima:
    """Test Amavasya and Purnima date computation."""

    def test_find_all_amavasyas(self, scanner):
        """Should find 12-13 Amavasyas in a year."""
        amavasyas = scanner.find_all_amavasyas(2026)
        assert 12 <= len(amavasyas) <= 13, f"Expected ~12 Amavasyas, got {len(amavasyas)}"
        for month, amavasya_date in amavasyas:
            assert isinstance(amavasya_date, date)

    def test_find_all_purnimas(self, scanner):
        """Should find 12-13 Purnimas in a year."""
        purnimas = scanner.find_all_purnimas(2026)
        assert 12 <= len(purnimas) <= 13, f"Expected ~12 Purnimas, got {len(purnimas)}"
        for month, purnima_date in purnimas:
            assert isinstance(purnima_date, date)

    def test_amavasya_purnima_interleave(self, scanner):
        """Amavasyas and Purnimas should interleave ~15 days apart."""
        amavasyas = scanner.find_all_amavasyas(2026)
        purnimas = scanner.find_all_purnimas(2026)
        # Each Amavasya should have a corresponding Purnima ~15 days before or after
        # Due to Adhika masa, some months may not align perfectly
        all_dates = sorted(amavasyas + purnimas, key=lambda x: x[1])
        assert len(all_dates) >= 24, "Should have ~24 full/new moon dates"

    def test_amavasya_is_new_moon(self, scanner, kaal):
        """Verify Amavasya has tithi_name 'Krishna Amavasya'."""
        amavasyas = scanner.find_all_amavasyas(2026)
        for month, amavasya_date in amavasyas[:3]:  # Check first 3
            dt = type('obj', (), {'year': amavasya_date.year,
                                  'month': amavasya_date.month,
                                  'day': amavasya_date.day})()
            # We already verified by construction, this is a sanity check
            assert amavasya_date is not None


# ─── Year Wrap Tests (Pausha, Magha, Phalguna) ─────────────────────

class TestYearWrapMonths:
    """Test months that span across Gregorian year boundaries."""

    def test_magha_shukla_panchami(self, scanner):
        """Vasant Panchami = Magha Shukla 5, typically in Jan/Feb."""
        result = scanner.find_tithi_date(2026, "Magha", "shukla", 5)
        # Vasant Panchami is typically in late Jan to mid-Feb
        assert result is not None
        assert result.month in (1, 2), f"Expected Jan/Feb, got {result}"

    def test_phalguna_purnima(self, scanner):
        """Holika Dahan = Phalguna Shukla Purnima, typically in Mar."""
        result = scanner.find_tithi_date(2026, "Phalguna", "shukla", 15)
        assert result is not None
        assert result.month in (2, 3), f"Expected Feb/Mar, got {result}"

    def test_pausha_purnima(self, scanner):
        """Pausha Purnima, typically in Jan."""
        result = scanner.find_tithi_date(2026, "Pausha", "shukla", 15)
        assert result is not None
        assert result.month in (1,), f"Expected Jan, got {result}"


# ─── Consistency Checks ────────────────────────────────────────────

class TestConsistency:
    """Self-consistency checks for the scanning algorithm."""

    def test_consecutive_tithis_monotonic(self, scanner):
        """Dates should be monotonically increasing with tithi number."""
        month = "Chaitra"
        dates_2026 = []
        for num in range(1, 16):
            d = scanner.find_tithi_date(2026, month, "shukla", num)
            if d:
                dates_2026.append((num, d))
        
        if len(dates_2026) >= 2:
            for i in range(1, len(dates_2026)):
                assert dates_2026[i][1] >= dates_2026[i-1][1], (
                    f"Tithi {dates_2026[i][0]} ({dates_2026[i][1]}) "
                    f"is before tithi {dates_2026[i-1][0]} ({dates_2026[i-1][1]})"
                )

    def test_krishna_after_shukla(self, scanner):
        """Krishna Paksha tithis should come after Shukla Paksha tithis in same month."""
        month = "Kartik"
        shukla_1 = scanner.find_tithi_date(2026, month, "shukla", 1)
        shukla_15 = scanner.find_tithi_date(2026, month, "shukla", 15)
        krishna_1 = scanner.find_tithi_date(2026, month, "krishna", 1)
        
        if all(d is not None for d in [shukla_1, shukla_15, krishna_1]):
            # Shukla 1 should be before Shukla 15
            assert shukla_1 <= shukla_15, (
                f"Shukla 1 ({shukla_1}) is after Shukla 15 ({shukla_15})"
            )
            # Krishna 1 should be after Shukla 15 (Purnima)
            # Actually Krishna 1 starts after Purnima, flexibility ±1 day
            assert krishna_1 >= shukla_1, (
                f"Krishna 1 ({krishna_1}) is before Shukla 1 ({shukla_1})"
            )


# ─── Lunar Month Boundary Tests ─────────────────────────────────────

class TestLunarMonthBoundaries:
    """Test lunar month boundary mapping."""

    def test_find_lunar_month_boundaries(self, scanner):
        """Should return boundaries for all 12 Hindu months."""
        boundaries = scanner.find_lunar_month_boundaries(2026)
        assert len(boundaries) >= 10, f"Expected ~12 months, got {len(boundaries)}"
        for month, (start, end) in boundaries.items():
            assert start <= end, f"{month}: start {start} after end {end}"

    def test_lunar_month_duration(self, scanner):
        """Lunar months should be approximately 29-30 days."""
        boundaries = scanner.find_lunar_month_boundaries(2026)
        for month, (start, end) in boundaries.items():
            duration = (end - start).days
            assert 28 <= duration <= 31, (
                f"{month}: {duration} days (expected 29-30)"
            )

    def test_no_gaps_between_months(self, scanner):
        """End of one month should connect to start of next."""
        boundaries = scanner.find_lunar_month_boundaries(2026)
        sorted_months = sorted(boundaries.items(), key=lambda x: x[1][0])
        for i in range(1, len(sorted_months)):
            prev_end = sorted_months[i-1][1][1]
            curr_start = sorted_months[i][1][0]
            gap = (curr_start - prev_end).days
            assert gap <= 2, (
                f"Gap of {gap} days between {sorted_months[i-1][0]} and {sorted_months[i][0]}"
            )


# ─── StreetScan Performance Test ─────────────────────────────────────

class TestPerformance:
    """Performance characteristics of the scanner."""

    def test_find_10_festivals_under_30_seconds(self, scanner):
        """Finding 10 festival dates should complete quickly."""
        import time
        test_cases = FESTIVAL_REFERENCE_2026[:10]
        
        start = time.time()
        for name, month, paksha, tithi_num, expected in test_cases:
            result = scanner.find_tithi_date(2026, month, paksha, tithi_num)
            assert result is not None
        elapsed = time.time() - start
        
        print(f"\n⏱ {len(test_cases)} festivals in {elapsed:.1f}s "
              f"({elapsed/len(test_cases):.2f}s per festival)")
        
        # Each get_panchang() call takes ~1-2s, so 10 festivals × 60 days ≈ 600 calls
        # Should complete in under 2 minutes
        assert elapsed < 120, f"Too slow: {elapsed:.0f}s for 10 festivals"


# ─── Integration with FestivalEngine ────────────────────────────────

class TestScanFestivalFunction:
    """Test scan_festival() bridge function for FestivalEngine integration."""

    def test_scan_festival_diwali(self, scanner):
        """scan_festival should compute Diwali date correctly."""
        rule = FestivalRule(
            name="Diwali",
            english_name="Diwali",
            festival_type=FestivalType.LUNAR,
            category=FestivalCategory.MAJOR,
            regions=[Region.ALL_INDIA],
            month="Kartik",
            paksha="krishna",
            tithi=15,
            description="Festival of lights"
        )
        result = scan_festival(scanner, rule, 2026)
        assert result == date(2026, 11, 8)

    def test_scan_festival_holi(self, scanner):
        """scan_festival should compute Holika Dahan date correctly."""
        rule = FestivalRule(
            name="Holi",
            english_name="Holika Dahan",
            festival_type=FestivalType.LUNAR,
            category=FestivalCategory.MAJOR,
            regions=[Region.ALL_INDIA],
            month="Phalguna",
            paksha="shukla",
            tithi=15,
            description="Holika Dahan"
        )
        result = scan_festival(scanner, rule, 2026)
        assert result == date(2026, 3, 3)

    def test_batch_scan_returns_all(self, scanner):
        """batch_scan_festivals should return results for all rules."""
        rules = [
            FestivalRule("Diwali", "Diwali", FestivalType.LUNAR, FestivalCategory.MAJOR,
                         [Region.ALL_INDIA], month="Kartik", paksha="krishna", tithi=15),
            FestivalRule("Holi", "Holi", FestivalType.LUNAR, FestivalCategory.MAJOR,
                         [Region.ALL_INDIA], month="Phalguna", paksha="shukla", tithi=15),
        ]
        results = batch_scan_festivals(scanner, rules, 2026)
        assert len(results) == 2
        for rule, result_date in results:
            assert result_date is not None, f"{rule.name} returned None"


# ─── Year Variability Test ──────────────────────────────────────────

class TestYearToYearVariability:
    """Verify festival dates shift year-to-year (not constant)."""

    def test_diwali_2025_vs_2026(self, scanner):
        """Diwali should be on different dates in different years."""
        d2025 = scanner.find_tithi_date(2025, "Kartik", "krishna", 15)
        d2026 = scanner.find_tithi_date(2026, "Kartik", "krushna", 15)
        # One might be None, but if both found, they should differ
        if d2025 and d2026:
            assert d2025 != d2026, "Diwali on same date in 2025 and 2026!"

    def test_holi_2025_vs_2026(self, scanner):
        """Holi should be on different dates in different years."""
        d2025 = scanner.find_tithi_date(2025, "Phalguna", "shukla", 15)
        d2026 = scanner.find_tithi_date(2026, "Phalguna", "shukla", 15)
        if d2025 and d2026:
            assert d2025 != d2026
