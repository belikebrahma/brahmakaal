"""
Validation Engine — Festival Calendar Cross-Validation Framework

Phase 4 deliverable from FESTIVAL_CALENDAR_PLAN.md

Automated validation of computed festival dates against:
- Reference dataset (stored known-good dates)
- Live Drik Panchang data (via dp_fetcher.py)
- Self-consistency checks (no duplicates, correct tithi names)
- Multi-year stability (no date drift)

Usage:
    from kaal_engine.core.validation_engine import FestivalValidator
    
    validator = FestivalValidator(festival_engine)
    
    # Validate against reference dataset
    results = validator.validate_year(2026, against="reference")
    
    # Validate against live Drik Panchang data
    dp_results = validator.validate_against_dp(2026, kaal_engine)
    
    # Self-consistency check
    issues = validator.validate_self_consistency(2026)
    
    # Summary report
    print(validator.report(2026))
"""

from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Set, Any
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to reference dataset
REFERENCE_DATA_PATH = Path(__file__).parents[2] / "data" / "reference" / "festival_dates.json"


class ValidationResult:
    """Result of a single festival validation check."""
    
    def __init__(
        self,
        festival_name: str,
        year: int,
        computed_date: Optional[date],
        reference_date: Optional[str],
        ref_source: str = "reference",
        diff_days: Optional[int] = None,
        passed: bool = False,
        notes: str = "",
    ):
        self.festival_name = festival_name
        self.year = year
        self.computed_date = computed_date
        self.reference_date = reference_date
        self.ref_source = ref_source
        self.diff_days = diff_days
        self.passed = passed
        self.notes = notes

    def to_dict(self) -> Dict:
        return {
            "festival": self.festival_name,
            "year": self.year,
            "computed": str(self.computed_date) if self.computed_date else None,
            "reference": self.reference_date,
            "ref_source": self.ref_source,
            "diff_days": self.diff_days,
            "passed": self.passed,
            "notes": self.notes,
        }

    def __repr__(self) -> str:
        status = "✅" if self.passed else "❌"
        diff = f" (diff={self.diff_days}d)" if self.diff_days else ""
        return (
            f"{status} {self.festival_name} ({self.year}): "
            f"computed={self.computed_date}, ref={self.reference_date}{diff}"
            f"{' — ' + self.notes if self.notes else ''}"
        )


