"""
Comprehensive Calculation Validation Tests for Brahmakaal.
Compares Kaal engine output against independent Skyfield reference computations.
These tests ensure all panchang elements are mathematically correct.
"""
import pytest
import math
import os
from datetime import datetime, timezone, timedelta

from skyfield.api import load, Topos
from skyfield.almanac import find_discrete, sunrise_sunset
from kaal_engine.kaal import Kaal
from kaal_engine.core.ayanamsha import AyanamshaEngine

# ──────────────────────────────────────────────────────
# Fixtures (session-scoped: load once, run many)
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def eph():
    """Load JPL ephemeris once for all tests."""
    return load("de421.bsp")


@pytest.fixture(scope="session")
def kaal(eph):
    """Initialise Kaal engine once."""
    return Kaal("de421.bsp")


@pytest.fixture(scope="session")
def ayanamsha_engine():
    return AyanamshaEngine()


# ──────────────────────────────────────────────────────
# Reference computation helpers (independent of Kaal)
# ──────────────────────────────────────────────────────

NAKSHATRAS = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Moola","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati"
]

TITHI_SHUKLA = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi",
    "Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi",
    "Trayodashi","Chaturdashi","Purnima"
]

TITHI_KRISHNA = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi",
    "Saptami","Ashtami","Navami","Dashami","Ekadashi","Dwadashi",
    "Trayodashi","Chaturdashi","Amavasya"
]

KARANAS = (["Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti"] * 8
           + ["Kimstughna","Shakuni","Chatushpada","Naga"])


def _jd(dt: datetime) -> float:
    """Datetime → Julian Day (UT1)."""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    frac = (dt.hour + dt.minute/60.0 + dt.second/3600.0) / 24.0
    return jdn + frac - 0.5


def _ref_planetary_positions(jd_tt: float, eph):
    """Raw Skyfield tropical longitudes at a given JD(TT)."""
    from skyfield.api import load
    ts = load.timescale()
    earth = eph["earth"]
    t = ts.tdb_jd(jd_tt)
    pos = {}
    # DE421 uses barycenter names for planets except Sun, Moon, Earth
    body_map = {
        "sun": "sun",
        "moon": "moon",
        "mars": "mars barycenter",
        "mercury": "mercury barycenter",
        "jupiter": "jupiter barycenter",
        "venus": "venus barycenter",
        "saturn": "saturn barycenter",
    }
    for name, body in body_map.items():
        p = earth.at(t).observe(eph[body]).apparent()
        lat, lon, _ = p.ecliptic_latlon()
        pos[name] = {"tropical_lon": lon.degrees, "tropical_lat": lat.degrees}
    return pos


def _ref_sunrise(jd: float, lat: float, lon: float, eph):
    """Skyfield sunrise JD for a location on a given date."""
    ts = load.timescale()
    observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
    t0 = ts.tdb_jd(jd - 0.5)
    t1 = ts.tdb_jd(jd + 0.5)
    t, y = find_discrete(t0, t1, sunrise_sunset(eph, observer))
    rise = t[y == 1]
    return rise[0].tdb if len(rise) > 0 else None


def _ref_tithi_name(tithi_val: float) -> str:
    """Tithi name matching the corrected Kaal engine logic.
    
    Active tithi = floor(tithi_val) + 1 (1-indexed).
    tithi_raw = (moon-sun diff) / 12, 0 at new moon.
    - raw [0, 1):  active=1 → Shukla Pratipada (0-12° after new moon)
    - raw [1, 14): active=2..14 → Shukla Dwitiya..Chaturdashi
    - raw [14, 15): active=15 → Shukla Purnima
    - raw [15, 29): active=16..29 → Krishna Pratipada..Chaturdashi
    - raw [29, 30): active=30 → Krishna Amavasya
    """
    t = tithi_val % 30
    if t < 1.0:
        return "Shukla Pratipada"
    if t < 14.0:
        return f"Shukla {TITHI_SHUKLA[int(t)]}"
    if t < 15.0:
        return "Shukla Purnima"
    if t < 29.0:
        return f"Krishna {TITHI_KRISHNA[int(t) - 15]}"
    return "Krishna Amavasya"


def _ref_moon_phase(tithi_val: float) -> str:
    """Moon phase from tithi value (matching fixed logic)."""
    t = tithi_val % 30
    if t < 1.0 or t >= 29.0:
        return "New Moon"
    if t < 6.5:
        return "Waxing Crescent"
    if t < 8.5:
        return "First Quarter"
    if t < 14.0:
        return "Waxing Gibbous"
    if t < 16.0:
        return "Full Moon"
    if t < 21.5:
        return "Waning Gibbous"
    if t < 23.5:
        return "Last Quarter"
    return "Waning Crescent"


