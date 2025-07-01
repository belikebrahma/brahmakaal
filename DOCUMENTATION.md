# Kaal (Vedic Ephemeris Engine) Documentation

## Project Overview
Kaal is a high-precision astronomy engine for Indian calendrics using Surya Siddhanta and NASA JPL data.

## Features
- Calculates 50+ parameters: tithi, nakshatra, yoga, karana, rahu_kaal
- Supports date range: 500 BCE to 3000 CE
- Input: (latitude, longitude, elevation, datetime_utc, ayanamsha)
- Output: JSON with Vedic time units and NASA-validated positions

## Architecture
The project is structured as follows:

```
kaal_engine/
├── core/
│   ├── __init__.py
│   ├── siddhanta.py        # Surya Siddhanta algorithms
│   ├── spice_loader.py     # DE441 .bsp parser
│   └── delta_t.py          # IERS ΔT adjustments
├── geo/
│   ├── micro_adjust.py      # Elevation/refraction
│   └── nadi_zones.py        # Ancient river basin mapping
├── tests/
│   ├── test_ujjain.py       # Validate against observatory
│   └── test_eclipse.py      # 1500 BCE-2024 CE eclipses
└── kaal.py                  # Main API class
```

## Core Functionality
The main class is `Kaal` in `kaal.py`. It initializes with the path to the DE441 kernel and provides a method `get_panchang` to compute the panchang for a given location and time.

## Dependencies
- Python 3.12
- skyfield
- astropy
- geographiclib
- erfa=2.0.3

## Installation
1. Download the DE441 kernel from NASA's FTP server and place it in the `data` directory.
2. Install the dependencies: `pip install -r requirements.txt`

## Usage
```python
from kaal_engine.kaal import Kaal

# Initialize the engine with the path to the DE441 kernel
kaal = Kaal("data/de441.bsp")

# Get panchang for a specific location and time
result = kaal.get_panchang(lat=28.6139, lon=77.2090, dt=datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
print(result)
```

## Validation
The project includes unit tests and validation protocols as described in the project requirements.

Now, we will create the code files.

 Let's create each file with the initial code as provided in the user's query.

 Note: We are creating the files in the `kaal_engine` directory.

 We'll start with `kaal_engine/kaal.py`:

```python:kaal_engine/kaal.py
from datetime import datetime
from .core import spice_loader, siddhanta, delta_t
from .geo import micro_adjust

class Kaal:
    def __init__(self, de441_path: str):
        self.eph = spice_loader.load_kernel(de441_path)
        self.earth = self.eph['earth']
        self.moon = self.eph['moon']
        self.sun = self.eph['sun']
    
    def get_panchang(self, lat: float, lon: float, 
                    dt: datetime, elevation: float = 0.0, 
                    ayanamsha: str = "LAHIRI") -> dict:
        """Main API method to compute all Vedic parameters"""
        jd_utc = self._julian_day(dt)
        jd_tt = delta_t.utc_to_tt(jd_utc)
        
        # Compute base positions
        sun_long = siddhanta.mean_sun_position(jd_tt)
        moon_long = siddhanta.mean_moon_position(jd_tt)
        
        # Compute tithi and nakshatra
        tithi = self._compute_tithi(sun_long, moon_long)
        nakshatra = self._moon_nakshatra(moon_long)
        
        # Adjust sunrise for local conditions
        sunrise_jd = micro_adjust.true_sunrise(
            jd_tt, lat, lon, elevation
        )
        
        return {
            "tithi": tithi,
            "nakshatra": nakshatra,
            "sunrise": sunrise_jd,
            # ... other parameters will be added
        }
    
    def _compute_tithi(self, sun_long: float, moon_long: float) -> float:
        """Tithi = (Moon_long - Sun_long) / 12°"""
        return ((moon_long - sun_long) % 360) / 12.0
    
    def _moon_nakshatra(self, moon_long: float) -> str:
        """Nakshatra = Moon_long / 13°20'"""
        nakshatra_index = int(moon_long // (13 + 20/60))
        # We'll define the list of nakshatras
        return NAKSHATRAS[nakshatra_index]
    
    def _julian_day(self, dt: datetime) -> float:
        """Convert UTC datetime to Julian Day"""
        # Implementation based on ERFA
        # We'll use a standard method (to be implemented)
        # For now, we return a placeholder
        return 0.0

# Constants
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", 
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", 
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", 
    "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", 
    "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
```

 Next, `kaal_engine/core/siddhanta.py`:

