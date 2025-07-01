import math

KALI_YUGA_EPOCH = 588465.5  # JD for Feb 18, 3102 BCE

def mean_sun_position(jd: float) -> float:
    days_since_epoch = jd - KALI_YUGA_EPOCH
    mean_long = (days_since_epoch * 0.98564736) % 360
    return mean_long + _equation_of_center(mean_long)

def mean_moon_position(jd: float) -> float:
    days_since_epoch = jd - KALI_YUGA_EPOCH
    mean_long = (days_since_epoch * 13.176396) % 360
    return mean_long + _lunar_equation(mean_long)

def _equation_of_center(long: float) -> float:
    rad = math.radians(long)
    return (1.914 * math.sin(rad) + 0.02 * math.sin(2 * rad))

def _lunar_equation(mean_long: float) -> float:
    # Placeholder for lunar equation
    return 0.0

def yuga_phase(jd: float) -> dict:
    elapsed_days = jd - KALI_YUGA_EPOCH
    elapsed_years = elapsed_days / 365.25
    return {
        "maha_yuga": "Kali",
        "elapsed_years": elapsed_years,
        "sub_yuga": _compute_sub_yuga(elapsed_years)
    }

def _compute_sub_yuga(years: float) -> str:
    # Placeholder for sub-yuga calculation
    return "Dawn Phase"