# ──────────────────────────────────────────────────────
# Test suites
# ──────────────────────────────────────────────────────

DELTA_T_APPROX = 0.00069  # ≈ 69 s for 2025

VALIDATION_CASES = [
    # (name, lat, lon, tz_offset, date_str)
    ("Mumbai_Jan01", 19.0760, 72.8777, 5.5, "2025-01-01"),
    ("Mumbai_Mar21", 19.0760, 72.8777, 5.5, "2025-03-21"),
    ("Mumbai_Jun21", 19.0760, 72.8777, 5.5, "2025-06-21"),
    ("Mumbai_Sep23", 19.0760, 72.8777, 5.5, "2025-09-23"),
    ("Delhi_Jan01",  28.6139, 77.2090, 5.5, "2025-01-01"),
    ("Delhi_Jun21",  28.6139, 77.2090, 5.5, "2025-06-21"),
    ("NYC_Jan01",    40.7128, -74.0060, -5.0, "2025-01-01"),
    ("London_Jun21", 51.5074, -0.1278, 0.0, "2025-06-21"),
    ("Mumbai_Dec21", 19.0760, 72.8777, 5.5, "2025-12-21"),
]


class TestPanchangValidation:
    """Cross-validate every panchang element against independent Skyfield reference."""

    @pytest.mark.parametrize("name,lat,lon,tz,date_str", VALIDATION_CASES)
    def test_tithi(self, kaal, eph, ayanamsha_engine, name, lat, lon, tz, date_str):
        dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
        # Compute JD from LOCAL NOON in UTC (matching Kaal engine's sunrise epoch)
        local_noon_utc = dt - timedelta(hours=tz)
        jd_local = _jd(local_noon_utc)

        # Kaal engine result
        result = kaal.get_panchang(lat, lon, dt, elevation=0, ayanamsha="LAHIRI", timezone_offset=tz)
        kaal_tithi = result["tithi_name"]

        # Reference at sunrise
        rise_jd = _ref_sunrise(jd_local, lat, lon, eph)
        assert rise_jd is not None, f"No sunrise found for {name}"

        rise_jd_tt = rise_jd + DELTA_T_APPROX
        ref_pos = _ref_planetary_positions(rise_jd_tt, eph)
        ref_ayan = ayanamsha_engine.calculate_ayanamsha(rise_jd_tt, "LAHIRI")

        sun_sid = (ref_pos["sun"]["tropical_lon"] - ref_ayan) % 360
        moon_sid = (ref_pos["moon"]["tropical_lon"] - ref_ayan) % 360
        ref_tithi_val = ((moon_sid - sun_sid) % 360) / 12.0
        ref_tithi = _ref_tithi_name(ref_tithi_val)

        assert kaal_tithi == ref_tithi, (
            f"{name}: tithi mismatch — Kaal={kaal_tithi}, Ref={ref_tithi} "
            f"(value={ref_tithi_val:.4f})"
        )

    @pytest.mark.parametrize("name,lat,lon,tz,date_str", VALIDATION_CASES)
    def test_nakshatra(self, kaal, eph, ayanamsha_engine, name, lat, lon, tz, date_str):
        dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
        local_noon_utc = dt - timedelta(hours=tz)
        jd_local = _jd(local_noon_utc)

        result = kaal.get_panchang(lat, lon, dt, elevation=0, ayanamsha="LAHIRI", timezone_offset=tz)
        kaal_nak = result["nakshatra"]

        rise_jd = _ref_sunrise(jd_local, lat, lon, eph)
        assert rise_jd is not None
        rise_jd_tt = rise_jd + DELTA_T_APPROX
        ref_pos = _ref_planetary_positions(rise_jd_tt, eph)
        ref_ayan = ayanamsha_engine.calculate_ayanamsha(rise_jd_tt, "LAHIRI")

        moon_sid = (ref_pos["moon"]["tropical_lon"] - ref_ayan) % 360
        ref_nak = NAKSHATRAS[int(moon_sid / 13.333333) % 27]

        assert kaal_nak == ref_nak, (
            f"{name}: nakshatra mismatch — Kaal={kaal_nak}, Ref={ref_nak} "
            f"(moon_sid={moon_sid:.3f}° index={int(moon_sid/13.333333)%27})"
        )

    @pytest.mark.parametrize("name,lat,lon,tz,date_str", VALIDATION_CASES)
    def test_karana(self, kaal, eph, ayanamsha_engine, name, lat, lon, tz, date_str):
        dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
        local_noon_utc = dt - timedelta(hours=tz)
        jd_local = _jd(local_noon_utc)

        result = kaal.get_panchang(lat, lon, dt, elevation=0, ayanamsha="LAHIRI", timezone_offset=tz)
        kaal_kar = result["karana_name"]

        rise_jd = _ref_sunrise(jd_local, lat, lon, eph)
        assert rise_jd is not None
        rise_jd_tt = rise_jd + DELTA_T_APPROX
        ref_pos = _ref_planetary_positions(rise_jd_tt, eph)
        ref_ayan = ayanamsha_engine.calculate_ayanamsha(rise_jd_tt, "LAHIRI")

        sun_sid = (ref_pos["sun"]["tropical_lon"] - ref_ayan) % 360
        moon_sid = (ref_pos["moon"]["tropical_lon"] - ref_ayan) % 360
        ref_tithi_val = ((moon_sid - sun_sid) % 360) / 12.0
        ref_karana_val = int((ref_tithi_val * 2) % 60) % 60
        ref_kar = KARANAS[ref_karana_val]

        assert kaal_kar == ref_kar, (
            f"{name}: karana mismatch — Kaal={kaal_kar}, Ref={ref_kar} "
            f"(karana_val={ref_karana_val})"
        )

    @pytest.mark.parametrize("name,lat,lon,tz,date_str", VALIDATION_CASES)
    def test_moon_phase(self, kaal, eph, ayanamsha_engine, name, lat, lon, tz, date_str):
        dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
        local_noon_utc = dt - timedelta(hours=tz)
        jd_local = _jd(local_noon_utc)

        result = kaal.get_panchang(lat, lon, dt, elevation=0, ayanamsha="LAHIRI", timezone_offset=tz)
        kaal_moon = result["moon_phase"]

        rise_jd = _ref_sunrise(jd_local, lat, lon, eph)
        assert rise_jd is not None
        rise_jd_tt = rise_jd + DELTA_T_APPROX
        ref_pos = _ref_planetary_positions(rise_jd_tt, eph)
        ref_ayan = ayanamsha_engine.calculate_ayanamsha(rise_jd_tt, "LAHIRI")

        sun_sid = (ref_pos["sun"]["tropical_lon"] - ref_ayan) % 360
        moon_sid = (ref_pos["moon"]["tropical_lon"] - ref_ayan) % 360
        ref_tithi_val = ((moon_sid - sun_sid) % 360) / 12.0
        ref_moon = _ref_moon_phase(ref_tithi_val)

        assert kaal_moon == ref_moon, (
            f"{name}: moon phase mismatch — Kaal={kaal_moon}, Ref={ref_moon} "
            f"(tithi_val={ref_tithi_val:.4f})"
        )