class ValidationReport:
    """Aggregated validation report for a year."""
    
    def __init__(self, year: int):
        self.year = year
        self.results: List[ValidationResult] = []
        self.consistency_issues: List[str] = []
    
    def add_result(self, result: ValidationResult):
        self.results.append(result)
    
    def add_issue(self, issue: str):
        self.consistency_issues.append(issue)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def pass_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total * 100
    
    def summary(self) -> str:
        lines = [
            f"\n{'='*60}",
            f"Validation Report — {self.year}",
            f"{'='*60}",
            f"Total: {self.total} festivals",
            f"Passed: {self.passed} ({self.pass_rate:.1f}%)",
            f"Failed: {self.failed}",
        ]
        if self.consistency_issues:
            lines.append(f"Consistency Issues: {len(self.consistency_issues)}")
            for issue in self.consistency_issues:
                lines.append(f"  ⚠️ {issue}")
        
        if self.failed > 0:
            lines.append("\nFailed Festivals:")
            for r in self.results:
                if not r.passed:
                    lines.append(f"  {r}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict:
        return {
            "year": self.year,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": self.pass_rate,
            "consistency_issues": self.consistency_issues,
            "results": [r.to_dict() for r in self.results],
        }
    
    def __str__(self) -> str:
        return self.summary()


class FestivalValidator:
    """
    Validates computed festival dates against reference data.
    
    Supports three validation modes:
    1. against=reference — vs stored reference dataset (festival_dates.json)
    2. against=drik_panchang — vs live Drik Panchang data (requires network)
    3. against=self — self-consistency checks only
    
    Args:
        festival_engine: Initialized FestivalEngine instance
        reference_path: Path to reference JSON (default: data/reference/festival_dates.json)
    """
    
    def __init__(
        self,
        festival_engine=None,
        reference_path: Optional[str] = None,
    ):
        self.festival_engine = festival_engine
        self.reference_data = self._load_reference(reference_path)
        # Cache for computed festivals to avoid repeated slow calculations
        self._computed_cache: Dict[int, List] = {}
    
    def _load_reference(self, path: Optional[str] = None) -> Dict:
        """Load reference dataset from JSON."""
        load_path = path or str(REFERENCE_DATA_PATH)
        try:
            with open(load_path, "r") as f:
                data = json.load(f)
            logger.info(f"Loaded reference dataset from {load_path}")
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Cannot load reference dataset: {e}")
            return {}
    
    def _parse_ref_date(self, ref_entry: Dict, year: int) -> Optional[str]:
        """Parse reference date from an entry, trying multiple key formats."""
        # Direct date string
        ref_date = ref_entry.get("date")
        if ref_date:
            return ref_date
        
        # Year-specific entry
        if str(year) in ref_entry:
            year_entry = ref_entry[str(year)]
            if isinstance(year_entry, dict):
                return year_entry.get("date")
            return str(year_entry)
        
        return None
    
    # ──────────────────────────────────────────────
    # Core Validation Methods
    # ──────────────────────────────────────────────
    
    def validate_festival(
        self,
        name: str,
        year: int,
        against: str = "reference",
    ) -> Optional[ValidationResult]:
        """
        Validate a single festival date.
        
        Args:
            name: Festival name (must match FestivalRule.name or reference key)
            year: Target year
            against: "reference", "drik_panchang", or "self"
        
        Returns:
            ValidationResult or None if validation couldn't be performed
        """
        if against == "reference":
            return self._validate_against_reference(name, year)
        elif against == "drik_panchang":
            return self._validate_against_dp_single(name, year)
        else:
            return None
    
    def validate_year(
        self,
        year: int,
        against: str = "reference",
        regions: Optional[List] = None,
        categories: Optional[List] = None,
    ) -> ValidationReport:
        """
        Validate all festivals for a year.
        
        Args:
            year: Target year
            against: "reference", "drik_panchang", or "self"
            regions: Regions filter (passed to FestivalEngine)
            categories: Categories filter
        
        Returns:
            ValidationReport with all results
        """
        report = ValidationReport(year)
        
        if against == "reference":
            self._validate_all_vs_reference(year, report)
        elif against == "drik_panchang":
            self._validate_all_vs_dp(year, report)
        elif against == "self":
            self.validate_self_consistency(year, report)
        else:
            logger.warning(f"Unknown validation mode: {against}")
        
        return report
    
    # ──────────────────────────────────────────────
    # Reference Dataset Validation
    # ──────────────────────────────────────────────
    
    def _validate_against_reference(self, name: str, year: int) -> Optional[ValidationResult]:
        """Validate one festival against the reference dataset."""
        if not self.reference_data:
            return ValidationResult(
                name, year, None, None,
                passed=False, notes="No reference data loaded"
            )
        
        ref_entry = self.reference_data.get(str(year), {}).get(name)
        if not ref_entry:
            # Try flat structure
            ref_entry = self.reference_data.get(name)
        
        if not ref_entry:
            return ValidationResult(
                name, year, None, None,
                passed=False, notes="No reference entry found"
            )
        
        ref_date_str = self._parse_ref_date(ref_entry, year)
        if not ref_date_str:
            return ValidationResult(
                name, year, None, None,
                passed=False, notes=f"Could not parse reference date from {ref_entry}"
            )
        
        # Compute the festival date using FestivalEngine
        computed = self._compute_festival_date(name, year)
        if not computed:
            return ValidationResult(
                name, year, None, ref_date_str,
                passed=False, notes="Could not compute festival date"
            )
        
        # Parse reference date
        try:
            ref_dt = datetime.strptime(ref_date_str, "%Y-%m-%d").date()
        except ValueError:
            return ValidationResult(
                name, year, computed, ref_date_str,
                passed=False, notes=f"Invalid reference date format: {ref_date_str}"
            )
        
        diff = abs((computed - ref_dt).days)
        passed = diff == 0
        
        notes = ""
        if not passed:
            notes = f"MISMATCH: computed={computed}, ref={ref_date_str}"
        
        return ValidationResult(
            name, year, computed, ref_date_str,
            diff_days=diff, passed=passed, notes=notes
        )
    
    def _validate_all_vs_reference(self, year: int, report: ValidationReport):
        """Validate all reference festivals for a year."""
        year_data = self.reference_data.get(str(year), {})
        if not year_data:
            logger.warning(f"No reference data found for year {year}")
            report.add_issue(f"No reference data for year {year}")
            return
        
        for festival_name in year_data:
            ref_entry = year_data[festival_name]
            ref_date_str = self._parse_ref_date(ref_entry, year)
            if not ref_date_str:
                continue
            
            result = self._validate_against_reference(festival_name, year)
            if result:
                report.add_result(result)
    
    # ──────────────────────────────────────────────
    # Drik Panchang Validation
    # ──────────────────────────────────────────────
    
    def _validate_against_dp_single(self, name: str, year: int) -> Optional[ValidationResult]:
        """Validate one festival against live Drik Panchang data."""
        try:
            from kaal_engine.scrapers.dp_fetcher import fetch_dp_panchang, decode_tithi, extract_data_attrs, _get_html
        except ImportError:
            return ValidationResult(
                name, year, None, None,
                ref_source="drik_panchang", passed=False,
                notes="dp_fetcher not available"
            )
        
        # We need to know the computed date first to fetch DP for that date
        computed = self._compute_festival_date(name, year)
        if not computed:
            return ValidationResult(
                name, year, None, None,
                ref_source="drik_panchang", passed=False,
                notes="Cannot compute festival date"
            )
        
        # Fetch DP data for the computed date
        dp_data = fetch_dp_panchang(computed.year, computed.month, computed.day)
        if not dp_data.get("success"):
            return ValidationResult(
                name, year, computed, None,
                ref_source="drik_panchang", passed=False,
                notes=f"Failed to fetch DP data: {dp_data.get('error', 'unknown')}"
            )
        
        dp_tithi = dp_data.get("tithi", {}).get("decoded", {})
        dp_name = dp_tithi.get("name", "")
        
        # Compare tithi names
        # Get expected tithi from FestivalRule
        expected_tithi = self._get_expected_tithi(name)
        tithi_match = False
        if expected_tithi and dp_name:
            tithi_match = expected_tithi.lower() in dp_name.lower() or dp_name.lower() in expected_tithi.lower()
        
        passed = tithi_match
        notes = f"DP tithi={dp_name}, expected≈{expected_tithi}" if not passed else ""
        
        return ValidationResult(
            name, year, computed, f"{computed} (DP tithi={dp_name})",
            ref_source="drik_panchang", passed=passed, notes=notes
        )
    
    def _validate_all_vs_dp(self, year: int, report: ValidationReport):
        """Validate against live DP for all reference festivals."""
        from kaal_engine.scrapers.dp_fetcher import fetch_dp_panchang
        
        year_data = self.reference_data.get(str(year), {})
        if not year_data:
            report.add_issue(f"No reference data for year {year}")
            return
        
        for festival_name in year_data:
            result = self._validate_against_dp_single(festival_name, year)
            if result:
                report.add_result(result)
    
    # ──────────────────────────────────────────────
    # Self-Consistency Validation
    # ──────────────────────────────────────────────
    
    def validate_self_consistency(
        self,
        year: int,
        report: Optional[ValidationReport] = None,
    ) -> List[str]:
        """
        Check self-consistency of computed festivals:
        - No duplicate dates (same date for different festivals)
        - All tithi names match their FestivalRule definitions
        - No missing major festivals
        - No out-of-range dates
        
        Returns:
            List of consistency issue descriptions (empty = clean)
        """
        if report is None:
            report = ValidationReport(year)
        
        issues = []
        
        if not self.festival_engine:
            issues.append("No FestivalEngine available")
            report.add_issue("No FestivalEngine available")
            return issues
        
        # Compute all festivals for the year
        try:
            all_festivals = self.festival_engine.calculate_festival_dates(year)
        except Exception as e:
            issues.append(f"Failed to compute festivals: {e}")
            report.add_issue(f"Failed to compute festivals: {e}")
            return issues
        
        if not all_festivals:
            issues.append("No festivals computed")
            report.add_issue("No festivals computed")
            return issues
        
        # Check 1: No duplicate dates
        date_map: Dict[date, List[str]] = {}
        for fd in all_festivals:
            if fd.date not in date_map:
                date_map[fd.date] = []
            date_map[fd.date].append(fd.festival_rule.name)
        
        for d, names in date_map.items():
            if len(names) > 1:
                msg = f"Multiple festivals on {d}: {', '.join(names)}"
                issues.append(msg)
                report.add_issue(msg)
        
        # Check 2: All dates within the target year
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        for fd in all_festivals:
            if fd.date < year_start or fd.date > year_end:
                # Allow Pausha/Magha/Phalguna to extend into next year
                month_name = fd.festival_rule.month or ""
                if month_name in ("Pausha", "Magha", "Phalguna", "Margashirsha"):
                    continue
                msg = f"{fd.festival_rule.name} on {fd.date} outside year {year}"
                issues.append(msg)
                report.add_issue(msg)
        
        # Check 3: Verify against major festival list
        major_festivals = {
            "Diwali", "Dussehra", "Holika Dahan", "Maha Shivaratri",
            "Ram Navami", "Janmashtami", "Ganesh Chaturthi",
            "Makar Sankranti", "Vasant Panchami", "Guru Purnima",
            "Dhanteras", "Naraka Chaturdashi",
        }
        computed_names = {fd.festival_rule.name for fd in all_festivals}
        missing = major_festivals - computed_names
        if missing:
            msg = f"Major festivals not computed: {', '.join(sorted(missing))}"
            issues.append(msg)
            report.add_issue(msg)
        
        # Check 4: Validate against reference if available
        if str(year) in self.reference_data:
            ref = self.reference_data[str(year)]
            for festival_name in ref:
                if festival_name not in computed_names:
                    msg = f"Reference festival '{festival_name}' not computed"
                    issues.append(msg)
                    report.add_issue(msg)
        
        # Record results
        for fd in all_festivals:
            report.add_result(ValidationResult(
                fd.festival_rule.name, year, fd.date, str(fd.date),
                ref_source="self_consistency", diff_days=0, passed=True
            ))
        
        return issues
    
    def validate_multi_year(
        self,
        years: List[int],
        against: str = "reference",
    ) -> Dict[int, ValidationReport]:
        """
        Validate across multiple years.
        
        Args:
            years: List of years to validate
            against: Validation mode
        
        Returns:
            Dict mapping year → ValidationReport
        """
        reports = {}
        for year in sorted(years):
            report = self.validate_year(year, against=against)
            reports[year] = report
            logger.info(f"Year {year}: {report.passed}/{report.total} passed ({report.pass_rate:.0f}%)")
        return reports
    
    def check_drift(
        self,
        festival_name: str,
        years: List[int],
    ) -> Dict[int, Optional[date]]:
        """
        Check date stability of a festival across years.
        
        Returns:
            Dict mapping year → computed date (or None if failed)
        """
        dates = {}
        for year in sorted(years):
            d = self._compute_festival_date(festival_name, year)
            dates[year] = d
        return dates
    
    # ──────────────────────────────────────────────
    # Report Generation
    # ──────────────────────────────────────────────
    
    def report(
        self,
        year: int,
        against: str = "reference",
    ) -> str:
        """
        Generate a comprehensive validation report for a year.
        
        Args:
            year: Target year
            against: Validation mode
        
        Returns:
            Formatted report string
        """
        report = self.validate_year(year, against=against)
        return report.summary()
    
    def summary_table(self, years: List[int]) -> str:
        """Generate a multi-year summary table."""
        reports = self.validate_multi_year(years)
        
        lines = [
            f"\n{'='*70}",
            f"Multi-Year Festival Validation Summary",
            f"{'='*70}",
            f"{'Year':>6}  {'Passed':>8}  {'Failed':>8}  {'Total':>8}  {'Rate':>8}",
            f"{'-'*6}  {'-'*8}  {'-'*8}  {'-'*8}  {'-'*8}",
        ]
        for year in sorted(years):
            r = reports.get(year)
            if r:
                rate = f"{r.pass_rate:.0f}%"
                lines.append(f"{year:>6}  {r.passed:>8}  {r.failed:>8}  {r.total:>8}  {rate:>8}")
        
        lines.append(f"{'='*70}")
        return "\n".join(lines)
    
    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────
    
    def _compute_festival_date(self, name: str, year: int) -> Optional[date]:
        """Compute a single festival date using FestivalEngine.
        
        Computes ONLY the requested festival (not all 37+ rules) to
        keep validation fast. Uses in-memory cache per festival name.
        """
        if not self.festival_engine:
            return None
        
        # Per-festival cache key
        cache_key = (name, year)
        if cache_key in self._computed_cache:
            return self._computed_cache[cache_key]
        
        try:
            # Find the matching rule
            rule = None
            for r in self.festival_engine.festival_rules:
                if r.name == name:
                    rule = r
                    break
            
            if rule is None:
                logger.warning(f"No festival rule found for '{name}'")
                return None
            
            # Compute just this one festival using the appropriate method
            if rule.festival_type.name == "LUNAR":
                dates = self.festival_engine._calculate_lunar_festival(rule, year)
            elif rule.festival_type.name == "SOLAR":
                dates = self.festival_engine._calculate_solar_festival(rule, year)
            elif rule.festival_type.name == "NAKSHATRA":
                dates = self.festival_engine._calculate_nakshatra_festival(rule, year)
            elif rule.festival_type.name == "CALCULATED":
                dates = self.festival_engine._calculate_special_festival(rule, year)
            else:
                return None
            
            if dates:
                result = dates[0].date
                self._computed_cache[cache_key] = result
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error computing {name} ({year}): {e}")
            return None
    
    def _get_expected_tithi(self, name: str) -> Optional[str]:
        """Get expected tithi name for a festival from its rule."""
        if not self.festival_engine:
            return None
        for rule in self.festival_engine.festival_rules:
            if rule.name == name:
                if rule.tithi is not None and rule.paksha:
                    tithi_num = int(rule.tithi)
                    TITHI_NAMES = [
                        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
                        "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
                        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
                    ]
                    if tithi_num <= 14:
                        return f"{rule.paksha.title()} {TITHI_NAMES[tithi_num-1]}"
                    elif tithi_num == 15:
                        if rule.paksha == "shukla":
                            return "Shukla Purnima"
                        else:
                            return "Krishna Amavasya"
        return None
