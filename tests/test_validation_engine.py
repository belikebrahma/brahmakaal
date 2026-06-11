"""
Tests for the Festival Validation Engine (Phase 4).

Test categories:
1. ValidationResult / ValidationReport data classes
2. Reference dataset loading
3. Single festival validation vs reference
4. Full-year validation vs reference
5. Self-consistency checks
6. Multi-year summary
7. Festival drift across years
8. Integration with real FestivalEngine
9. Edge cases (missing data, invalid dates)
"""

import pytest
import json
import os
import tempfile
from datetime import date, datetime
from pathlib import Path

from kaal_engine.core.validation_engine import (
    FestivalValidator,
    ValidationResult,
    ValidationReport,
    REFERENCE_DATA_PATH,
)


# ──────────────────────────────────────────────────
# Sample reference data for unit tests (no engine needed)
# ──────────────────────────────────────────────────

SAMPLE_REFERENCE = {
    "2026": {
        "Diwali": {"date": "2026-11-09", "source": "test", "method": "tithi_scanner"},
        "Dussehra": {"date": "2026-09-21", "source": "test", "method": "tithi_scanner"},
        "Holika Dahan": {"date": "2026-03-04", "source": "test", "method": "tithi_scanner"},
        "Makar Sankranti": {"date": "2026-01-15", "source": "test", "method": "solar_scan"},
        "Guru Purnima": {"date": "2026-06-29", "source": "test", "method": "tithi_scanner"},
        "Ganesh Chaturthi": {"date": "2026-08-16", "source": "test", "method": "tithi_scanner"},
        "Maha Shivaratri": {"date": "2026-02-16", "source": "test", "method": "tithi_scanner"},
    },
    "2025": {
        "Diwali": {"date": "2025-10-20", "source": "test", "method": "tithi_scanner"},
    },
    "_meta": {
        "version": "test",
        "years_covered": ["2025", "2026"],
    },
}


@pytest.fixture
def sample_reference_path():
    """Create a temporary reference JSON file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(SAMPLE_REFERENCE, f)
        path = f.name
    yield path
    os.unlink(path)


@pytest.fixture
def empty_reference_path():
    """Create an empty reference JSON."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({}, f)
        path = f.name
    yield path
    os.unlink(path)


# ──────────────────────────────────────────────────
# ValidationResult Tests
# ──────────────────────────────────────────────────

class TestValidationResult:
    def test_passed_result(self):
        r = ValidationResult("Diwali", 2026, date(2026, 11, 9), "2026-11-09",
                            diff_days=0, passed=True)
        assert r.passed
        assert r.festival_name == "Diwali"
        assert r.diff_days == 0
        # String representation should show ✅
        assert "✅" in repr(r)
        assert "Diwali" in repr(r)

    def test_failed_result(self):
        r = ValidationResult("Diwali", 2026, date(2026, 11, 9), "2026-11-10",
                            diff_days=1, passed=False,
                            notes="MISMATCH: computed=2026-11-09, ref=2026-11-10")
        assert not r.passed
        assert r.diff_days == 1
        assert "❌" in repr(r)

    def test_to_dict(self):
        r = ValidationResult("Test", 2026, date(2026, 6, 1), "2026-06-01",
                            ref_source="drik_panchang", diff_days=0, passed=True)
        d = r.to_dict()
        assert d["festival"] == "Test"
        assert d["passed"]
        assert d["ref_source"] == "drik_panchang"
        assert d["computed"] == "2026-06-01"

    def test_no_computed_date(self):
        r = ValidationResult("Fake", 2026, None, None, passed=False,
                            notes="Cannot compute")
        assert r.computed_date is None
        assert not r.passed


# ──────────────────────────────────────────────────
# ValidationReport Tests
# ──────────────────────────────────────────────────