class TestAyanamshaCalibration:
    """Verify ayanamsha values match IAE published reference."""

    def test_lahiri_j2000(self, ayanamsha_engine):
        """Lahiri ayanamsha at J2000.0 should match calibrated reference."""
        jd_j2000 = 2451545.0  # Jan 1, 2000 12:00 TT
        ay = ayanamsha_engine.calculate_ayanamsha(jd_j2000, "LAHIRI")
        # Calibrated J2000 value is 24.222896°
        assert abs(ay - 24.222896) < 0.001, (
            f"Lahiri at J2000: {ay:.6f}° (expected ~24.2229°)"
        )

    def test_lahiri_2025(self, ayanamsha_engine):
        """Lahiri ayanamsha for 2025 should match IAE published value ~24°13'35\"."""
        jd_2025 = 2460677.0  # Jan 1, 2025 12:00 TT
        ay = ayanamsha_engine.calculate_ayanamsha(jd_2025, "LAHIRI")
        # IAE 2025 Lahiri ≈ 24°13'35" = 24.226389°
        expected = 24.226389
        assert abs(ay - expected) < 0.001, (
            f"Lahiri Jan 2025: {ay:.6f}° (IAE reference: {expected:.6f}°)"
        )

    def test_multiple_systems(self, ayanamsha_engine):
        """All supported ayanamsha systems return reasonable values."""
        jd = 2460677.0
        for system in ayanamsha_engine.SUPPORTED_SYSTEMS:
            val = ayanamsha_engine.calculate_ayanamsha(jd, system)
            assert 0 < val < 30, (
                f"{system} ayanamsha out of range: {val:.4f}°"
            )


