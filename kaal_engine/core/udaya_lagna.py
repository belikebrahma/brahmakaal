"""
Udaya Lagna Engine - Rising Sign Calculations
Calculates the 12 rising sign periods throughout the day matching Drik Panchang
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import math


class UdayaLagnaEngine:
    """
    Udaya Lagna calculation engine providing rising sign periods throughout the day
    """
    
    def __init__(self):
        # Rashi (zodiac signs) with their characteristics
        self.rashi_data = {
            "Mesha": {
                "name": "Aries",
                "element": "Fire",
                "lord": "Mars", 
                "favorable_activities": ["New beginnings", "Leadership", "Sports", "Adventure", "Military matters"],
                "avoid_activities": ["Patience-requiring tasks", "Diplomatic negotiations"],
                "nature": "Movable",
                "guna": "Rajas"
            },
            "Vrishabha": {
                "name": "Taurus", 
                "element": "Earth",
                "lord": "Venus",
                "favorable_activities": ["Financial matters", "Art", "Beauty", "Agriculture", "Luxury goods"],
                "avoid_activities": ["Hasty decisions", "Major changes"],
                "nature": "Fixed",
                "guna": "Rajas"
            },
            "Mithuna": {
                "name": "Gemini",
                "element": "Air", 
                "lord": "Mercury",
                "favorable_activities": ["Communication", "Writing", "Travel", "Learning", "Trade"],
                "avoid_activities": ["Long-term commitments", "Concentration-heavy work"],
                "nature": "Dual",
                "guna": "Rajas"
            },
            "Karka": {
                "name": "Cancer",
                "element": "Water",
                "lord": "Moon",
                "favorable_activities": ["Home matters", "Family", "Emotions", "Nurturing", "Water-related work"],
                "avoid_activities": ["Harsh negotiations", "Aggressive actions"],
                "nature": "Movable", 
                "guna": "Sattva"
            },
            "Simha": {
                "name": "Leo",
                "element": "Fire",
                "lord": "Sun",
                "favorable_activities": ["Authority", "Government", "Royal matters", "Entertainment", "Creativity"],
                "avoid_activities": ["Submissive roles", "Background work"],
                "nature": "Fixed",
                "guna": "Sattva"
            },
            "Kanya": {
                "name": "Virgo", 
                "element": "Earth",
                "lord": "Mercury",
                "favorable_activities": ["Details", "Analysis", "Health", "Service", "Organization"],
                "avoid_activities": ["Grand gestures", "Big investments"],
                "nature": "Dual",
                "guna": "Rajas"
            },
            "Tula": {
                "name": "Libra",
                "element": "Air",
                "lord": "Venus", 
                "favorable_activities": ["Partnerships", "Justice", "Art", "Diplomacy", "Marriage"],
                "avoid_activities": ["Solitary work", "Harsh decisions"],
                "nature": "Movable",
                "guna": "Rajas"
            },
            "Vrishchika": {
                "name": "Scorpio",
                "element": "Water",
                "lord": "Mars",
                "favorable_activities": ["Research", "Investigation", "Transformation", "Occult", "Surgery"],
                "avoid_activities": ["Surface-level work", "Public exposure"],
                "nature": "Fixed",
                "guna": "Tamas"
            },
            "Dhanu": {
                "name": "Sagittarius",
                "element": "Fire", 
                "lord": "Jupiter",
                "favorable_activities": ["Education", "Philosophy", "Religion", "Long distance", "Publishing"],
                "avoid_activities": ["Mundane tasks", "Routine work"],
                "nature": "Dual",
                "guna": "Sattva"
            },
            "Makara": {
                "name": "Capricorn",
                "element": "Earth",
                "lord": "Saturn",
                "favorable_activities": ["Structure", "Organization", "Government", "Elder matters", "Persistence"],
                "avoid_activities": ["Hasty actions", "Emotional decisions"],
                "nature": "Movable",
                "guna": "Tamas"
            },
            "Kumbha": {
                "name": "Aquarius",
                "element": "Air",
                "lord": "Saturn",
                "favorable_activities": ["Innovation", "Technology", "Groups", "Humanitarian work", "Future planning"],
                "avoid_activities": ["Traditional methods", "Conservative approaches"],
                "nature": "Fixed", 
                "guna": "Tamas"
            },
            "Meena": {
                "name": "Pisces",
                "element": "Water",
                "lord": "Jupiter",
                "favorable_activities": ["Spirituality", "Charity", "Arts", "Intuition", "Healing"],
                "avoid_activities": ["Practical planning", "Aggressive business"],
                "nature": "Dual",
                "guna": "Sattva"
            }
        }
        
        # Rashi sequence in zodiacal order
        self.rashi_sequence = [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
        ]
    
    def calculate_udaya_lagna_periods(self, date: datetime, sunrise: datetime, sunset: datetime,
                                    location: Dict[str, float], sun_longitude: float) -> List[Dict[str, Any]]:
        """
        Calculate rising sign periods throughout the day
        
        Args:
            date: Date for calculation
            sunrise: Sunrise time
            sunset: Sunset time
            location: Location data with latitude, longitude
            sun_longitude: Sun's longitude in degrees
            
        Returns:
            List of 12 rising sign periods with timing and characteristics
        """
        periods = []
        
        # Calculate day and night durations
        day_duration = sunset - sunrise
        total_day_hours = 24
        
        # Each rashi rises for approximately 2 hours (720 minutes / 12 = 60 minutes base)
        # But this varies based on latitude and season
        base_period_minutes = 120  # 2 hours base
        
        # Get the rising sign at sunrise (Udaya Lagna)
        sunrise_lagna = self._calculate_lagna_at_time(sunrise, location, sun_longitude)
        
        # Start from 24 hours before sunrise for complete day cycle
        start_time = sunrise - timedelta(hours=6)  # Start 6 hours before sunrise
        current_time = start_time
        
        # Calculate periods for all 12 rashis
        for i in range(12):
            # Determine current rashi
            rashi_index = (self.rashi_sequence.index(sunrise_lagna) + i) % 12
            current_rashi = self.rashi_sequence[rashi_index]
            
            # Calculate period duration with astronomical adjustments
            period_duration = self._calculate_rashi_duration(
                current_time, location, current_rashi, day_duration
            )
            
            period_end = current_time + period_duration
            
            # Create period data
            period_data = {
                "rashi": current_rashi,
                "rashi_name": self.rashi_data[current_rashi]["name"],
                "start": current_time,
                "end": period_end,
                "duration_minutes": int(period_duration.total_seconds() / 60),
                "is_day_period": sunrise <= current_time < sunset,
                **self.rashi_data[current_rashi]
            }
            
            periods.append(period_data)
            current_time = period_end
            
            # Stop when we've covered 24 hours or have 12 periods
            if len(periods) >= 12:
                break
        
        return periods
    
    def _calculate_lagna_at_time(self, time: datetime, location: Dict[str, float], 
                                sun_longitude: float) -> str:
        """
        Calculate the rising sign (lagna) at a specific time
        """
        # This is a simplified calculation - in reality this requires complex astronomical calculations
        # For now, we'll use an approximation based on sun position and time
        
        latitude = location.get('latitude', 0)
        
        # Calculate approximate lagna based on sun's longitude and time
        # Each rashi spans 30 degrees, so we can determine which rashi is rising
        
        # Hours since midnight
        hours_since_midnight = time.hour + time.minute / 60.0
        
        # Approximate adjustment for latitude (higher latitudes have longer/shorter ascension times)
        latitude_factor = 1.0 + (abs(latitude) / 90.0) * 0.3
        
        # Calculate which rashi is rising
        # This is a simplified model - real calculation requires sidereal time, obliquity, etc.
        rising_offset = (hours_since_midnight * latitude_factor) % 12
        
        # Start from the rashi where sun is (approximately)
        sun_rashi_index = int(sun_longitude / 30) % 12
        rising_rashi_index = (sun_rashi_index + int(rising_offset)) % 12
        
        return self.rashi_sequence[rising_rashi_index]
    
    def _calculate_rashi_duration(self, current_time: datetime, location: Dict[str, float],
                                 rashi: str, day_duration: timedelta) -> timedelta:
        """
        Calculate the duration for which a rashi rises
        """
        latitude = location.get('latitude', 0)
        
        # Base duration is 2 hours
        base_duration = timedelta(hours=2)
        
        # Adjustments based on rashi characteristics and location
        rashi_info = self.rashi_data[rashi]
        
        # Movable signs rise faster, Fixed signs rise slower, Dual signs are medium
        nature_factor = {
            "Movable": 0.9,    # 10% faster
            "Fixed": 1.1,      # 10% slower  
            "Dual": 1.0        # Normal
        }.get(rashi_info["nature"], 1.0)
        
        # Latitude effect - higher latitudes have more variation
        latitude_factor = 1.0 + (abs(latitude) / 90.0) * 0.2
        
        # Time of day effect - dawn/dusk periods are different
        hour = current_time.hour
        if 5 <= hour <= 7 or 17 <= hour <= 19:
            time_factor = 0.9  # Shorter during transition periods
        elif 22 <= hour or hour <= 4:
            time_factor = 1.1  # Longer during night
        else:
            time_factor = 1.0
        
        # Apply all factors
        adjustment_factor = nature_factor * latitude_factor * time_factor
        adjusted_duration = base_duration * adjustment_factor
        
        # Ensure reasonable bounds (1 hour to 3 hours)
        min_duration = timedelta(hours=1)
        max_duration = timedelta(hours=3)
        
        return max(min_duration, min(max_duration, adjusted_duration))
    
    def get_current_udaya_lagna(self, periods: List[Dict[str, Any]], 
                              current_time: datetime) -> Dict[str, Any]:
        """
        Get the current rising sign for the given time
        """
        for period in periods:
            if period['start'] <= current_time <= period['end']:
                return period
        
        # If no period found, return first period as default
        return periods[0] if periods else {
            "rashi": "Mesha",
            "rashi_name": "Aries",
            "start": current_time,
            "end": current_time + timedelta(hours=2),
            **self.rashi_data["Mesha"]
        }
    
    def get_most_favorable_periods(self, periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get the most favorable rising sign periods for important activities
        """
        # Beneficial rashis for most activities
        favorable_rashis = ["Vrishabha", "Mithuna", "Simha", "Kanya", "Tula", "Dhanu"]
        
        favorable_periods = []
        for period in periods:
            if period['rashi'] in favorable_rashis:
                favorable_periods.append(period)
        
        return favorable_periods
    
    def get_rashi_compatibility(self, rashi1: str, rashi2: str) -> Dict[str, Any]:
        """
        Get compatibility between two rashis
        """
        # This is a simplified compatibility system
        # In reality, this involves complex astrological rules
        
        elements = {
            rashi1: self.rashi_data[rashi1]["element"],
            rashi2: self.rashi_data[rashi2]["element"]
        }
        
        # Same element is generally compatible
        if elements[rashi1] == elements[rashi2]:
            compatibility = "High"
            description = f"Both {elements[rashi1]} signs - natural harmony"
        elif (elements[rashi1] == "Fire" and elements[rashi2] == "Air") or \
             (elements[rashi1] == "Air" and elements[rashi2] == "Fire"):
            compatibility = "Excellent" 
            description = "Fire and Air combination - mutual support"
        elif (elements[rashi1] == "Earth" and elements[rashi2] == "Water") or \
             (elements[rashi1] == "Water" and elements[rashi2] == "Earth"):
            compatibility = "Good"
            description = "Earth and Water combination - stable foundation"
        else:
            compatibility = "Moderate"
            description = "Different elements - requires adjustment"
        
        return {
            "compatibility": compatibility,
            "description": description,
            "elements": elements
        } 