class TestValidationReport:
    def test_empty_report(self):
        report = ValidationReport(2026)
        assert report.total == 0
        assert report.passed == 0
        assert report.failed == 0
        assert report.pass_rate == 0.0
        summary = report.summary()
        assert "0 festivals" in summary
        assert "0.0%" in summary

    def test_all_passed(self):
        report = ValidationReport(2026)
        for name in ["A", "B", "C"]:
            report.add_result(ValidationResult(name, 2026, date(2026, 1, 1),
                                              "2026-01-01", passed=True))
        assert report.total == 3
        assert report.passed == 3
        assert report.failed == 0
        assert report.pass_rate == 100.0

    def test_mixed_results(self):
        report = ValidationReport(2026)
        report.add_result(ValidationResult("Pass", 2026, date(2026, 1, 1),
                                          "2026-01-01", passed=True))
        report.add_result(ValidationResult("Fail", 2026, date(2026, 1, 2),
                                          "2026-01-01", diff_days=1, passed=False))
        assert report.total == 2
        assert report.passed == 1
        assert report.failed == 1
        assert report.pass_rate == 50.0

    def test_consistency_issues(self):
        report = ValidationReport(2026)
        report.add_issue("Duplicate festival on 2026-01-01")
        report.add_issue("Missing major festival: Diwali")
        assert len(report.consistency_issues) == 2
        assert "consistency" in report.summary().lower()

    def test_to_dict(self):
        report = ValidationReport(2026)
        report.add_result(ValidationResult("A", 2026, date(2026, 1, 1),
                                          "2026-01-01", passed=True))
        d = report.to_dict()
        assert d["year"] == 2026
        assert d["passed"] == 1
        assert len(d["results"]) == 1


# ──────────────────────────────────────────────────
# FestivalValidator Unit Tests
# ──────────────────────────────────────────────────