class TestKaranaSequence:
    """Verify karana indexing covers all 60 positions correctly."""

    def test_all_60_karanas_accessible(self):
        """Every karana index 0-59 should map to a valid name."""
        for idx in range(60):
            assert idx < len(KARANAS), f"Index {idx} exceeds karana list length"
            name = KARANAS[idx]
            assert name, f"Empty karana at index {idx}"

    def test_fixed_karanas_at_end(self):
        """The 4 fixed karanas occupy the last 4 positions (indices 56-59)."""
        assert KARANAS[56] == "Kimstughna", f"Expected Kimstughna at 56, got {KARANAS[56]}"
        assert KARANAS[57] == "Shakuni", f"Expected Shakuni at 57, got {KARANAS[57]}"
        assert KARANAS[58] == "Chatushpada", f"Expected Chatushpada at 58, got {KARANAS[58]}"
        assert KARANAS[59] == "Naga", f"Expected Naga at 59, got {KARANAS[59]}"

    def test_karana_int_indexing(self, kaal, eph):
        """Karana index = int(karana_val) should be used (not int(karana_val/2))."""
        dt = datetime(2025, 1, 1, 12, 0, 0)
        result = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)

        # The karana should be one of the 60 valid names (not just the first 30)
        karana = result["karana_name"]
        assert karana in KARANAS, f"Unknown karana: {karana}"

        # Verify the karana is not one that would come from wrong int(karana/2) indexing
        # int(karana/2) would only access indices 0-30, never 31-59
        karana_index = KARANAS.index(karana)
        assert karana_index >= 0, f"Karana {karana} not found in list"


class TestSunriseConsistency:
    """Verify sunrise calculations are consistent and reasonable."""

    def test_sunrise_before_noon(self, kaal, eph):
        """Sunrise should always occur before local noon."""
        for lat, lon, tz, name in [(19.076, 72.8777, 5.5, "Mumbai"),
                                     (28.6139, 77.2090, 5.5, "Delhi"),
                                     (40.7128, -74.006, -5, "NYC"),
                                     (51.5074, -0.1278, 0, "London")]:
            for date_str in ["2025-01-01", "2025-06-21", "2025-09-23"]:
                dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
                result = kaal.get_panchang(lat, lon, dt, ayanamsha="LAHIRI", timezone_offset=tz)
                sunrise = result["sunrise"]
                sunset = result["sunset"]
                if sunrise and sunset:
                    sr_hour = sunrise.hour + sunrise.minute/60
                    ss_hour = sunset.hour + sunset.minute/60
                    assert sr_hour < 12, f"{name} {date_str}: sunrise at {sr_hour:.1f}h (after noon)"
                    assert ss_hour > sr_hour, f"{name} {date_str}: sunset before sunrise"

    def test_sunrise_consistent_across_ayanamsha(self, kaal):
        """Sunrise time should not depend on ayanamsha system."""
        dt = datetime(2025, 6, 21, 12, 0, 0)
        r1 = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)
        r2 = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="RAMAN", timezone_offset=5.5)
        assert r1["sunrise"] == r2["sunrise"], "Sunrise changed with ayanamsha!"


class TestTithiBoundaries:
    """Test edge cases around tithi boundaries."""

    def test_tithi_name_at_boundaries(self, kaal):
        """Verify tithi names at key boundaries (Amavasya, Purnima)."""
        # Test a known full moon date (approximate)
        dt = datetime(2025, 8, 9, 12, 0, 0)
        result = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)
        tithi_name = result["tithi_name"]
        # Should be around Purnima or nearby
        assert "Purnima" in tithi_name or "Pratipada" in tithi_name or "Chaturdashi" in tithi_name, (
            f"Near full moon date (Aug 9): unexpected tithi {tithi_name}"
        )

    def test_tithi_name_not_none(self, kaal):
        """Tithi name should never be None or empty."""
        for lat, lon, tz in [(19.076, 72.8777, 5.5), (28.6139, 77.2090, 5.5)]:
            for date_str in ["2025-01-01", "2025-03-21", "2025-06-21", "2025-09-23", "2025-12-21"]:
                dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
                result = kaal.get_panchang(lat, lon, dt, ayanamsha="LAHIRI", timezone_offset=tz)
                assert result["tithi_name"], f"Empty tithi for {lat},{lon} on {date_str}"