```python:kaal_engine/core/siddhanta.py
import math

KALI_YUGA_EPOCH = 588465.5  # JD for Feb 18, 3102 BCE

def mean_sun_position(jd: float) -> float:
    """Surya Siddhanta Chapter 2, Verse 28-35"""
    days_since_epoch = jd - KALI_YUGA_EPOCH
    mean_long = (days_since_epoch * 0.98564736) % 360
    return mean_long + _equation_of_center(mean_long)

def mean_moon_position(jd: float) -> float:
    """Surya Siddhanta Chapter 1, Verse 30-34"""
    days_since_epoch = jd - KALI_YUGA_EPOCH
    mean_long = (days_since_epoch * 13.176396) % 360
    return mean_long + _lunar_equation(mean_long)

def _equation_of_center(long: float) -> float:
    """3-term sine series for equation of center"""
    rad = math.radians(long)
    return (1.914 * math.sin(rad) + 
            0.02 * math.sin(2 * rad))

def _lunar_equation(mean_long: float) -> float:
    """Equation of center for the moon (to be implemented)"""
    # Placeholder: we'll add the actual equation from Surya Siddhanta
    return 0.0

def yuga_phase(jd: float) -> dict:
    """Compute current Yuga phase per Aryabhata"""
    elapsed_days = jd - KALI_YUGA_EPOCH
    elapsed_years = elapsed_days / 365.25
    
    return {
        "maha_yuga": "Kali",
        "elapsed_years": elapsed_years,
        "sub_yuga": _compute_sub_yuga(elapsed_years)
    }

def _compute_sub_yuga(years: float) -> str:
    """Determine sub-yuga phase"""
    # Implementation based on 4:3:2:1 ratio
    # Placeholder: to be implemented
    return "Dawn Phase"
```

 Now, `kaal_engine/core/spice_loader.py`:

```python:kaal_engine/core/spice_loader.py
from skyfield.jpllib import SpiceKernel

def load_kernel(path: str) -> SpiceKernel:
    """Load DE441 kernel with error handling"""
    try:
        return SpiceKernel(path)
    except Exception as e:
        raise RuntimeError(f"Failed to load SPICE kernel: {str(e)}")

def interpolate_position(kernel: SpiceKernel, jd: float, body: str):
    """Get precise body position using NASA ephemeris"""
    # We need to create a timescale and then get the position
    # Placeholder: we'll implement this later
    return (0.0, 0.0, 0.0)
```

 Then, `kaal_engine/core/delta_t.py`:

```python:kaal_engine/core/delta_t.py
# Historical ΔT values (IERS data)
DELTA_T_TABLE = {
    -500: 17190,   # 500 BCE
    0: 10583,      # 0 CE
    500: 5700,     # 500 CE
    1000: 1570,    # 1000 CE
    1500: 200,     # 1500 CE
    2000: 64,      # 2000 CE
}

def utc_to_tt(jd_utc: float) -> float:
    """Convert UTC to Terrestrial Time"""
    delta_t = _estimate_delta_t(jd_utc)
    return jd_utc + delta_t / 86400.0

def _estimate_delta_t(jd: float) -> float:
    """Get ΔT in seconds for given Julian Day"""
    year = _jd_to_year(jd)
    # Find the two closest years in the table
    years = sorted(DELTA_T_TABLE.keys())
    # If the year is before the first entry, use the first entry
    if year < years[0]:
        return DELTA_T_TABLE[years[0]]
    # If the year is after the last entry, use the last entry
    if year > years[-1]:
        return DELTA_T_TABLE[years[-1]]
    # Otherwise, find the two closest years and interpolate
    for i in range(len(years)-1):
        y1, y2 = years[i], years[i+1]
        if y1 <= year <= y2:
            dt1 = DELTA_T_TABLE[y1]
            dt2 = DELTA_T_TABLE[y2]
            # Linear interpolation
            return dt1 + (dt2 - dt1) * (year - y1) / (y2 - y1)
    # Should not reach here
    return DELTA_T_TABLE[years[0]]

def _jd_to_year(jd: float) -> float:
    """Convert Julian Day to decimal year"""
    # This is a simplified version. We assume a constant 365.25 days per year.
    # The year 0 is defined as 1 BCE, year 1 is 1 CE.
    # We use the Julian year starting at January 1, 12:00 UTC.
    # This is not exact but sufficient for our interpolation of ΔT.
    year = (jd - 1721424.5) / 365.25
    return year
```

 Next, `kaal_engine/geo/micro_adjust.py`:

