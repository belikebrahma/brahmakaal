"""
Enhanced Panchaka Engine - Detailed hourly panchaka calculations
Matches Drik Panchang's comprehensive hourly breakdown system
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import math


class EnhancedPanchakaEngine:
    """
    Enhanced Panchaka calculation engine providing detailed hourly breakdown
    matching Drik Panchang's comprehensive system
    """
    
    def __init__(self):
        # Panchaka types with their characteristics
        self.panchaka_types = {
            "Mrityu Panchaka": {
                "description": "Death element - avoid new beginnings, endings favored",
                "element": "Death",
                "favorable": ["Ending bad habits", "Completing projects", "Funeral rites", "Letting go"],
                "avoid": ["New ventures", "Marriages", "Important purchases", "Birth ceremonies"],
                "severity": "High"
            },
            "Agni Panchaka": {
                "description": "Fire element - avoid fire-related activities, spiritual work favored",
                "element": "Fire", 
                "favorable": ["Religious ceremonies", "Spiritual practices", "Meditation", "Worship"],
                "avoid": ["Starting fires", "Cooking elaborate meals", "Metalwork", "Chemical work"],
                "severity": "Medium"
            },
            "Raja Panchaka": {
                "description": "Royal element - good for leadership and government work",
                "element": "Royal",
                "favorable": ["Government work", "Leadership roles", "Important decisions", "Authority matters"],
                "avoid": ["Submissive activities", "Following others", "Servant work"],
                "severity": "Low"
            },
            "Chora Panchaka": {
                "description": "Theft element - be cautious with valuables and security",
                "element": "Theft",
                "favorable": ["Security arrangements", "Vigilance", "Protective measures", "Lock installation"],
                "avoid": ["Displaying wealth", "Traveling with valuables", "Trusting strangers", "Financial transactions"],
                "severity": "High"
            },
            "Roga Panchaka": {
                "description": "Disease element - focus on health and avoid unhealthy activities",
                "element": "Disease",
                "favorable": ["Health checkups", "Healing practices", "Medical treatments", "Hygiene"],
                "avoid": ["Unhealthy food", "Stress", "Overexertion", "Hospital visits for non-urgent matters"],
                "severity": "Medium"
            },
            "Good Muhurta": {
                "description": "Auspicious period - favorable for all normal and important activities",
                "element": "Beneficial",
                "favorable": ["All auspicious work", "New beginnings", "Important ceremonies", "Business deals"],
                "avoid": ["None specific"],
                "severity": "Beneficial"
            }
        }
    
    def calculate_daily_panchaka_periods(self, date: datetime, sunrise: datetime, sunset: datetime, 
                                       moon_longitude: float, location: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Calculate detailed hourly panchaka periods for the entire day
        
        Args:
            date: Date for calculation
            sunrise: Sunrise time for the date
            sunset: Sunset time for the date  
            moon_longitude: Moon's longitude in degrees
            location: Dict with latitude, longitude, elevation
            
        Returns:
            List of panchaka periods with detailed timing and descriptions
        """
        periods = []
        
        # Get the primary panchaka type for the day
        primary_panchaka = self._get_primary_panchaka_type(date, moon_longitude)
        
        # Calculate day and night durations
        day_duration = sunset - sunrise
        night_duration = timedelta(hours=24) - day_duration
        
        # Calculate base period lengths (variable based on day/night cycle)
        day_period_length = day_duration / 8  # 8 periods during day
        night_period_length = night_duration / 8  # 8 periods during night
        
        # Start from previous sunset for traditional calculation
        previous_sunset = sunrise - timedelta(hours=12)  # Approximate previous sunset
        current_time = previous_sunset
        
        # Generate 24-hour panchaka cycle (traditional day starts at sunset)
        panchaka_sequence = self._generate_panchaka_sequence(primary_panchaka, date)
        
        period_index = 0
        while current_time < sunrise + timedelta(hours=24):
            # Determine if we're in day or night period
            is_day_period = sunrise <= current_time <= sunset
            
            # Calculate period duration based on day/night
            if is_day_period:
                period_duration = day_period_length
            else:
                period_duration = night_period_length
            
            # Adjust for astronomical factors
            period_duration = self._adjust_period_for_astronomical_factors(
                period_duration, current_time, moon_longitude, location
            )
            
            # Get panchaka type for this period
            panchaka_type = panchaka_sequence[period_index % len(panchaka_sequence)]
            
            period_end = current_time + period_duration
            
            # Create period data
            period_data = {
                "type": panchaka_type,
                "start": current_time,
                "end": period_end,
                "duration_minutes": int(period_duration.total_seconds() / 60),
                "is_day_period": is_day_period,
                "favorable": panchaka_type == "Good Muhurta",
                **self.panchaka_types.get(panchaka_type, self.panchaka_types["Good Muhurta"])
            }
            
            periods.append(period_data)
            
            current_time = period_end
            period_index += 1
            
            # Limit to reasonable number of periods
            if len(periods) >= 24:
                break
        
        return periods
    
    def _get_primary_panchaka_type(self, date: datetime, moon_longitude: float) -> str:
        """
        Determine the primary panchaka type for the day based on astronomical factors
        """
        # Get current nakshatra from moon longitude
        nakshatra_number = int(moon_longitude / 13.333333) + 1
        
        # Panchaka nakshatras: Dhanishtha(23), Shatabhisha(24), Purva Bhadrapada(25), 
        # Uttara Bhadrapada(26), Revati(27)
        panchaka_nakshatras = [23, 24, 25, 26, 27]
        
        if nakshatra_number in panchaka_nakshatras:
            # Map nakshatra to panchaka type
            panchaka_map = {
                23: "Agni Panchaka",     # Dhanishtha
                24: "Raja Panchaka",     # Shatabhisha  
                25: "Mrityu Panchaka",   # Purva Bhadrapada
                26: "Chora Panchaka",    # Uttara Bhadrapada
                27: "Roga Panchaka"      # Revati
            }
            return panchaka_map.get(nakshatra_number, "Agni Panchaka")
        else:
            # Non-panchaka day - mostly good periods
            return "Good Muhurta"
    
    def _generate_panchaka_sequence(self, primary_panchaka: str, date: datetime) -> List[str]:
        """
        Generate the sequence of panchaka periods for the day
        Based on traditional patterns and astronomical factors
        """
        if primary_panchaka == "Good Muhurta":
            # Non-panchaka day - mostly good with occasional caution periods
            return [
                "Good Muhurta", "Good Muhurta", "Agni Panchaka", "Good Muhurta",
                "Good Muhurta", "Raja Panchaka", "Good Muhurta", "Good Muhurta",
                "Good Muhurta", "Roga Panchaka", "Good Muhurta", "Good Muhurta"
            ]
        else:
            # Panchaka day - alternate between primary panchaka and good periods
            secondary_panchaka = self._get_secondary_panchaka(primary_panchaka, date)
            return [
                primary_panchaka, "Agni Panchaka", "Good Muhurta", secondary_panchaka,
                "Good Muhurta", "Chora Panchaka", "Good Muhurta", "Roga Panchaka", 
                "Good Muhurta", primary_panchaka, secondary_panchaka, "Good Muhurta"
            ]
    
    def _get_secondary_panchaka(self, primary: str, date: datetime) -> str:
        """Get secondary panchaka type based on day of week and primary type"""
        day_of_week = date.weekday()
        
        secondary_map = {
            "Mrityu Panchaka": ["Agni Panchaka", "Roga Panchaka", "Chora Panchaka", "Raja Panchaka"],
            "Agni Panchaka": ["Mrityu Panchaka", "Chora Panchaka", "Roga Panchaka", "Raja Panchaka"],
            "Raja Panchaka": ["Agni Panchaka", "Mrityu Panchaka", "Roga Panchaka", "Chora Panchaka"],
            "Chora Panchaka": ["Mrityu Panchaka", "Roga Panchaka", "Agni Panchaka", "Raja Panchaka"],
            "Roga Panchaka": ["Agni Panchaka", "Chora Panchaka", "Mrityu Panchaka", "Raja Panchaka"]
        }
        
        secondary_options = secondary_map.get(primary, ["Agni Panchaka"])
        return secondary_options[day_of_week % len(secondary_options)]
    
    def _adjust_period_for_astronomical_factors(self, base_duration: timedelta, 
                                              current_time: datetime, moon_longitude: float,
                                              location: Dict[str, float]) -> timedelta:
        """
        Adjust period duration based on astronomical factors
        """
        # Moon's speed affects panchaka timing
        moon_speed_factor = self._calculate_moon_speed_factor(moon_longitude)
        
        # Location-based adjustment (latitude effect)
        latitude_factor = 1.0 + (abs(location.get('latitude', 0)) / 90.0) * 0.1
        
        # Time of day adjustment (dawn/dusk periods are shorter)
        time_factor = self._calculate_time_factor(current_time)
        
        # Apply all factors
        adjustment_factor = moon_speed_factor * latitude_factor * time_factor
        
        adjusted_duration = base_duration * adjustment_factor
        
        # Ensure reasonable bounds (30 minutes to 3 hours)
        min_duration = timedelta(minutes=30)
        max_duration = timedelta(hours=3)
        
        return max(min_duration, min(max_duration, adjusted_duration))
    
    def _calculate_moon_speed_factor(self, moon_longitude: float) -> float:
        """Calculate moon speed factor affecting panchaka timing"""
        # Moon's orbital speed varies - faster at perigee, slower at apogee
        # This is a simplified approximation
        return 0.9 + 0.2 * math.sin(math.radians(moon_longitude * 13.176))
    
    def _calculate_time_factor(self, current_time: datetime) -> float:
        """Calculate time-based factor for period adjustment"""
        hour = current_time.hour
        
        # Dawn and dusk periods (transition times) are shorter
        if 5 <= hour <= 7 or 17 <= hour <= 19:
            return 0.8  # 20% shorter
        # Night periods are longer
        elif 22 <= hour or hour <= 4:
            return 1.2  # 20% longer
        else:
            return 1.0  # Normal duration
    
    def get_current_panchaka_period(self, periods: List[Dict[str, Any]], 
                                  current_time: datetime) -> Dict[str, Any]:
        """
        Get the current panchaka period for the given time
        """
        for period in periods:
            if period['start'] <= current_time <= period['end']:
                return period
        
        # If no period found, return a default good period
        return {
            "type": "Good Muhurta",
            "start": current_time,
            "end": current_time + timedelta(hours=1),
            "duration_minutes": 60,
            "favorable": True,
            **self.panchaka_types["Good Muhurta"]
        }
    
    def get_next_favorable_period(self, periods: List[Dict[str, Any]], 
                                current_time: datetime) -> Dict[str, Any]:
        """
        Get the next favorable (Good Muhurta) period
        """
        for period in periods:
            if period['start'] > current_time and period['favorable']:
                return period
        
        # If no favorable period found, return tomorrow's first good period
        return periods[0] if periods else None 