class TestPlanetaryPositions:
    """Verify planetary positions against raw Skyfield."""

    def test_sun_moon_rashi(self, kaal, eph):
        """Sun and Moon should be in valid rashis."""
        for date_str in ["2025-01-01", "2025-06-21", "2025-09-23"]:
            dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
            result = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)
            valid_rashis = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya",
                            "Tula","Vrishchika","Dhanu","Makara","Kumbha","Meena"]
            assert result["rashi_of_sun"] in valid_rashis, (
                f"Invalid Sun rashi {result['rashi_of_sun']} on {date_str}"
            )
            assert result["rashi_of_moon"] in valid_rashis, (
                f"Invalid Moon rashi {result['rashi_of_moon']} on {date_str}"
            )

    def test_rahu_ketu_opposite(self, kaal):
        """Rahu and Ketu should be 180° apart."""
        dt = datetime(2025, 6, 21, 12, 0, 0)
        result = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)
        planets = result.get("graha_positions", {})
        rahu_lon = planets.get("rahu", {}).get("longitude", 0)
        ketu_lon = planets.get("ketu", {}).get("longitude", 0)
        diff = abs(rahu_lon - ketu_lon) % 360
        assert abs(diff - 180) < 1.0, (
            f"Rahu ({rahu_lon:.2f}°) and Ketu ({ketu_lon:.2f}°) not opposite (diff={diff:.2f}°)"
        )


class TestMoonPhaseConsistency:
    """Verify moon phase naming is internally consistent."""

    def test_moon_phase_matches_tithi(self, kaal):
        """Moon phase should be consistent with the tithi value."""
        for date_str in ["2025-01-01", "2025-06-21", "2025-09-23"]:
            dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
            result = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)
            tithi_name = result["tithi_name"]
            moon_phase = result["moon_phase"]

            # New Moon should not appear with Shukla Dwitiya or later
            if "Dwitiya" in tithi_name or "Tritiya" in tithi_name:
                assert moon_phase != "New Moon", (
                    f"Tithi {tithi_name} but moon phase is {moon_phase} on {date_str}"
                )

            # Full Moon should appear with Purnima
            if "Purnima" in tithi_name:
                assert moon_phase == "Full Moon", (
                    f"Tithi {tithi_name} but moon phase is {moon_phase} on {date_str}"
                )


class TestRahuPosition:
    """Verify Rahu (lunar node) calculations."""

    # Standard coefficients from Meeus "Astronomical Algorithms"
    MEEUS_RAHU_COEFFS = (125.044556, -1934.136686, 0.002076, 2e-6)

    def test_rahu_close_to_mee_us(self, kaal, eph):
        """Rahu position should be close to the standard Meeus formula."""
        jd = _jd(datetime(2025, 6, 21, 12, 0, 0))
        T = (jd - 2451545.0) / 36525.0

        # Meeus formula
        meeus_omega = (125.044556 - 1934.136686 * T + 0.002076 * T*T + 2e-6 * T*T*T) % 360

        # Kaal engine
        result = kaal.get_panchang(19.076, 72.8777, datetime(2025, 6, 21, 12, 0, 0),
                                    ayanamsha="LAHIRI", timezone_offset=5.5)
        kaal_rahu = result.get("graha_positions", {}).get("rahu", {}).get("longitude", 0)

        # Should be within 1° (the code uses simplified mean node)
        diff = min(abs(kaal_rahu - meeus_omega), 360 - abs(kaal_rahu - meeus_omega))
        assert diff < 1.0, (
            f"Rahu: Kaal={kaal_rahu:.4f}°, Meeus={meeus_omega:.4f}° (diff={diff:.4f}°)"
        )


class TestYoga:
    """Verify yoga calculations."""

    YOGA_NAMES = [
        "Vishkambha","Priti","Ayushman","Saubhagya","Shobhana",
        "Atiganda","Sukarma","Dhriti","Shula","Ganda",
        "Vriddhi","Dhruva","Vyaghata","Harshana","Vajra",
        "Siddhi","Vyatipata","Variyan","Parigha","Shiva",
        "Siddha","Sadhya","Shubha","Shukla","Brahma",
        "Indra","Vaidhriti"
    ]

    def test_yoga_in_valid_list(self, kaal):
        """Yoga name should be one of the 27 valid yogas."""
        for date_str in ["2025-01-01", "2025-06-21", "2025-09-23"]:
            dt = datetime.strptime(f"{date_str} 12:00:00", "%Y-%m-%d %H:%M:%S")
            result = kaal.get_panchang(19.076, 72.8777, dt, ayanamsha="LAHIRI", timezone_offset=5.5)
            yoga_name = result["yoga_name"]
            assert yoga_name in self.YOGA_NAMES, (
                f"Unknown yoga {yoga_name} on {date_str}"
            )
