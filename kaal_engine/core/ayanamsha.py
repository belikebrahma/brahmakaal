"""
Multi-Ayanamsha Engine for Brahmakaal
Supports various ayanamsha calculation systems used in Vedic astrology
"""

import math
from datetime import datetime
from typing import Dict, List, Tuple

class AyanamshaEngine:
    """
    Comprehensive ayanamsha calculation engine supporting multiple systems
    """
    
    # Supported ayanamsha systems
    SUPPORTED_SYSTEMS = {
        "LAHIRI": "Chitrapaksha Ayanamsha (Official Indian)",
        "RAMAN": "B.V. Raman Ayanamsha", 
        "KRISHNAMURTI": "Krishnamurti Paddhati (KP)",
        "YUKTESHWAR": "Sri Yukteshwar Ayanamsha",
        "SURYASIDDHANTA": "Traditional Surya Siddhanta",
        "FAGAN_BRADLEY": "Fagan-Bradley (Western Sidereal)",
        "DELUCE": "DeLuce Ayanamsha",
        "PUSHYA_PAKSHA": "Pushya Paksha Ayanamsha",
        "GALACTIC_CENTER": "Galactic Center Ayanamsha",
        "TRUE_CITRA": "True Chitrapaksha"
    }
    
    # Reference epoch and constants
    J2000_EPOCH = 2451545.0  # January 1, 2000, 12:00 TT
    TROPICAL_YEAR = 365.25636  # days
    
    # Ayanamsha rates (arcseconds per year)
    AYANAMSHA_RATES = {
        "LAHIRI": 50.29,
        "RAMAN": 50.26,
        "KRISHNAMURTI": 50.29,
        "YUKTESHWAR": 50.33,
        "SURYASIDDHANTA": 54.0,
        "FAGAN_BRADLEY": 50.25,
        "DELUCE": 50.27,
        "PUSHYA_PAKSHA": 50.29,
        "GALACTIC_CENTER": 50.29,
        "TRUE_CITRA": 50.29
    }
    
    # Reference ayanamsha values at J2000.0
    J2000_VALUES = {
        "LAHIRI": 23.85209,
        "RAMAN": 21.45292,
        "KRISHNAMURTI": 23.86388,
        "YUKTESHWAR": 22.46667,
        "SURYASIDDHANTA": 22.46157,
        "FAGAN_BRADLEY": 24.74204,
        "DELUCE": 24.02958,
        "PUSHYA_PAKSHA": 25.11667,
        "GALACTIC_CENTER": 26.96667,
        "TRUE_CITRA": 23.86289
    }
    
    def __init__(self):
        """Initialize the ayanamsha engine"""
        self.current_system = "LAHIRI"
        self._cache = {}
    
    def calculate_ayanamsha(self, jd: float, system: str = "LAHIRI") -> float:
        """
        Calculate ayanamsha for given Julian Day and system
        
        Args:
            jd: Julian Day Number (TT)
            system: Ayanamsha system to use
            
        Returns:
            Ayanamsha value in degrees
        """
        if system not in self.SUPPORTED_SYSTEMS:
            raise ValueError(f"Unsupported ayanamsha system: {system}")
        
        # Check cache
        cache_key = f"{jd}_{system}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Calculate ayanamsha
        if system == "LAHIRI":
            ayanamsha = self._calculate_lahiri(jd)
        elif system == "RAMAN":
            ayanamsha = self._calculate_raman(jd)
        elif system == "KRISHNAMURTI":
            ayanamsha = self._calculate_krishnamurti(jd)
        elif system == "YUKTESHWAR":
            ayanamsha = self._calculate_yukteshwar(jd)
        elif system == "SURYASIDDHANTA":
            ayanamsha = self._calculate_suryasiddhanta(jd)
        elif system == "FAGAN_BRADLEY":
            ayanamsha = self._calculate_fagan_bradley(jd)
        elif system == "DELUCE":
            ayanamsha = self._calculate_deluce(jd)
        elif system == "PUSHYA_PAKSHA":
            ayanamsha = self._calculate_pushya_paksha(jd)
        elif system == "GALACTIC_CENTER":
            ayanamsha = self._calculate_galactic_center(jd)
        elif system == "TRUE_CITRA":
            ayanamsha = self._calculate_true_citra(jd)
        else:
            ayanamsha = self._calculate_lahiri(jd)  # Default
        
        # Cache result
        self._cache[cache_key] = ayanamsha
        return ayanamsha
    
    def _calculate_lahiri(self, jd: float) -> float:
        """Calculate Lahiri (Chitrapaksha) ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # Lahiri's formula with modern refinements
        # Base value at J2000.0
        ayanamsha = self.J2000_VALUES["LAHIRI"]
        
        # Linear term
        ayanamsha += T * self.AYANAMSHA_RATES["LAHIRI"] / 3600.0
        
        # Higher order corrections (Lahiri's refinements)
        ayanamsha += T * T * 0.000139 / 3600.0
        ayanamsha += T * T * T * 0.0000002 / 3600.0
        
        return ayanamsha
    
    def _calculate_raman(self, jd: float) -> float:
        """Calculate B.V. Raman ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # Raman's formula
        ayanamsha = self.J2000_VALUES["RAMAN"]
        ayanamsha += T * self.AYANAMSHA_RATES["RAMAN"] / 3600.0
        
        return ayanamsha
    
    def _calculate_krishnamurti(self, jd: float) -> float:
        """Calculate Krishnamurti Paddhati (KP) ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # KP ayanamsha (very close to Lahiri with slight variations)
        ayanamsha = self.J2000_VALUES["KRISHNAMURTI"]
        ayanamsha += T * self.AYANAMSHA_RATES["KRISHNAMURTI"] / 3600.0
        
        # KP specific adjustments
        ayanamsha += T * T * 0.000144 / 3600.0
        
        return ayanamsha
    
    def _calculate_yukteshwar(self, jd: float) -> float:
        """Calculate Sri Yukteshwar ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # Yukteshwar's calculation based on his holy science
        ayanamsha = self.J2000_VALUES["YUKTESHWAR"]
        ayanamsha += T * self.AYANAMSHA_RATES["YUKTESHWAR"] / 3600.0
        
        return ayanamsha
    
    def _calculate_suryasiddhanta(self, jd: float) -> float:
        """Calculate traditional Surya Siddhanta ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # Traditional calculation with higher rate
        ayanamsha = self.J2000_VALUES["SURYASIDDHANTA"]
        ayanamsha += T * self.AYANAMSHA_RATES["SURYASIDDHANTA"] / 3600.0
        
        return ayanamsha
    
    def _calculate_fagan_bradley(self, jd: float) -> float:
        """Calculate Fagan-Bradley ayanamsha (Western sidereal)"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # Fagan-Bradley formula
        ayanamsha = self.J2000_VALUES["FAGAN_BRADLEY"]
        ayanamsha += T * self.AYANAMSHA_RATES["FAGAN_BRADLEY"] / 3600.0
        
        return ayanamsha
    
    def _calculate_deluce(self, jd: float) -> float:
        """Calculate DeLuce ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        ayanamsha = self.J2000_VALUES["DELUCE"]
        ayanamsha += T * self.AYANAMSHA_RATES["DELUCE"] / 3600.0
        
        return ayanamsha
    
    def _calculate_pushya_paksha(self, jd: float) -> float:
        """Calculate Pushya Paksha ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        ayanamsha = self.J2000_VALUES["PUSHYA_PAKSHA"]
        ayanamsha += T * self.AYANAMSHA_RATES["PUSHYA_PAKSHA"] / 3600.0
        
        return ayanamsha
    
    def _calculate_galactic_center(self, jd: float) -> float:
        """Calculate Galactic Center ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        ayanamsha = self.J2000_VALUES["GALACTIC_CENTER"]
        ayanamsha += T * self.AYANAMSHA_RATES["GALACTIC_CENTER"] / 3600.0
        
        return ayanamsha
    
    def _calculate_true_citra(self, jd: float) -> float:
        """Calculate True Chitrapaksha ayanamsha"""
        T = (jd - self.J2000_EPOCH) / 36525.0
        
        # True Citra based on actual star position
        ayanamsha = self.J2000_VALUES["TRUE_CITRA"]
        ayanamsha += T * self.AYANAMSHA_RATES["TRUE_CITRA"] / 3600.0
        
        # Additional correction for proper motion of Spica
        ayanamsha += T * 0.000035 / 3600.0
        
        return ayanamsha
    
    def tropical_to_sidereal(self, tropical_long: float, jd: float, system: str = "LAHIRI") -> float:
        """
        Convert tropical longitude to sidereal longitude
        
        Args:
            tropical_long: Tropical longitude in degrees
            jd: Julian Day Number
            system: Ayanamsha system to use
            
        Returns:
            Sidereal longitude in degrees
        """
        ayanamsha = self.calculate_ayanamsha(jd, system)
        sidereal_long = (tropical_long - ayanamsha) % 360
        return sidereal_long
    
    def sidereal_to_tropical(self, sidereal_long: float, jd: float, system: str = "LAHIRI") -> float:
        """
        Convert sidereal longitude to tropical longitude
        
        Args:
            sidereal_long: Sidereal longitude in degrees
            jd: Julian Day Number
            system: Ayanamsha system to use
            
        Returns:
            Tropical longitude in degrees
        """
        ayanamsha = self.calculate_ayanamsha(jd, system)
        tropical_long = (sidereal_long + ayanamsha) % 360
        return tropical_long
    
    def compare_systems(self, jd: float) -> Dict[str, float]:
        """
        Compare all ayanamsha systems for a given date
        
        Args:
            jd: Julian Day Number
            
        Returns:
            Dictionary of system names and their ayanamsha values
        """
        comparisons = {}
        for system in self.SUPPORTED_SYSTEMS.keys():
            comparisons[system] = self.calculate_ayanamsha(jd, system)
        
        return comparisons
    
    def get_system_info(self, system: str) -> Dict[str, any]:
        """
        Get detailed information about an ayanamsha system
        
        Args:
            system: Ayanamsha system name
            
        Returns:
            Dictionary with system information
        """
        if system not in self.SUPPORTED_SYSTEMS:
            raise ValueError(f"Unknown ayanamsha system: {system}")
        
        return {
            "name": system,
            "description": self.SUPPORTED_SYSTEMS[system],
            "j2000_value": self.J2000_VALUES[system],
            "annual_rate": self.AYANAMSHA_RATES[system],
            "annual_rate_degrees": self.AYANAMSHA_RATES[system] / 3600.0
        }
    
    def calculate_difference(self, jd: float, system1: str, system2: str) -> float:
        """
        Calculate difference between two ayanamsha systems
        
        Args:
            jd: Julian Day Number
            system1: First ayanamsha system
            system2: Second ayanamsha system
            
        Returns:
            Difference in degrees (system1 - system2)
        """
        ayanamsha1 = self.calculate_ayanamsha(jd, system1)
        ayanamsha2 = self.calculate_ayanamsha(jd, system2)
        
        return ayanamsha1 - ayanamsha2
    
    def get_historical_values(self, system: str, start_year: int, end_year: int, step: int = 10) -> List[Tuple[int, float]]:
        """
        Get historical ayanamsha values for a system
        
        Args:
            system: Ayanamsha system
            start_year: Starting year (CE)
            end_year: Ending year (CE)
            step: Year step size
            
        Returns:
            List of (year, ayanamsha_value) tuples
        """
        if system not in self.SUPPORTED_SYSTEMS:
            raise ValueError(f"Unknown ayanamsha system: {system}")
        
        values = []
        for year in range(start_year, end_year + 1, step):
            # Convert year to Julian Day (January 1 of that year)
            jd = self._year_to_jd(year)
            ayanamsha = self.calculate_ayanamsha(jd, system)
            values.append((year, round(ayanamsha, 4)))
        
        return values
    
    def _year_to_jd(self, year: int) -> float:
        """Convert year to Julian Day for January 1, 12:00 UT"""
        # Simplified conversion - in practice, would use more precise algorithms
        if year >= 1583:  # Gregorian calendar
            a = (14 - 1) // 12
            y = year + 4800 - a
            m = 1 + 12 * a - 3
            jd = 1 + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        else:  # Julian calendar
            a = (14 - 1) // 12
            y = year + 4800 - a
            m = 1 + 12 * a - 3
            jd = 1 + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
        
        return float(jd - 0.5)  # Convert to JD at noon
    
    def validate_system(self, system: str) -> bool:
        """
        Validate if an ayanamsha system is supported
        
        Args:
            system: Ayanamsha system name
            
        Returns:
            True if supported, False otherwise
        """
        return system in self.SUPPORTED_SYSTEMS
    
    def clear_cache(self):
        """Clear the calculation cache"""
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """Get current cache size"""
        return len(self._cache)

# Convenience functions for common operations
def get_lahiri_ayanamsha(jd: float) -> float:
    """Quick function to get Lahiri ayanamsha"""
    engine = AyanamshaEngine()
    return engine.calculate_ayanamsha(jd, "LAHIRI")

def get_raman_ayanamsha(jd: float) -> float:
    """Quick function to get Raman ayanamsha"""
    engine = AyanamshaEngine()
    return engine.calculate_ayanamsha(jd, "RAMAN")

def tropical_to_sidereal_lahiri(tropical_long: float, jd: float) -> float:
    """Quick conversion using Lahiri ayanamsha"""
    engine = AyanamshaEngine()
    return engine.tropical_to_sidereal(tropical_long, jd, "LAHIRI")

def compare_all_ayanamshas(jd: float) -> Dict[str, float]:
    """Quick comparison of all ayanamsha systems"""
    engine = AyanamshaEngine()
    return engine.compare_systems(jd) 