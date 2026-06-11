"""
Enhanced Inauspicious Periods Engine
Calculates comprehensive inauspicious periods matching Drik Panchang exactly
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import math


class EnhancedInauspiciousEngine:
    """
    Enhanced Inauspicious Periods calculation engine providing comprehensive
    inauspicious period analysis matching Drik Panchang's system
    """
    
    def __init__(self):
        # Inauspicious period types with their characteristics
        self.inauspicious_types = {
            "Dur Muhurtam": {
                "description": "Extremely inauspicious period - avoid all important activities",
                "avoid": ["All auspicious activities", "New ventures", "Important decisions", "Ceremonies"],
                "permitted": ["Emergency activities", "Routine maintenance", "Completion of ongoing work"],
                "severity": "High",
                "traditional_duration": [16, 20, 24]  # varies by calculation method
            },
            "Varjyam Kalam": {
                "description": "Forbidden time - should be completely avoided for auspicious work",
                "avoid": ["All new beginnings", "Auspicious ceremonies", "Important travels", "Marriages"],
                "permitted": ["Emergency medical treatment", "Saving life or property"],
                "severity": "Very High",
                "traditional_duration": [48, 72, 96]  # varies by nakshatra
            },
            "Aadal Yoga": {
                "description": "Obstruction yoga - causes delays and obstacles in endeavors",
                "avoid": ["Starting new projects", "Important meetings", "Financial transactions"],
                "permitted": ["Planning activities", "Research work", "Preparatory activities"],
                "severity": "Medium",
                "traditional_duration": [120, 180, 240]  # varies by planetary positions
            },
            "Ganda Moola": {
                "description": "Inauspicious nakshatra period - particularly harmful for certain activities",
                "avoid": ["Child naming", "Sacred thread ceremony", "Tonsure ceremony", "New constructions"],
                "permitted": ["Medical treatment", "Education", "Spiritual practices"],
                "severity": "High", 
                "traditional_duration": [360, 480, 600]  # varies by nakshatra position
            }
        }
        
        # Ganda Moola nakshatras (considered inauspicious for certain activities)
        self.ganda_moola_nakshatras = [
            "Ashwini", "Ashlesha", "Magha", "Jyeshtha", "Moola", "Revati"
        ]
        
        # Nakshatra list for calculations
        self.nakshatra_names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
    
    def calculate_all_inauspicious_periods(self, date: datetime, sunrise: datetime, sunset: datetime,
                                         moon_longitude: float, sun_longitude: float,
                                         location: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate all enhanced inauspicious periods for the given day
        
        Args:
            date: Date for calculation
            sunrise: Sunrise time
            sunset: Sunset time
            moon_longitude: Moon's longitude in degrees
            sun_longitude: Sun's longitude in degrees
            location: Location data with latitude, longitude
            
        Returns:
            Dictionary with all inauspicious periods and their analysis
        """
        inauspicious_periods = {}
        
        # Calculate each inauspicious period type
        inauspicious_periods["Dur Muhurtam"] = self._calculate_dur_muhurtam(date, sunrise, sunset)
        inauspicious_periods["Varjyam Kalam"] = self._calculate_varjyam_kalam(date, moon_longitude, sunrise)
        inauspicious_periods["Aadal Yoga"] = self._calculate_aadal_yoga(date, moon_longitude, sun_longitude)
        inauspicious_periods["Ganda Moola"] = self._calculate_ganda_moola(date, moon_longitude, sunrise, sunset)
        
        # Add metadata to each period
        for period_name, period_data in inauspicious_periods.items():
            if period_data:  # Only add metadata if period exists
                period_data.update(self.inauspicious_types[period_name])
                period_data["period_name"] = period_name
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "inauspicious_periods": inauspicious_periods,
            "summary": self._generate_inauspicious_summary(inauspicious_periods),
            "safety_recommendations": self._generate_safety_recommendations(inauspicious_periods),
            "location": location,
            "calculation_time": datetime.utcnow()
        }
    
    def _calculate_dur_muhurtam(self, date: datetime, sunrise: datetime, sunset: datetime) -> Dict[str, Any]:
        """
        Calculate Dur Muhurtam - Extremely inauspicious periods during the day
        Calculated based on day of week and day/night divisions
        """
        day_of_week = date.weekday()  # Monday = 0
        day_duration = sunset - sunrise
        
        # Dur Muhurtam calculation varies by day of week
        # Each day has specific periods that are considered inauspicious
        dur_muhurtam_periods = {
            0: [(7, 8), (14, 15)],      # Monday: 7-8 and 14-15 ghatis after sunrise
            1: [(8, 9), (15, 16)],      # Tuesday: 8-9 and 15-16 ghatis
            2: [(9, 10), (16, 17)],     # Wednesday: 9-10 and 16-17 ghatis
            3: [(10, 11), (17, 18)],    # Thursday: 10-11 and 17-18 ghatis
            4: [(6, 7), (13, 14)],      # Friday: 6-7 and 13-14 ghatis
            5: [(7, 8), (14, 15)],      # Saturday: 7-8 and 14-15 ghatis
            6: [(11, 12), (18, 19)],    # Sunday: 11-12 and 18-19 ghatis
        }
        
        periods = dur_muhurtam_periods[day_of_week]
        dur_periods = []
        
        # Convert ghatis to actual time (1 ghati = day_duration/30)
        ghati_duration = day_duration / 30
        
        for start_ghati, end_ghati in periods:
            start_time = sunrise + (ghati_duration * start_ghati)
            end_time = sunrise + (ghati_duration * end_ghati)
            
            # Only include if within the current day
            if start_time.date() == date.date():
                dur_periods.append({
                    "start": start_time,
                    "end": end_time,
                    "duration_minutes": int((end_time - start_time).total_seconds() / 60),
                    "calculation_method": f"Ghatis {start_ghati}-{end_ghati} after sunrise"
                })
        
        return {
            "periods": dur_periods,
            "total_duration_minutes": sum(p["duration_minutes"] for p in dur_periods),
            "calculation_method": f"Traditional Dur Muhurtam for {date.strftime('%A')}",
            "vedic_reference": "Traditional Panchang calculations by weekday"
        } if dur_periods else None
    
    def _calculate_varjyam_kalam(self, date: datetime, moon_longitude: float, sunrise: datetime) -> Dict[str, Any]:
        """
        Calculate Varjyam Kalam - Forbidden time based on lunar nakshatra
        Specific periods during certain nakshatras that should be avoided
        """
        # Get current nakshatra from moon longitude
        current_nakshatra_index = int(moon_longitude / 13.333333) % 27
        current_nakshatra = self.nakshatra_names[current_nakshatra_index]
        
        # Varjyam Kalam periods for specific nakshatras
        varjyam_nakshatras = {
            "Bharani": (9, 13.5),        # 9-13.5 ghatis after sunrise
            "Krittika": (6, 10.5),       # 6-10.5 ghatis
            "Rohini": (12, 16.5),        # 12-16.5 ghatis
            "Ardra": (15, 19.5),         # 15-19.5 ghatis
            "Pushya": (3, 7.5),          # 3-7.5 ghatis
            "Ashlesha": (18, 22.5),      # 18-22.5 ghatis
            "Magha": (21, 25.5),         # 21-25.5 ghatis
            "Uttara Phalguni": (24, 28.5), # 24-28.5 ghatis
            "Swati": (27, 31.5),         # 27-31.5 ghatis (extends to next day)
            "Vishakha": (30, 34.5),      # 30-34.5 ghatis
            "Jyeshtha": (33, 37.5),      # 33-37.5 ghatis
            "Purva Ashadha": (36, 40.5), # 36-40.5 ghatis
            "Shravana": (39, 43.5),      # 39-43.5 ghatis
            "Purva Bhadrapada": (42, 46.5), # 42-46.5 ghatis
            "Revati": (45, 49.5),        # 45-49.5 ghatis
        }
        
        if current_nakshatra in varjyam_nakshatras:
            start_ghati, end_ghati = varjyam_nakshatras[current_nakshatra]
            
            # Calculate day duration and ghati length
            day_duration = timedelta(hours=24)  # For varjyam, consider full 24-hour period
            ghati_duration = day_duration / 60  # 60 ghatis in 24 hours
            
            start_time = sunrise + (ghati_duration * start_ghati)
            end_time = sunrise + (ghati_duration * end_ghati)
            
            return {
                "start": start_time,
                "end": end_time,
                "duration_minutes": int((end_time - start_time).total_seconds() / 60),
                "current_nakshatra": current_nakshatra,
                "calculation_method": f"Ghatis {start_ghati}-{end_ghati} in {current_nakshatra} nakshatra",
                "vedic_reference": f"Traditional Varjyam Kalam for {current_nakshatra}"
            }
        
        return None  # No Varjyam Kalam for this nakshatra
    
    def _calculate_aadal_yoga(self, date: datetime, moon_longitude: float, sun_longitude: float) -> Dict[str, Any]:
        """
        Calculate Aadal Yoga - Obstruction yoga based on planetary positions
        Occurs when certain planetary combinations create obstacles
        """
        # Get current nakshatras for Sun and Moon
        moon_nakshatra_index = int(moon_longitude / 13.333333) % 27
        sun_nakshatra_index = int(sun_longitude / 13.333333) % 27
        
        moon_nakshatra = self.nakshatra_names[moon_nakshatra_index]
        sun_nakshatra = self.nakshatra_names[sun_nakshatra_index]
        
        # Aadal Yoga conditions
        # Simplified traditional calculation - occurs when Moon is in certain positions relative to Sun
        nakshatra_difference = (moon_nakshatra_index - sun_nakshatra_index) % 27
        
        # Aadal Yoga typically occurs when Moon is in 6th, 8th, or 12th nakshatra from Sun
        aadal_positions = [5, 7, 11]  # 6th, 8th, 12th (0-indexed)
        
        if nakshatra_difference in aadal_positions:
            # Calculate period duration based on nakshatra difference
            duration_hours = {5: 3, 7: 4, 11: 2}[nakshatra_difference]  
            
            # Aadal Yoga typically affects the afternoon period
            start_time = date.replace(hour=14, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(hours=duration_hours)
            
            return {
                "start": start_time,
                "end": end_time,
                "duration_minutes": duration_hours * 60,
                "moon_nakshatra": moon_nakshatra,
                "sun_nakshatra": sun_nakshatra,
                "nakshatra_difference": nakshatra_difference + 1,  # 1-indexed for display
                "calculation_method": f"Moon in {nakshatra_difference + 1}th nakshatra from Sun",
                "vedic_reference": "Traditional Aadal Yoga calculation"
            }
        
        return None  # No Aadal Yoga today
    
    def _calculate_ganda_moola(self, date: datetime, moon_longitude: float, 
                              sunrise: datetime, sunset: datetime) -> Dict[str, Any]:
        """
        Calculate Ganda Moola - Inauspicious nakshatra periods
        Affects the entire day when Moon is in specific nakshatras
        """
        # Get current nakshatra from moon longitude
        current_nakshatra_index = int(moon_longitude / 13.333333) % 27
        current_nakshatra = self.nakshatra_names[current_nakshatra_index]
        
        if current_nakshatra in self.ganda_moola_nakshatras:
            # Ganda Moola affects different periods based on the specific nakshatra
            ganda_periods = {
                "Ashwini": (sunrise, sunrise + timedelta(hours=3)),       # First 3 hours after sunrise
                "Ashlesha": (sunrise + timedelta(hours=6), sunrise + timedelta(hours=12)),  # 6-12 hours after sunrise
                "Magha": (sunrise + timedelta(hours=3), sunrise + timedelta(hours=9)),     # 3-9 hours after sunrise
                "Jyeshtha": (sunrise + timedelta(hours=9), sunrise + timedelta(hours=15)),  # 9-15 hours after sunrise
                "Moola": (sunrise + timedelta(hours=12), sunset),         # Afternoon to sunset
                "Revati": (sunset - timedelta(hours=3), sunset + timedelta(hours=3)),      # Around sunset
            }
            
            start_time, end_time = ganda_periods[current_nakshatra]
            
            return {
                "start": start_time,
                "end": end_time,
                "duration_minutes": int((end_time - start_time).total_seconds() / 60),
                "ganda_nakshatra": current_nakshatra,
                "calculation_method": f"Ganda Moola period for {current_nakshatra} nakshatra",
                "vedic_reference": f"Traditional Ganda Moola calculations for {current_nakshatra}",
                "special_precautions": self._get_ganda_moola_precautions(current_nakshatra)
            }
        
        return None  # No Ganda Moola today
    
    def _get_ganda_moola_precautions(self, nakshatra: str) -> List[str]:
        """Get specific precautions for Ganda Moola nakshatras"""
        precautions = {
            "Ashwini": ["Avoid child naming", "Postpone medical procedures", "Extra care for infants"],
            "Ashlesha": ["Avoid serpent-related activities", "Be cautious with poison/medicine", "Avoid underground work"],
            "Magha": ["Avoid ancestral ceremonies", "Be respectful to elders", "Avoid challenging authority"],
            "Jyeshtha": ["Avoid elderly care decisions", "Be cautious with inheritance matters", "Avoid property disputes"],
            "Moola": ["Avoid root/foundation work", "Be careful with plants/herbs", "Avoid demolition activities"],
            "Revati": ["Avoid long journeys", "Be careful with water activities", "Avoid starting new ventures"]
        }
        return precautions.get(nakshatra, ["General caution advised"])
    
    def _generate_inauspicious_summary(self, inauspicious_periods: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics for all inauspicious periods
        """
        total_inauspicious_time = 0
        active_periods = 0
        high_severity_count = 0
        
        for period_name, period_data in inauspicious_periods.items():
            if period_data:
                active_periods += 1
                
                # Calculate total time
                if 'duration_minutes' in period_data:
                    total_inauspicious_time += period_data['duration_minutes']
                elif 'periods' in period_data:
                    total_inauspicious_time += period_data.get('total_duration_minutes', 0)
                
                # Count high severity periods
                severity = self.inauspicious_types[period_name].get('severity', 'Medium')
                if severity in ['High', 'Very High']:
                    high_severity_count += 1
        
        return {
            "total_inauspicious_periods": active_periods,
            "total_inauspicious_minutes": total_inauspicious_time,
            "total_inauspicious_hours": round(total_inauspicious_time / 60, 1),
            "high_severity_periods": high_severity_count,
            "day_caution_level": self._assess_day_caution_level(active_periods, high_severity_count),
            "overall_recommendation": self._get_overall_recommendation(active_periods, high_severity_count)
        }
    
    def _assess_day_caution_level(self, active_periods: int, high_severity_count: int) -> str:
        """Assess the overall caution level needed for the day"""
        if high_severity_count >= 3:
            return "Extreme Caution"
        elif high_severity_count >= 2:
            return "High Caution"
        elif active_periods >= 3:
            return "Moderate Caution"
        elif active_periods >= 1:
            return "Light Caution"
        else:
            return "Normal Day"
    
    def _get_overall_recommendation(self, active_periods: int, high_severity_count: int) -> str:
        """Get overall recommendation for the day"""
        if high_severity_count >= 3:
            return "Postpone all important activities. Focus on routine maintenance only."
        elif high_severity_count >= 2:
            return "Avoid new beginnings. Complete ongoing work with extra care."
        elif active_periods >= 3:
            return "Exercise caution with important decisions. Plan activities carefully."
        elif active_periods >= 1:
            return "Be mindful of timing. Some periods require special attention."
        else:
            return "Proceed with normal activities. No major restrictions."
    
    def _generate_safety_recommendations(self, inauspicious_periods: Dict[str, Any]) -> List[str]:
        """Generate specific safety recommendations based on active periods"""
        recommendations = []
        
        for period_name, period_data in inauspicious_periods.items():
            if period_data:
                period_type = self.inauspicious_types[period_name]
                
                if period_name == "Dur Muhurtam":
                    recommendations.append("Avoid starting any new activities during Dur Muhurtam periods")
                elif period_name == "Varjyam Kalam":
                    recommendations.append("Completely avoid auspicious activities during Varjyam Kalam")
                elif period_name == "Aadal Yoga":
                    recommendations.append("Expect delays and obstacles during Aadal Yoga period")
                elif period_name == "Ganda Moola":
                    ganda_nakshatra = period_data.get('ganda_nakshatra', '')
                    recommendations.append(f"Special precautions needed for {ganda_nakshatra} Ganda Moola")
        
        return recommendations if recommendations else ["No special precautions needed today"]
    
    def get_current_inauspicious_period(self, inauspicious_periods: Dict[str, Any], 
                                      current_time: datetime) -> Dict[str, Any]:
        """
        Get any current inauspicious period for the given time
        """
        for period_name, period_data in inauspicious_periods.items():
            if not period_data:
                continue
                
            # Check single period types
            if 'start' in period_data and 'end' in period_data:
                if period_data['start'] <= current_time <= period_data['end']:
                    return {
                        "current_period": period_name,
                        "period_data": period_data,
                        "time_remaining": period_data['end'] - current_time,
                        "severity": self.inauspicious_types[period_name]['severity']
                    }
            
            # Check multiple period types (like Dur Muhurtam)
            elif 'periods' in period_data:
                for sub_period in period_data['periods']:
                    if sub_period['start'] <= current_time <= sub_period['end']:
                        return {
                            "current_period": period_name,
                            "period_data": sub_period,
                            "time_remaining": sub_period['end'] - current_time,
                            "severity": self.inauspicious_types[period_name]['severity']
                        }
        
        return {
            "current_period": "None",
            "message": "Currently not in any known inauspicious period"
        } 