```python:kaal_engine/geo/micro_adjust.py
ATM_REFRACTION = 34 / 60  # 34 arcminutes

def true_sunrise(jd: float, lat: float, lon: float, elev: float) -> float:
    """Compute sunrise with elevation and refraction"""
    base_jd = _apparent_sunrise(jd, lat, lon)
    # Adjust for elevation: each meter of elevation adds about 0.035 seconds to sunrise
    # and refraction adds about 2 minutes (at horizon)
    # We'll combine both adjustments
    adjustment = _elevation_adjustment(elev) + _refraction_adjustment()
    return base_jd + adjustment

def _apparent_sunrise(jd: float, lat: float, lon: float) -> float:
    """Compute the apparent sunrise without adjustments"""
    # Placeholder: we'll compute the actual sunrise time using an algorithm
    return jd

def _elevation_adjustment(elev: float) -> float:
    """Time adjustment for observer elevation in days"""
    # Formula: adjustment in minutes = 0.035 * sqrt(elev) [in meters]
    # Convert to days: (minutes / (24*60)) = (0.035 * sqrt(elev)) / 1440
    if elev <= 0:
        return 0.0
    adjustment_minutes = 0.035 * (elev ** 0.5)
    return adjustment_minutes / (24 * 60)

def _refraction_adjustment() -> float:
    """Adjustment for atmospheric refraction in days"""
    # Refraction causes the sun to be seen about 34 arcminutes below the horizon.
    # This corresponds to about 2 minutes of time at the equator.
    # We return this in days: 2 minutes = 2/(24*60) days
    return 2 / (24 * 60)
```

 We also need to create `kaal_engine/geo/nadi_zones.py` (placeholder for now):

```python:kaal_engine/geo/nadi_zones.py
# This module will map ancient river basins to modern coordinates

def get_nadi_zone(lat: float, lon: float) -> str:
    """Get the ancient river basin for given coordinates"""
    # To be implemented
    return "Unknown"
```

 And the test files:

`kaal_engine/tests/test_ujjain.py`:

```python:kaal_engine/tests/test_ujjain.py
from datetime import datetime, timezone
from kaal_engine.kaal import Kaal

def test_mahashivaratri_2025():
    kaal = Kaal("data/de441.bsp")
    dt = datetime(2025, 2, 26, tzinfo=timezone.utc)
    result = kaal.get_panchang(23.1765, 75.7885, dt)  # Ujjain coords
    assert result['tithi'] == 14.0  # Krishna Chaturdashi is the 14th tithi of the dark half
    # We are not yet converting tithi index to name in the code, so we check the index
    # Also note: the sunrise time is in JD, so we need to convert to time of day for assertion
    # This test is a placeholder until we complete the implementation
```

`kaal_engine/tests/test_eclipse.py`:

```python:kaal_engine/tests/test_eclipse.py
# Placeholder for eclipse tests
```

 We also need an `__init__.py` in the core and geo directories to make them packages.

`kaal_engine/core/__init__.py` (empty for now):

```python:kaal_engine/core/__init__.py
```

`kaal_engine/geo/__init__.py` (empty for now):

```python:kaal_engine/geo/__init__.py
```

 Finally, we create the `DOCUMENTATION.md` file as described above.

 We also create a `requirements.txt`:

```text:requirements.txt
skyfield
astropy
geographiclib
erfa==2.0.3
```

 And a `.gitignore`:

```text:.gitignore
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
env/
venv/
ENV/
env.bak/
venv.bak/
*.swp
*.bak
*.tmp
*.log
data/
```

 We'll also create a `setup.py` for packaging:

```python:setup.py
from setuptools import setup, find_packages

setup(
    name='kaal_engine',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'skyfield',
        'astropy',
        'geographiclib',
        'erfa==2.0.3'
    ],
    include_package_data=True,
    package_data={
        'kaal_engine': ['data/*.bsp'],
    },
)
```

 We have now created the initial project structure and code.

 Note: The user must download the DE441 kernel and place it in `data/de441.bsp`.

 We'll output the code for each file as described.

 However, note that the user's environment is in the `kaal` directory. We are creating the `kaal_engine` package inside.

 Let's write the files.

python run_tests.py  # Run all validation tests