class TestFestivalValidator:
    def test_init_with_path(self, sample_reference_path):
        """Validator loads reference from file path."""
        v = FestivalValidator(festival_engine=None, reference_path=sample_reference_path)
        assert "2026" in v.reference_data
        assert "2025" in v.reference_data
        assert v.reference_data["2026"]["Diwali"]["date"] == "2026-11-09"

    def test_init_no_reference(self):
        """Validator loads default reference even without explicit path."""
        v = FestivalValidator(festival_engine=None)
        # Should load the default reference dataset (which exists)
        assert isinstance(v.reference_data, dict)
        # The default dataset has _meta and year entries
        assert "_meta" in v.reference_data or len(v.reference_data) > 0

    def test_init_empty_reference(self, empty_reference_path):
        """Validator handles empty reference."""
        v = FestivalValidator(festival_engine=None, reference_path=empty_reference_path)
        assert v.reference_data == {}

    def test_parse_ref_date_direct(self):
        """Parse reference date from direct date string."""
        v = FestivalValidator(festival_engine=None)
        result = v._parse_ref_date({"date": "2026-11-09"}, 2026)
        assert result == "2026-11-09"

    def test_parse_ref_date_year_specific(self):
        """Parse reference date from year-specific sub-object."""
        v = FestivalValidator(festival_engine=None)
        entry = {"2026": {"date": "2026-11-09"}}
        result = v._parse_ref_date(entry, 2026)
        assert result == "2026-11-09"

    def test_validate_without_engine(self):
        """Validation without engine returns proper failure."""
        v = FestivalValidator(festival_engine=None)
        result = v.validate_festival("Diwali", 2026, against="reference")
        # Should fail gracefully — no engine to compute
        assert result is not None
        assert not result.passed  # Either no ref or can't compute

    def test_validate_invalid_date_format(self):
        """Validation with invalid reference date."""
        ref = {"2026": {"Diwali": {"date": "not-a-date"}}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(ref, f)
            path = f.name
        v = FestivalValidator(festival_engine=None, reference_path=path)
        result = v.validate_festival("Diwali", 2026, against="reference")
        assert result is not None
        assert not result.passed
        # Without engine, it can't compute the date, so the invalid format
        # is the secondary error (after failed computation), not the primary
        os.unlink(path)

    def test_missing_reference_entry(self):
        """Validation with missing reference entry returns failure."""
        v = FestivalValidator(festival_engine=None)
        result = v.validate_festival("NonExistentFestival", 2026, against="reference")
        assert result is not None
        assert not result.passed

    def test_self_consistency_no_engine(self):
        """Self-consistency check without engine."""
        v = FestivalValidator(festival_engine=None)
        issues = v.validate_self_consistency(2026)
        assert "No FestivalEngine available" in issues

    def test_multi_year_empty(self):
        """Multi-year validation with no engine."""
        v = FestivalValidator(festival_engine=None)
        reports = v.validate_multi_year([2025, 2026], against="reference")
        assert 2025 in reports
        assert 2026 in reports
        # Without engine, festivals can't be computed. The reference data
        # IS loaded but compute returns None for each, so results are failures.
        # Total may be >0 from reference entries, all marked failed.

    def test_drift_no_engine(self):
        """Festival drift check without engine returns None dates."""
        v = FestivalValidator(festival_engine=None)
        dates = v.check_drift("Diwali", [2025, 2026, 2027])
        assert all(d is None for d in dates.values())


# ──────────────────────────────────────────────────
# Reference Dataset Integration Tests
# ──────────────────────────────────────────────────

class TestReferenceDataset:
    """Tests that the actual reference dataset is valid JSON and has expected structure."""

    def test_reference_file_exists(self):
        """Reference dataset file must exist at the expected location."""
        assert REFERENCE_DATA_PATH.exists(), (
            f"Reference dataset not found at {REFERENCE_DATA_PATH}"
        )

    def test_reference_is_valid_json(self):
        """Reference dataset must be valid JSON."""
        with open(REFERENCE_DATA_PATH) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_reference_has_meta(self):
        """Reference must have _meta key."""
        with open(REFERENCE_DATA_PATH) as f:
            data = json.load(f)
        assert "_meta" in data, "Missing _meta section"

    def test_reference_has_years(self):
        """Reference must have at least one year of data."""
        with open(REFERENCE_DATA_PATH) as f:
            data = json.load(f)
        years = [k for k in data if k != "_meta"]
        assert len(years) >= 1, "No year data found"

    def test_reference_entries_have_dates(self):
        """All reference entries must have valid date strings."""
        with open(REFERENCE_DATA_PATH) as f:
            data = json.load(f)
        for year_key in data:
            if year_key == "_meta":
                continue
            for name, entry in data[year_key].items():
                assert "date" in entry, f"{name} ({year_key}) missing date"
                date_str = entry["date"]
                # Date must be YYYY-MM-DD format
                parts = date_str.split("-")
                assert len(parts) == 3, f"{name}: invalid date format '{date_str}'"
                y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                assert 2000 <= y <= 2100, f"{name}: year out of range {y}"
                assert 1 <= m <= 12, f"{name}: month out of range {m}"
                assert 1 <= d <= 31, f"{name}: day out of range {d}"

    def test_reference_entries_have_source(self):
        """All reference entries should have a source field."""
        with open(REFERENCE_DATA_PATH) as f:
            data = json.load(f)
        for year_key in data:
            if year_key == "_meta":
                continue
            for name, entry in data[year_key].items():
                assert "source" in entry, f"{name} ({year_key}) missing source"

    def test_dp_reference_usable(self):
        """Validate that the reference can be loaded by the validator."""
        v = FestivalValidator(festival_engine=None)
        assert "2026" in v.reference_data
        diwali = v.reference_data.get("2026", {}).get("Diwali", {})
        assert diwali.get("date") == "2026-11-08"


# ──────────────────────────────────────────────────
# DP Fetcher Integration Tests
# ──────────────────────────────────────────────────

class TestDPComparison:
    """Tests that require Drik Panchang data (may fail without network)."""

    def test_dp_validator_has_tithi_parser(self):
        """Validator can parse expected tithi from FestivalRule names."""
        from kaal_engine.core.validation_engine import FestivalValidator
        v = FestivalValidator(festival_engine=None)
        # _get_expected_tithi returns None without engine
        assert v._get_expected_tithi("Diwali") is None


# ──────────────────────────────────────────────────
# Edge Cases
# ──────────────────────────────────────────────────

class TestEdgeCases:
    def test_no_reference_file(self):
        """Validator handles missing reference file gracefully."""
        v = FestivalValidator(festival_engine=None, reference_path="/nonexistent/path.json")
        assert v.reference_data == {}

    def test_malformed_json_reference(self):
        """Validator handles malformed JSON reference."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{broken json!!")
            path = f.name
        v = FestivalValidator(festival_engine=None, reference_path=path)
        assert v.reference_data == {}
        os.unlink(path)

    def test_partial_reference(self):
        """Partial reference (only some festivals) handled okay."""
        partial = {"2026": {"Diwali": {"date": "2026-11-09"}}}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(partial, f)
            path = f.name
        v = FestivalValidator(festival_engine=None, reference_path=path)
        assert "2026" in v.reference_data
        assert "Dussehra" not in v.reference_data.get("2026", {})
        os.unlink(path)

    def test_verify_year_dates_are_valid(self):
        """Each year's festival dates should be valid YYYY-MM-DD strings."""
        with open(REFERENCE_DATA_PATH) as f:
            data = json.load(f)
        for year_key in data:
            if year_key == "_meta":
                continue
            for name, entry in data[year_key].items():
                try:
                    d = datetime.strptime(entry["date"], "%Y-%m-%d").date()
                except (ValueError, KeyError) as e:
                    pytest.fail(f"{name} ({year_key}) has invalid date: {e}")
                # Year must match the year_key
                if year_key.isdigit():
                    assert d.year == int(year_key), (
                        f"{name}: date year {d.year} != reference year {year_key}"
                    )


# ──────────────────────────────────────────────────
# Integration Tests (requires Kaal + FestivalEngine)
# ──────────────────────────────────────────────────

@pytest.fixture(scope="session")
def session_validator():
    """Create a validator once per test session (slow init, fast per-festival)."""
    from kaal_engine.kaal import Kaal
    from kaal_engine.core.festivals import FestivalEngine

    k = Kaal("de421.bsp")
    fe = FestivalEngine(
        k, lat=28.6139, lod=77.2090,
        timezone_offset=5.5, elevation=0
    )
    return FestivalValidator(festival_engine=fe)


class TestIntegration:
    """Integration tests with real FestivalEngine.
    
    These tests verify that FestivalValidator works end-to-end with
    the actual computation engine and reference dataset.
    
    Note: Each test takes ~10-30s because TithiScanner scans day by day.
    Use --runslow to execute.
    """

    @pytest.mark.slow
    def test_validate_diwali_against_reference(self, session_validator):
        """Diwali 2026 must match reference exactly."""
        result = session_validator.validate_festival("Diwali", 2026, against="reference")
        assert result is not None
        assert result.passed, (
            f"Diwali 2026 mismatch: computed={result.computed_date}, "
            f"ref={result.reference_date} (diff={result.diff_days}d)"
        )

    @pytest.mark.slow
    def test_validate_dussehra_against_reference(self, session_validator):
        """Dussehra 2026 must match reference exactly."""
        result = session_validator.validate_festival("Dussehra", 2026, against="reference")
        assert result is not None
        assert result.passed, (
            f"Dussehra 2026 mismatch: computed={result.computed_date}, "
            f"ref={result.reference_date}"
        )

    @pytest.mark.slow
    def test_validate_holika_dahan_against_reference(self, session_validator):
        """Holika Dahan 2026 must match reference exactly."""
        result = session_validator.validate_festival("Holika Dahan", 2026, against="reference")
        assert result is not None
        assert result.passed, (
            f"Holika Dahan 2026 mismatch: computed={result.computed_date}, "
            f"ref={result.reference_date}"
        )

    @pytest.mark.slow
    def test_validate_makar_sankranti_against_reference(self, session_validator):
        """Makar Sankranti 2026 must match reference exactly."""
        result = session_validator.validate_festival("Makar Sankranti", 2026, against="reference")
        assert result is not None
        assert result.passed, (
            f"Makar Sankranti 2026 mismatch: computed={result.computed_date}, "
            f"ref={result.reference_date}"
        )

    @pytest.mark.slow
    def test_validate_guru_purnima_against_reference(self, session_validator):
        """Guru Purnima 2026 must match reference exactly."""
        result = session_validator.validate_festival("Guru Purnima", 2026, against="reference")
        assert result is not None
        assert result.passed, (
            f"Guru Purnima mismatch: computed={result.computed_date}, "
            f"ref={result.reference_date}"
        )

    @pytest.mark.slow
    def test_diwali_2025(self, session_validator):
        """Diwali 2025 — already in reference."""
        result = session_validator.validate_festival("Diwali", 2025, against="reference")
        if result:
            print(f"  Diwali 2025: {result}")

    @pytest.mark.slow
    def test_diwali_drift(self, session_validator):
        """Diwali should not drift more than 30 days year-over-year."""
        dates = session_validator.check_drift("Diwali", [2025, 2026])
        if dates.get(2025) and dates.get(2026):
            diff = abs((dates[2026] - dates[2025]).days)
            assert 10 <= diff <= 30, (
                f"Diwali drift 2025→2026: {diff} days (expected 10-30)"
            )
            print(f"  Diwali drift 2025→2026: {diff} days ✅")

    @pytest.mark.slow
    def test_batch_validate_major_2026(self, session_validator):
        """Batch validate 5 major 2026 festivals."""
        festivals = ["Diwali", "Dussehra", "Holika Dahan", "Makar Sankranti", "Guru Purnima"]
        passed = 0
        total = 0
        for name in festivals:
            r = session_validator.validate_festival(name, 2026, against="reference")
            if r:
                total += 1
                if r.passed:
                    passed += 1
                print(f"  {name}: {'✅' if r.passed else '❌'} computed={r.computed_date} ref={r.reference_date}")
        
        assert passed >= total - 1, f"Only {passed}/{total} passed"
        print(f"  → {passed}/{total} passed")
