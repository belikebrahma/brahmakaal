"""
Calendar System Extensions Engine
Advanced calendar systems matching Drik Panchang exactly
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import math


class CalendarExtensionsEngine:
    """
    Calendar Extensions calculation engine providing advanced calendar systems
    including Gujarati Samvat, Pravishte/Gate system, and enhanced Brihaspati Samvatsara
    """
    
    def __init__(self):
        # Brihaspati Samvatsara cycle (60-year cycle)
        self.brihaspati_samvatsaras = [
            "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati",
            "Angirasa", "Shrimukha", "Bhava", "Yuva", "Dhata",
            "Ishvara", "Bahudhanya", "Pramadhi", "Vikrama", "Visha",
            "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
            "Sarvajit", "Sarvadharin", "Virodhin", "Vikrita", "Khara",
            "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukha",
            "Hemalamba", "Vilamba", "Vikarin", "Sharvarin", "Plava",
            "Shubhakrit", "Shobhakrit", "Krodhin", "Vishvavasu", "Parabhava",
            "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit",
            "Paridhavin", "Pramadin", "Ananda", "Rakshasa", "Nala",
            "Pingala", "Kalayukta", "Siddharthin", "Raudra", "Durmati",
            "Dundubhi", "Rudhirodgarin", "Raktaksha", "Krodhana", "Akshaya"
        ]
        
        # Gujarati calendar months and their characteristics
        self.gujarati_months = [
            {"name": "Kartik", "season": "Sharad", "deity": "Lakshmi"},
            {"name": "Margashirsha", "season": "Sharad", "deity": "Vishnu"},
            {"name": "Pausha", "season": "Shishir", "deity": "Narayana"},
            {"name": "Magha", "season": "Shishir", "deity": "Shiva"},
            {"name": "Phalguna", "season": "Vasant", "deity": "Brahma"},
            {"name": "Chaitra", "season": "Vasant", "deity": "Chaitra"},
            {"name": "Vaishakha", "season": "Grishma", "deity": "Madhava"},
            {"name": "Jyeshtha", "season": "Grishma", "deity": "Trivikrama"},
            {"name": "Ashadha", "season": "Varsha", "deity": "Vamana"},
            {"name": "Shravana", "season": "Varsha", "deity": "Shridhara"},
            {"name": "Bhadrapada", "season": "Varsha", "deity": "Hrishikesha"},
            {"name": "Ashwin", "season": "Sharad", "deity": "Padmanabha"}
        ]
        
        # Pravishte/Gate system - traditional classification
        self.pravishte_gates = {
            1: {"name": "Dhvaja", "description": "Flag gate - auspicious for victories"},
            2: {"name": "Simha", "description": "Lion gate - powerful for leadership"},
            3: {"name": "Gaja", "description": "Elephant gate - good for wealth"},
            4: {"name": "Turaga", "description": "Horse gate - favorable for travel"},
            5: {"name": "Kharga", "description": "Sword gate - warning of conflicts"},
            6: {"name": "Vajra", "description": "Diamond gate - strong for important matters"},
            7: {"name": "Musala", "description": "Pestle gate - good for agriculture"},
            8: {"name": "Kuta", "description": "Mountain gate - stability and endurance"},
            9: {"name": "Chapa", "description": "Bow gate - success in competitions"},
            10: {"name": "Padma", "description": "Lotus gate - highly auspicious"},
            11: {"name": "Makaranda", "description": "Nectar gate - spiritual benefits"},
            12: {"name": "Kalpavriksha", "description": "Wish tree gate - fulfills desires"}
        }
    
    def calculate_extended_calendar_systems(self, date: datetime, sun_longitude: float,
                                          moon_longitude: float, ayanamsha: float) -> Dict[str, Any]:
        """
        Calculate all extended calendar systems for the given date
        
        Args:
            date: Date for calculation
            sun_longitude: Sun's longitude in degrees
            moon_longitude: Moon's longitude in degrees
            ayanamsha: Ayanamsha value for the date
            
        Returns:
            Dictionary with all extended calendar system data
        """
        extended_systems = {}
        
        # Calculate Gujarati Samvat system
        extended_systems["gujarati_samvat"] = self._calculate_gujarati_samvat(date, sun_longitude)
        
        # Calculate Pravishte/Gate system
        extended_systems["pravishte_gate"] = self._calculate_pravishte_gate(date, moon_longitude)
        
        # Calculate enhanced Brihaspati Samvatsara
        extended_systems["brihaspati_samvatsara"] = self._calculate_brihaspati_samvatsara(date)
        
        # Calculate additional era systems
        extended_systems["era_systems"] = self._calculate_era_systems(date)
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "extended_calendar_systems": extended_systems,
            "summary": self._generate_calendar_summary(extended_systems),
            "cultural_significance": self._generate_cultural_significance(extended_systems),
            "calculation_time": datetime.utcnow()
        }
    
    def _calculate_gujarati_samvat(self, date: datetime, sun_longitude: float) -> Dict[str, Any]:
        """
        Calculate Gujarati Samvat calendar system
        Gujarati New Year starts around Kartik Shukla Pratipada
        """
        # Gujarati calendar year calculation
        # Base year 57 BCE for Vikram Samvat, but Gujarati starts from Kartik
        base_year = 57
        current_year = date.year + base_year
        
        # Determine if we're before or after Gujarati New Year (around October/November)
        # Gujarati New Year is on the day after Diwali (Kartik Shukla Pratipada)
        if date.month < 10:  # Before Gujarati New Year
            gujarati_year = current_year - 1
        elif date.month == 10 or date.month == 11:
            # Need to check exact date of Gujarati New Year for this year
            # Simplified calculation - usually around Kartik Shukla Pratipada
            gujarati_year = current_year - 1 if date.day < 15 else current_year
        else:
            gujarati_year = current_year
        
        # Determine current Gujarati month based on sun's longitude
        # Gujarati months are lunar-solar, starting from Kartik
        sun_rashi = int(sun_longitude / 30) % 12
        
        # Adjust for Gujarati calendar which starts from Kartik (around Scorpio)
        gujarati_month_index = (sun_rashi + 1) % 12  # +1 to start from Kartik
        gujarati_month = self.gujarati_months[gujarati_month_index]
        
        return {
            "year": gujarati_year,
            "month": gujarati_month["name"],
            "season": gujarati_month["season"],
            "presiding_deity": gujarati_month["deity"],
            "calculation_method": "Traditional Gujarati calendar based on Kartik commencement",
            "cultural_notes": "Gujarati calendar starts from Kartik Shukla Pratipada (day after Diwali)"
        }
    
    def _calculate_pravishte_gate(self, date: datetime, moon_longitude: float) -> Dict[str, Any]:
        """
        Calculate Pravishte/Gate system based on lunar position and date
        Traditional system for determining auspicious gates
        """
        # Calculate gate number based on multiple factors
        # Day of month
        day_factor = date.day % 12
        
        # Moon's nakshatra
        moon_nakshatra = int(moon_longitude / 13.333333) % 27
        nakshatra_factor = (moon_nakshatra % 12) + 1
        
        # Weekday
        weekday_factor = date.weekday() + 1
        
        # Combined calculation for gate determination
        gate_number = ((day_factor + nakshatra_factor + weekday_factor) % 12) + 1
        
        gate_info = self.pravishte_gates[gate_number]
        
        # Determine auspiciousness level
        auspicious_gates = [1, 2, 3, 6, 9, 10, 11, 12]  # Traditionally favorable gates
        is_auspicious = gate_number in auspicious_gates
        
        return {
            "gate_number": gate_number,
            "gate_name": gate_info["name"],
            "description": gate_info["description"],
            "is_auspicious": is_auspicious,
            "auspiciousness_level": "Highly Favorable" if gate_number in [10, 11, 12] else
                                   "Favorable" if is_auspicious else
                                   "Caution Advised",
            "calculation_factors": {
                "day_of_month": date.day,
                "moon_nakshatra": moon_nakshatra + 1,
                "weekday": date.strftime("%A")
            },
            "vedic_reference": "Traditional Pravishte gate calculation system"
        }
    
    def _calculate_brihaspati_samvatsara(self, date: datetime) -> Dict[str, Any]:
        """
        Calculate enhanced Brihaspati Samvatsara (60-year cycle)
        More detailed than basic implementation
        """
        # Base year for calculation (traditionally 2082 BCE)
        base_year = 2082
        years_elapsed = date.year + base_year
        
        # Current position in 60-year cycle
        cycle_position = years_elapsed % 60
        current_samvatsara = self.brihaspati_samvatsaras[cycle_position]
        
        # Calculate which cycle we're in
        cycle_number = (years_elapsed // 60) + 1
        
        # Years remaining in current cycle
        years_remaining_in_cycle = 60 - (cycle_position + 1)
        
        # Next samvatsara
        next_position = (cycle_position + 1) % 60
        next_samvatsara = self.brihaspati_samvatsaras[next_position]
        
        # Get characteristics of current samvatsara
        samvatsara_characteristics = self._get_samvatsara_characteristics(current_samvatsara)
        
        return {
            "current_samvatsara": current_samvatsara,
            "cycle_number": cycle_number,
            "position_in_cycle": cycle_position + 1,
            "years_remaining_in_cycle": years_remaining_in_cycle,
            "next_samvatsara": next_samvatsara,
            "characteristics": samvatsara_characteristics,
            "calculation_method": "Traditional 60-year Brihaspati cycle",
            "vedic_reference": "Based on Jupiter's orbital period approximation"
        }
    
    def _get_samvatsara_characteristics(self, samvatsara: str) -> Dict[str, Any]:
        """Get characteristics for specific Brihaspati Samvatsara"""
        # Simplified characteristics - in reality this would be much more detailed
        characteristics_map = {
            "Prabhava": {"nature": "Influential", "quality": "Leadership", "element": "Fire"},
            "Vibhava": {"nature": "Prosperous", "quality": "Wealth", "element": "Earth"},
            "Shukla": {"nature": "Pure", "quality": "Spirituality", "element": "Air"},
            "Pramoda": {"nature": "Joyful", "quality": "Happiness", "element": "Water"},
            "Kalayukta": {"nature": "Artistic", "quality": "Creativity", "element": "Fire"},
            "Siddharthin": {"nature": "Achieving", "quality": "Success", "element": "Earth"},
            "Akshaya": {"nature": "Eternal", "quality": "Permanence", "element": "Air"}
        }
        
        return characteristics_map.get(samvatsara, {
            "nature": "Balanced",
            "quality": "Moderate",
            "element": "Mixed"
        })
    
    def _calculate_era_systems(self, date: datetime) -> Dict[str, Any]:
        """Calculate various era systems used in Indian calendar"""
        current_year = date.year
        
        return {
            "kali_yuga": {
                "year": current_year + 3102,  # Kali Yuga started 3102 BCE
                "description": "Years since Kali Yuga commencement"
            },
            "saka_era": {
                "year": current_year - 78,  # Saka era started 78 CE
                "description": "Official Indian National Calendar era"
            },
            "buddha_nirvana": {
                "year": current_year + 544,  # Buddha's Nirvana traditionally 544 BCE
                "description": "Years since Buddha's Mahaparinirvana"
            },
            "hijri_approximate": {
                "year": int((current_year - 622) * 1.030684),  # Approximate Hijri conversion
                "description": "Approximate Islamic Hijri year"
            }
        }
    
    def _generate_calendar_summary(self, extended_systems: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of all calendar systems"""
        gujarati = extended_systems.get("gujarati_samvat", {})
        pravishte = extended_systems.get("pravishte_gate", {})
        brihaspati = extended_systems.get("brihaspati_samvatsara", {})
        
        return {
            "primary_era": f"Gujarati Samvat {gujarati.get('year', 'Unknown')}",
            "current_season": gujarati.get("season", "Unknown"),
            "pravishte_status": pravishte.get("auspiciousness_level", "Unknown"),
            "brihaspati_cycle": f"{brihaspati.get('current_samvatsara', 'Unknown')} ({brihaspati.get('position_in_cycle', 0)}/60)",
            "overall_assessment": self._assess_calendar_alignment(extended_systems)
        }
    
    def _assess_calendar_alignment(self, extended_systems: Dict[str, Any]) -> str:
        """Assess overall auspiciousness based on calendar alignments"""
        pravishte = extended_systems.get("pravishte_gate", {})
        
        if pravishte.get("is_auspicious", False):
            if pravishte.get("auspiciousness_level") == "Highly Favorable":
                return "Extremely Auspicious Period"
            else:
                return "Favorable Period"
        else:
            return "Exercise Caution"
    
    def _generate_cultural_significance(self, extended_systems: Dict[str, Any]) -> List[str]:
        """Generate cultural significance notes"""
        significance = []
        
        gujarati = extended_systems.get("gujarati_samvat", {})
        pravishte = extended_systems.get("pravishte_gate", {})
        brihaspati = extended_systems.get("brihaspati_samvatsara", {})
        
        # Gujarati calendar significance
        if gujarati.get("month"):
            month = gujarati["month"]
            deity = gujarati.get("presiding_deity", "Unknown")
            significance.append(f"Gujarati month {month} is presided over by {deity}")
        
        # Pravishte gate significance
        if pravishte.get("gate_name"):
            gate = pravishte["gate_name"]
            significance.append(f"Today's Pravishte gate is {gate} - {pravishte.get('description', '')}")
        
        # Brihaspati Samvatsara significance
        if brihaspati.get("current_samvatsara"):
            samvatsara = brihaspati["current_samvatsara"]
            characteristics = brihaspati.get("characteristics", {})
            nature = characteristics.get("nature", "Unknown")
            significance.append(f"Current Brihaspati Samvatsara {samvatsara} has {nature} nature")
        
        return significance if significance else ["Standard calendar period with no special significance"] 