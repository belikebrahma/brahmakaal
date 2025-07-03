"""
Traditional Vedic Panchang Enhancements for Brahmakaal
Implements missing traditional features: Tarabala, Chandrabala, Shool direction, 
Panchaka classification, traditional calendar years, and end times
"""

from datetime import datetime, timedelta
import math
from typing import Dict, Any

class PanchangEnhancements:
    """
    Enhanced traditional Vedic panchang calculations
    """
    
    def __init__(self):
        # Nakshatra names for reference
        self.nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
            "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
            "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
            "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha",
            "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
    
    def calculate_tithi_end_time(self, sun_long: float, moon_long: float, jd_tt: float) -> Dict[str, Any]:
        """Calculate exact end time for current tithi"""
        current_tithi = ((moon_long - sun_long) % 360) / 12.0
        next_tithi_target = math.ceil(current_tithi)
        
        # Calculate how much tithi has progressed (0-1)
        progress = current_tithi % 1
        remaining_fraction = 1 - progress
        
        # Average tithi duration is about 23.62 hours
        average_tithi_duration_hours = 23.62
        remaining_hours = remaining_fraction * average_tithi_duration_hours
        
        # Calculate end time
        base_time = datetime.utcfromtimestamp((jd_tt - 2440587.5) * 86400)
        end_time = base_time + timedelta(hours=remaining_hours)
        
        return {
            "end_time": end_time,
            "hours_remaining": int(remaining_hours),
            "minutes_remaining": int((remaining_hours % 1) * 60),
            "percentage_complete": round(progress * 100, 1)
        }
    
    def calculate_nakshatra_end_time(self, moon_long: float, jd_tt: float) -> Dict[str, Any]:
        """Calculate exact end time for current nakshatra"""
        # Each nakshatra spans 13.333... degrees (360/27)
        nakshatra_span = 360.0 / 27.0
        current_nakshatra_position = moon_long % nakshatra_span
        progress = current_nakshatra_position / nakshatra_span
        
        # Average moon motion is about 13.2 degrees per day
        moon_daily_motion = 13.2
        remaining_degrees = nakshatra_span - current_nakshatra_position
        remaining_hours = (remaining_degrees / moon_daily_motion) * 24
        
        # Calculate end time
        base_time = datetime.utcfromtimestamp((jd_tt - 2440587.5) * 86400)
        end_time = base_time + timedelta(hours=remaining_hours)
        
        return {
            "end_time": end_time,
            "hours_remaining": int(remaining_hours),
            "minutes_remaining": int((remaining_hours % 1) * 60),
            "percentage_complete": round(progress * 100, 1)
        }
    
    def calculate_traditional_years(self, dt: datetime) -> Dict[str, Any]:
        """Calculate traditional Hindu calendar years"""
        year = dt.year
        
        # Vikram Samvat (starts around April, so add 57 for most of the year)
        if dt.month >= 4:
            vikram_samvat = year + 57
        else:
            vikram_samvat = year + 56
        
        # Shaka Samvat (starts around March/April, subtract 78)
        if dt.month >= 3:
            shaka_samvat = year - 78
        else:
            shaka_samvat = year - 79
        
        # Kali Yuga year (add 3102 to CE year)
        kali_yuga = year + 3102
        
        # Bengali San (starts around April, subtract 593)
        if dt.month >= 4:
            bengali_san = year - 593
        else:
            bengali_san = year - 594
        
        # Tamil year names cycle (60-year cycle)
        tamil_years = [
            "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati", "Angirasa", "Shrimukha", "Bhava",
            "Yuva", "Dhata", "Ishvara", "Bahudhanya", "Pramadi", "Vikrama", "Vrusha", "Chitrabhanu",
            "Svabhanu", "Tarana", "Parthiva", "Vyaya", "Sarvajeeth", "Sarvadhadi", "Virodhi", "Vikrita",
            "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi", "Hemalamba", "Vilamba",
            "Vikari", "Sharvari", "Plava", "Shubhakrit", "Sobhakrit", "Krodhi", "Vishvavasu", "Parabhava",
            "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadi", "Ananda",
            "Rakshasa", "Nala", "Pingala", "Kalayukti", "Siddharthi", "Raudra", "Durmati", "Dundubhi",
            "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"
        ]
        
        # Calculate Tamil year (approximately)
        tamil_year_index = (year - 1987) % 60  # 1987 was Prabhava year
        tamil_year = tamil_years[tamil_year_index]
        
        return {
            "vikram_samvat": vikram_samvat,
            "shaka_samvat": shaka_samvat,
            "kali_yuga": kali_yuga,
            "bengali_san": bengali_san,
            "tamil_year": tamil_year
        }
    
    def calculate_tarabala_chandrabala(self, moon_long: float, dt: datetime) -> Dict[str, Any]:
        """Calculate Tarabala and Chandrabala"""
        # Get birth nakshatra (using a reference - in real app, this would be user's birth nakshatra)
        # For demo, using Rohini (4th nakshatra) as reference
        birth_nakshatra_number = 4  # This should come from user data
        
        # Current Moon nakshatra
        current_nakshatra_number = self.get_nakshatra_number(moon_long)
        
        # Calculate Tarabala
        if current_nakshatra_number >= birth_nakshatra_number:
            tara_count = current_nakshatra_number - birth_nakshatra_number + 1
        else:
            tara_count = current_nakshatra_number + 27 - birth_nakshatra_number + 1
        
        tara_count = ((tara_count - 1) % 9) + 1
        
        tara_names = [
            "Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhaka", "Vadha", "Mitra", "Param Mitra"
        ]
        
        tara_results = [
            "Neutral", "Very Good", "Bad", "Good", "Bad", "Good", "Very Bad", "Very Good", "Excellent"
        ]
        
        tarabala = tara_names[tara_count - 1]
        tarabala_result = tara_results[tara_count - 1]
        
        # Calculate Chandrabala (simplified)
        # Based on lunar day and other factors
        sun_long = self.get_approximate_sun_longitude(dt)
        tithi_number = int(((moon_long - sun_long) % 360) / 12.0)
        chandrabala_points = min(6, max(0, (tithi_number % 8)))
        
        chandrabala_names = ["Very Weak", "Weak", "Average", "Good", "Very Good", "Excellent", "Supreme"]
        chandrabala = chandrabala_names[min(6, chandrabala_points)]
        
        return {
            "tarabala": tarabala,
            "tarabala_number": tara_count,
            "tarabala_result": tarabala_result,
            "chandrabala": chandrabala,
            "chandrabala_points": chandrabala_points
        }
    
    def calculate_shool_nivas(self, dt: datetime, moon_long: float) -> Dict[str, Any]:
        """Calculate Shool direction and Nivas"""
        day_of_week = dt.weekday()  # 0 = Monday
        
        # Shool directions by day of week
        shool_directions = [
            "North",     # Monday
            "East",      # Tuesday  
            "South",     # Wednesday
            "West",      # Thursday
            "North",     # Friday
            "East",      # Saturday
            "South"      # Sunday
        ]
        
        # Ruling deities for each direction
        direction_deities = {
            "North": "Kubera",
            "East": "Indra", 
            "South": "Yama",
            "West": "Varuna"
        }
        
        # Current Nivas (residence) calculation based on lunar month
        nivas_cycle = ["Ksheera Sagara", "Vaikuntha", "Ksheer Sagara", "Bhu Loka", "Patala Loka", "Swarga Loka"]
        lunar_month = int((moon_long / 30) % 12)
        nivas = nivas_cycle[lunar_month % 6]
        
        # Favorable direction (opposite to Shool)
        direction_opposites = {
            "North": "South",
            "South": "North", 
            "East": "West",
            "West": "East"
        }
        
        shool_direction = shool_directions[day_of_week]
        favorable_direction = direction_opposites[shool_direction]
        
        return {
            "shool_direction": shool_direction,
            "shool_deity": direction_deities[shool_direction],
            "nivas": nivas,
            "favorable_direction": favorable_direction
        }
    
    def calculate_panchaka(self, dt: datetime, moon_long: float) -> Dict[str, Any]:
        """Calculate Panchaka classification"""
        # Get current nakshatra
        nakshatra_number = self.get_nakshatra_number(moon_long)
        
        # Panchaka nakshatras: Dhanishtha, Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada, Revati
        panchaka_nakshatras = [23, 24, 25, 26, 27]  # Nakshatra numbers
        
        if nakshatra_number in panchaka_nakshatras:
            # Determine specific Panchaka type based on additional factors
            day_of_week = dt.weekday()
            
            panchaka_types = [
                {
                    "type": "Agni Panchaka",
                    "description": "Fire element dominance, avoid fire-related activities",
                    "favorable": ["Religious ceremonies", "Spiritual practices", "Meditation"],
                    "avoid": ["Starting fires", "Cooking elaborate meals", "Metalwork"]
                },
                {
                    "type": "Raja Panchaka", 
                    "description": "Royal element, good for leadership activities",
                    "favorable": ["Government work", "Leadership roles", "Important decisions"],
                    "avoid": ["Submissive activities", "Following others blindly"]
                },
                {
                    "type": "Mrityu Panchaka",
                    "description": "Death element, avoid new beginnings",
                    "favorable": ["Ending bad habits", "Completing projects", "Letting go"],
                    "avoid": ["New ventures", "Marriages", "Important purchases"]
                },
                {
                    "type": "Chor Panchaka",
                    "description": "Theft element, be cautious with valuables",
                    "favorable": ["Security arrangements", "Vigilance", "Protective measures"],
                    "avoid": ["Displaying wealth", "Traveling with valuables", "Trusting strangers"]
                },
                {
                    "type": "Roga Panchaka",
                    "description": "Disease element, focus on health",
                    "favorable": ["Health checkups", "Healing practices", "Medical treatments"],
                    "avoid": ["Unhealthy food", "Stress", "Overexertion"]
                }
            ]
            
            panchaka_index = (nakshatra_number - 23 + day_of_week) % 5
            panchaka_info = panchaka_types[panchaka_index]
            
            return {
                "panchaka_type": panchaka_info["type"],
                "panchaka_description": panchaka_info["description"],
                "favorable_activities": panchaka_info["favorable"],
                "activities_to_avoid": panchaka_info["avoid"]
            }
        else:
            return {
                "panchaka_type": "No Panchaka",
                "panchaka_description": "Normal period, no special Panchaka restrictions",
                "favorable_activities": ["All normal activities", "General work", "Regular tasks"],
                "activities_to_avoid": ["None specific"]
            }
    
    def get_nakshatra_number(self, moon_long: float) -> int:
        """Get nakshatra number (1-27) from moon longitude"""
        return int(moon_long / 13.333333) + 1
    
    def get_approximate_sun_longitude(self, dt: datetime) -> float:
        """Get approximate sun longitude for given datetime"""
        # Simplified calculation - in production would use precise ephemeris
        day_of_year = dt.timetuple().tm_yday
        # Approximate sun longitude based on day of year
        # Spring equinox (March 21) is around day 80, when sun is at 0 degrees
        sun_longitude = ((day_of_year - 80) * 360 / 365.25) % 360
        return sun_longitude

# Global instance for easy access
panchang_enhancements = PanchangEnhancements()
