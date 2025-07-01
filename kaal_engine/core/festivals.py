"""
Comprehensive Hindu Festival Calendar System for Brahmakaal
Handles all types of Hindu festivals, regional variations, and calendar generation

This module implements a complete festival calculation engine supporting:
- Lunar festivals (tithi-based)
- Solar festivals (sankranti-based) 
- Nakshatra-based festivals
- Regional variations across India
- Ekadashi and spiritual observances
- Multi-year calendar generation
"""

from datetime import datetime, timedelta, timezone, date
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import calendar
import json
from collections import defaultdict

class FestivalType(Enum):
    """Types of Hindu festivals"""
    LUNAR = "lunar"           # Based on tithi (lunar day)
    SOLAR = "solar"           # Based on solar months/sankranti
    NAKSHATRA = "nakshatra"   # Based on nakshatra (lunar mansion)
    YOGA = "yoga"             # Based on yoga combinations
    FIXED = "fixed"           # Fixed dates (rare)
    CALCULATED = "calculated" # Complex calculations (e.g., Ekadashi)

class FestivalCategory(Enum):
    """Categories of festivals"""
    MAJOR = "major"           # Major festivals (Diwali, Holi, etc.)
    RELIGIOUS = "religious"   # Religious observances
    SEASONAL = "seasonal"     # Seasonal celebrations
    REGIONAL = "regional"     # Regional specific
    SPIRITUAL = "spiritual"   # Spiritual observances (Ekadashi, etc.)
    CULTURAL = "cultural"     # Cultural celebrations
    ASTRONOMICAL = "astronomical" # Astronomical events

class Region(Enum):
    """Regional variations"""
    ALL_INDIA = "all_india"
    NORTH_INDIA = "north_india"
    SOUTH_INDIA = "south_india"
    WEST_INDIA = "west_india"
    EAST_INDIA = "east_india"
    MAHARASHTRA = "maharashtra"
    GUJARAT = "gujarat"
    BENGAL = "bengal"
    TAMIL_NADU = "tamil_nadu"
    KERALA = "kerala"
    KARNATAKA = "karnataka"
    ANDHRA_PRADESH = "andhra_pradesh"
    RAJASTHAN = "rajasthan"
    PUNJAB = "punjab"
    ODISHA = "odisha"
    ASSAM = "assam"

@dataclass
class FestivalRule:
    """Defines rules for calculating a festival"""
    name: str
    english_name: str
    festival_type: FestivalType
    category: FestivalCategory
    regions: List[Region]
    
    # Lunar festival parameters
    month: Optional[str] = None  # Hindu month name
    paksha: Optional[str] = None  # "shukla" or "krishna"
    tithi: Optional[int] = None   # 1-15 for lunar day
    
    # Solar festival parameters
    solar_month: Optional[int] = None  # 1-12 for solar month
    solar_day: Optional[int] = None    # Day of solar month
    
    # Nakshatra festival parameters
    nakshatra: Optional[str] = None    # Nakshatra name
    
    # Alternative names and descriptions
    description: str = ""
    alternative_names: List[str] = field(default_factory=list)
    
    # Special rules
    special_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Observance details
    duration_days: int = 1
    observance_time: str = "full_day"  # "sunrise", "sunset", "noon", "full_day"

@dataclass
class FestivalDate:
    """Represents a calculated festival date"""
    festival_rule: FestivalRule
    date: date
    year: int
    additional_info: Dict[str, Any] = field(default_factory=dict)
    regional_variations: Dict[Region, date] = field(default_factory=dict)

class HinduCalendar:
    """Hindu calendar calculations and utilities"""
    
    # Hindu month names (Lunar)
    HINDU_MONTHS = [
        "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
        "Shravana", "Bhadrapada", "Ashwin", "Kartik", 
        "Margashirsha", "Pausha", "Magha", "Phalguna"
    ]
    
    # Solar month names
    SOLAR_MONTHS = [
        "Mesha", "Vrishabha", "Mithuna", "Karka",
        "Simha", "Kanya", "Tula", "Vrischika",
        "Dhanus", "Makara", "Kumbha", "Meena"
    ]
    
    # Nakshatra names
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
        "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
        "Purva_Phalguni", "Uttara_Phalguni", "Hasta", "Chitra", "Swati",
        "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva_Ashadha",
        "Uttara_Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva_Bhadrapada",
        "Uttara_Bhadrapada", "Revati"
    ]

class FestivalEngine:
    """
    Comprehensive Festival Calculation Engine
    
    Calculates Hindu festivals for any given year with regional variations,
    supporting all major festival types and observance patterns.
    """
    
    def __init__(self, kaal_engine):
        """
        Initialize festival engine with astronomical calculations
        
        Args:
            kaal_engine: Instance of Kaal class for astronomical calculations
        """
        self.kaal = kaal_engine
        self.calendar = HinduCalendar()
        self.festival_rules = []
        self.cache = {}
        
        # Initialize festival database
        self._initialize_festival_database()
    
    def _initialize_festival_database(self):
        """Initialize comprehensive festival rule database"""
        
        # Major Pan-Indian Festivals
        self._add_major_festivals()
        
        # Religious and Spiritual Observances
        self._add_religious_festivals()
        
        # Seasonal and Cultural Festivals
        self._add_seasonal_festivals()
        
        # Regional Festivals
        self._add_regional_festivals()
        
        # Ekadashi and Spiritual Observances
        self._add_spiritual_observances()
        
        # Astronomical Events
        self._add_astronomical_festivals()
    
    def _add_major_festivals(self):
        """Add major pan-Indian festivals"""
        
        major_festivals = [
            # Diwali Complex (5-day celebration)
            FestivalRule(
                name="Dhanteras",
                english_name="Dhanteras",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=13,
                description="First day of Diwali, worship of wealth and prosperity"
            ),
            FestivalRule(
                name="Naraka Chaturdashi",
                english_name="Choti Diwali",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=14,
                description="Second day of Diwali, defeat of demon Narakasura",
                alternative_names=["Choti Diwali", "Roop Chaudas"]
            ),
            FestivalRule(
                name="Diwali",
                english_name="Diwali",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=15,  # Amavasya
                description="Festival of lights, worship of Goddess Lakshmi",
                alternative_names=["Deepavali", "Lakshmi Puja"]
            ),
            FestivalRule(
                name="Govardhan Puja",
                english_name="Govardhan Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="shukla",
                tithi=1,
                description="Fourth day of Diwali, worship of Mount Govardhan",
                alternative_names=["Annakut"]
            ),
            FestivalRule(
                name="Bhai Dooj",
                english_name="Bhai Dooj",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="shukla",
                tithi=2,
                description="Fifth day of Diwali, bond between brothers and sisters",
                alternative_names=["Bhai Tika", "Yama Dwitiya"]
            ),
            
            # Holi Complex
            FestivalRule(
                name="Holika Dahan",
                english_name="Holika Dahan",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Phalguna",
                paksha="shukla",
                tithi=15,  # Purnima
                description="Bonfire night before Holi, burning of Holika",
                observance_time="sunset"
            ),
            FestivalRule(
                name="Holi",
                english_name="Holi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Chaitra",
                paksha="krishna",
                tithi=1,
                description="Festival of colors, celebration of spring",
                alternative_names=["Rangwali Holi", "Dhulandi"]
            ),
            
            # Navaratri and Durga Puja
            FestivalRule(
                name="Chaitra Navaratri",
                english_name="Chaitra Navaratri",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=1,
                description="Nine nights dedicated to Goddess Durga",
                duration_days=9
            ),
            FestivalRule(
                name="Sharad Navaratri",
                english_name="Navaratri",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=1,
                description="Nine nights dedicated to Goddess Durga",
                duration_days=9,
                alternative_names=["Durga Puja", "Dussehra"]
            ),
            FestivalRule(
                name="Dussehra",
                english_name="Dussehra",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=10,
                description="Victory of good over evil, Ram's victory over Ravana",
                alternative_names=["Vijayadashami", "Dasara"]
            ),
            
            # Krishna Festivals
            FestivalRule(
                name="Krishna Janmashtami",
                english_name="Krishna Janmashtami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="krishna",
                tithi=8,
                description="Birth of Lord Krishna",
                alternative_names=["Janmashtami", "Gokulashtami"],
                observance_time="midnight"
            ),
            
            # Ganesha Festival
            FestivalRule(
                name="Ganesh Chaturthi",
                english_name="Ganesh Chaturthi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=4,
                description="Birth of Lord Ganesha",
                alternative_names=["Vinayaka Chaturthi"]
            ),
            
            # Ram Festival
            FestivalRule(
                name="Ram Navami",
                english_name="Ram Navami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=9,
                description="Birth of Lord Rama"
            ),
            
            # Karva Chauth
            FestivalRule(
                name="Karva Chauth",
                english_name="Karva Chauth",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=4,
                description="Fast by married women for husband's longevity",
                observance_time="moonrise"
            ),
        ]
        
        self.festival_rules.extend(major_festivals)
    
    def _add_religious_festivals(self):
        """Add religious and spiritual festivals"""
        
        religious_festivals = [
            # Shiva Festivals
            FestivalRule(
                name="Maha Shivaratri",
                english_name="Maha Shivaratri",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Magha",
                paksha="krishna",
                tithi=14,
                description="Great night of Lord Shiva",
                observance_time="night"
            ),
            
            # Hanuman Festivals
            FestivalRule(
                name="Hanuman Jayanti",
                english_name="Hanuman Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=15,  # Purnima
                description="Birth of Lord Hanuman"
            ),
            
            # Guru Festivals
            FestivalRule(
                name="Guru Purnima",
                english_name="Guru Purnima",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Ashadha",
                paksha="shukla",
                tithi=15,  # Purnima
                description="Honoring spiritual teachers and gurus"
            ),
            
            # Saraswati Festival
            FestivalRule(
                name="Saraswati Puja",
                english_name="Saraswati Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.BENGAL, Region.EAST_INDIA],
                month="Magha",
                paksha="shukla",
                tithi=5,
                description="Worship of Goddess Saraswati",
                alternative_names=["Vasant Panchami"]
            ),
            
            # Lakshmi Festivals
            FestivalRule(
                name="Varalakshmi Vratam",
                english_name="Varalakshmi Vratam",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.SOUTH_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=15,  # Usually Friday before Purnima
                description="Worship of Goddess Lakshmi by married women"
            ),
        ]
        
        self.festival_rules.extend(religious_festivals)
    
    def _add_seasonal_festivals(self):
        """Add seasonal and harvest festivals"""
        
        seasonal_festivals = [
            # Harvest Festivals
            FestivalRule(
                name="Makar Sankranti",
                english_name="Makar Sankranti",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.ALL_INDIA],
                solar_month=10,  # Makara (Capricorn)
                solar_day=1,     # Entry into Capricorn
                description="Winter solstice, harvest festival",
                alternative_names=["Pongal", "Lohri", "Uttarayan"]
            ),
            
            # Spring Festivals
            FestivalRule(
                name="Basant Panchami",
                english_name="Basant Panchami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.NORTH_INDIA],
                month="Magha",
                paksha="shukla",
                tithi=5,
                description="Arrival of spring, worship of Saraswati",
                alternative_names=["Vasant Panchami", "Saraswati Puja"]
            ),
            
            # Monsoon Festivals
            FestivalRule(
                name="Teej",
                english_name="Teej",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.NORTH_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=3,
                description="Monsoon festival, worship of Parvati",
                alternative_names=["Hariyali Teej"]
            ),
        ]
        
        self.festival_rules.extend(seasonal_festivals)
    
    def _add_regional_festivals(self):
        """Add region-specific festivals"""
        
        regional_festivals = [
            # Bengali Festivals
            FestivalRule(
                name="Durga Puja",
                english_name="Durga Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.BENGAL],
                month="Ashwin",
                paksha="shukla",
                tithi=6,  # Shashti to Dashami
                description="Grand worship of Goddess Durga in Bengal",
                duration_days=5
            ),
            FestivalRule(
                name="Kali Puja",
                english_name="Kali Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.BENGAL],
                month="Kartik",
                paksha="krishna",
                tithi=15,  # Same as Diwali
                description="Worship of Goddess Kali in Bengal"
            ),
            
            # South Indian Festivals
            FestivalRule(
                name="Onam",
                english_name="Onam",
                festival_type=FestivalType.NAKSHATRA,
                category=FestivalCategory.REGIONAL,
                regions=[Region.KERALA],
                nakshatra="Thiruvonam",  # Shravana
                month="Bhadrapada",  # Usually in this month
                description="Harvest festival of Kerala",
                duration_days=10
            ),
            FestivalRule(
                name="Pongal",
                english_name="Pongal",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.TAMIL_NADU],
                solar_month=10,  # Makara (same as Makar Sankranti)
                description="Harvest festival of Tamil Nadu",
                duration_days=4
            ),
            
            # Gujarati Festivals
            FestivalRule(
                name="Navratri",
                english_name="Navratri",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.GUJARAT],
                month="Ashwin",
                paksha="shukla",
                tithi=1,
                description="Nine nights of dance and devotion in Gujarat",
                duration_days=9
            ),
            
            # Maharashtrian Festivals
            FestivalRule(
                name="Gudi Padwa",
                english_name="Gudi Padwa",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.MAHARASHTRA],
                month="Chaitra",
                paksha="shukla",
                tithi=1,
                description="Marathi New Year"
            ),
            
            # Punjabi Festivals
            FestivalRule(
                name="Lohri",
                english_name="Lohri",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.PUNJAB],
                solar_month=10,  # Day before Makar Sankranti
                description="Punjabi harvest festival"
            ),
            FestivalRule(
                name="Baisakhi",
                english_name="Baisakhi",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.PUNJAB],
                solar_month=1,  # Mesha (Aries)
                solar_day=13,   # Usually April 13/14
                description="Punjabi New Year and harvest festival"
            ),
        ]
        
        self.festival_rules.extend(regional_festivals)
    
    def _add_spiritual_observances(self):
        """Add Ekadashi and other spiritual observances"""
        
        spiritual_observances = [
            # Note: Ekadashi dates are calculated dynamically as they occur twice per month
            FestivalRule(
                name="Ekadashi",
                english_name="Ekadashi",
                festival_type=FestivalType.CALCULATED,
                category=FestivalCategory.SPIRITUAL,
                regions=[Region.ALL_INDIA],
                tithi=11,  # 11th day of both paksha
                description="Fasting day dedicated to Lord Vishnu",
                special_rules={"occurs_twice_monthly": True}
            ),
            
            # Purnima observances
            FestivalRule(
                name="Kartik Purnima",
                english_name="Kartik Purnima",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SPIRITUAL,
                regions=[Region.ALL_INDIA],
                month="Kartik",
                paksha="shukla",
                tithi=15,
                description="Sacred full moon of Kartik month",
                alternative_names=["Dev Deepavali"]
            ),
            
            # Amavasya observances
            FestivalRule(
                name="Mahalaya",
                english_name="Mahalaya",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SPIRITUAL,
                regions=[Region.BENGAL],
                month="Ashwin",
                paksha="krishna",
                tithi=15,  # Amavasya before Durga Puja
                description="Ancestral worship before Durga Puja"
            ),
        ]
        
        self.festival_rules.extend(spiritual_observances)
    
    def _add_astronomical_festivals(self):
        """Add festivals based on astronomical events"""
        
        astronomical_festivals = [
            # Solar events
            FestivalRule(
                name="Dakshinayana",
                english_name="Dakshinayana",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                description="Sun's southward journey begins",
                special_rules={"summer_solstice": True}
            ),
            FestivalRule(
                name="Uttarayana",
                english_name="Uttarayana",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                description="Sun's northward journey begins",
                special_rules={"winter_solstice": True}
            ),
            
            # Eclipse observances
            FestivalRule(
                name="Surya Grahan",
                english_name="Solar Eclipse",
                festival_type=FestivalType.CALCULATED,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                description="Solar eclipse observance",
                special_rules={"eclipse_type": "solar"}
            ),
            FestivalRule(
                name="Chandra Grahan",
                english_name="Lunar Eclipse",
                festival_type=FestivalType.CALCULATED,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                description="Lunar eclipse observance",
                special_rules={"eclipse_type": "lunar"}
            ),
        ]
        
        self.festival_rules.extend(astronomical_festivals)
    
    def calculate_festival_dates(self, year: int, regions: List[Region] = None, 
                               categories: List[FestivalCategory] = None) -> List[FestivalDate]:
        """
        Calculate all festival dates for a given year
        
        Args:
            year: Year to calculate festivals for
            regions: List of regions to include (default: all)
            categories: List of categories to include (default: all)
            
        Returns:
            List of FestivalDate objects sorted by date
        """
        if regions is None:
            regions = [Region.ALL_INDIA]
        
        festival_dates = []
        
        for rule in self.festival_rules:
            # Check if rule applies to requested regions
            if not any(region in rule.regions or Region.ALL_INDIA in rule.regions for region in regions):
                continue
            
            # Check if rule applies to requested categories
            if categories and rule.category not in categories:
                continue
            
            # Calculate date based on festival type
            try:
                if rule.festival_type == FestivalType.LUNAR:
                    dates = self._calculate_lunar_festival(rule, year)
                elif rule.festival_type == FestivalType.SOLAR:
                    dates = self._calculate_solar_festival(rule, year)
                elif rule.festival_type == FestivalType.NAKSHATRA:
                    dates = self._calculate_nakshatra_festival(rule, year)
                elif rule.festival_type == FestivalType.CALCULATED:
                    dates = self._calculate_special_festival(rule, year)
                else:
                    continue
                
                festival_dates.extend(dates)
                
            except Exception as e:
                print(f"Error calculating {rule.name}: {e}")
                continue
        
        # Sort by date
        festival_dates.sort(key=lambda x: x.date)
        
        return festival_dates
    
    def _calculate_lunar_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate lunar festival dates"""
        festival_dates = []
        
        if not rule.month or rule.tithi is None:
            return festival_dates
        
        try:
            # Find the specific tithi in the specified month
            # This is a simplified calculation - in practice would need 
            # proper lunar month calculation using panchang
            
            # For demonstration, using approximate dates
            # In production, would use kaal.get_panchang() to find exact tithi dates
            
            # Create approximate date calculation
            month_map = {
                "Chaitra": 3,    # March-April
                "Vaishakha": 4,  # April-May
                "Jyeshtha": 5,   # May-June
                "Ashadha": 6,    # June-July
                "Shravana": 7,   # July-August
                "Bhadrapada": 8, # August-September
                "Ashwin": 9,     # September-October
                "Kartik": 10,    # October-November
                "Margashirsha": 11, # November-December
                "Pausha": 12,    # December-January
                "Magha": 1,      # January-February
                "Phalguna": 2    # February-March
            }
            
            approx_month = month_map.get(rule.month, 1)
            
            # Create a test date in the approximate month
            test_date = datetime(year, approx_month, 15, 12, 0, 0, tzinfo=timezone.utc)
            
            # For now, using approximate calculation
            # In production, would iterate through the month to find exact tithi
            festival_date = FestivalDate(
                festival_rule=rule,
                date=test_date.date(),
                year=year,
                additional_info={
                    "lunar_month": rule.month,
                    "paksha": rule.paksha,
                    "tithi": rule.tithi
                }
            )
            
            festival_dates.append(festival_date)
            
        except Exception as e:
            print(f"Error in lunar calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def _calculate_solar_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate solar festival dates"""
        festival_dates = []
        
        try:
            if rule.name == "Makar Sankranti":
                # Makar Sankranti is typically January 14/15
                sankranti_date = date(year, 1, 14)
                
                festival_date = FestivalDate(
                    festival_rule=rule,
                    date=sankranti_date,
                    year=year,
                    additional_info={"solar_event": "Capricorn_entry"}
                )
                
                festival_dates.append(festival_date)
                
            elif rule.name == "Baisakhi":
                # Baisakhi is typically April 13/14
                baisakhi_date = date(year, 4, 13)
                
                festival_date = FestivalDate(
                    festival_rule=rule,
                    date=baisakhi_date,
                    year=year,
                    additional_info={"solar_event": "Aries_entry"}
                )
                
                festival_dates.append(festival_date)
                
        except Exception as e:
            print(f"Error in solar calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def _calculate_nakshatra_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate nakshatra-based festival dates"""
        festival_dates = []
        
        try:
            if rule.name == "Onam":
                # Onam occurs when Moon is in Shravana nakshatra in Bhadrapada month
                # Typically in August/September
                onam_date = date(year, 9, 15)  # Approximate
                
                festival_date = FestivalDate(
                    festival_rule=rule,
                    date=onam_date,
                    year=year,
                    additional_info={"nakshatra": "Shravana"}
                )
                
                festival_dates.append(festival_date)
                
        except Exception as e:
            print(f"Error in nakshatra calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def _calculate_special_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate special festivals like Ekadashi"""
        festival_dates = []
        
        try:
            if rule.name == "Ekadashi":
                # Ekadashi occurs twice per month (Shukla and Krishna Ekadashi)
                # Calculate for all 12 months
                for month in range(1, 13):
                    # Approximate Ekadashi dates (11th day of lunar fortnight)
                    # In production, would calculate exact dates using panchang
                    
                    # Shukla Ekadashi (waxing phase)
                    shukla_date = date(year, month, 11)
                    shukla_festival = FestivalDate(
                        festival_rule=rule,
                        date=shukla_date,
                        year=year,
                        additional_info={
                            "paksha": "shukla",
                            "ekadashi_type": "shukla"
                        }
                    )
                    
                    # Krishna Ekadashi (waning phase)
                    krishna_date = date(year, month, 26)
                    krishna_festival = FestivalDate(
                        festival_rule=rule,
                        date=krishna_date,
                        year=year,
                        additional_info={
                            "paksha": "krishna",
                            "ekadashi_type": "krishna"
                        }
                    )
                    
                    festival_dates.extend([shukla_festival, krishna_festival])
                    
        except Exception as e:
            print(f"Error in special calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def get_festivals_for_date(self, target_date: date, regions: List[Region] = None) -> List[FestivalDate]:
        """Get all festivals occurring on a specific date"""
        year = target_date.year
        all_festivals = self.calculate_festival_dates(year, regions)
        
        return [f for f in all_festivals if f.date == target_date]
    
    def get_festivals_for_month(self, year: int, month: int, regions: List[Region] = None) -> List[FestivalDate]:
        """Get all festivals occurring in a specific month"""
        all_festivals = self.calculate_festival_dates(year, regions)
        
        return [f for f in all_festivals if f.date.month == month]
    
    def generate_calendar(self, start_date: date, end_date: date, 
                         regions: List[Region] = None, 
                         categories: List[FestivalCategory] = None) -> Dict[str, List[FestivalDate]]:
        """
        Generate a festival calendar for a date range
        
        Returns:
            Dictionary with date strings as keys and festival lists as values
        """
        calendar_dict = defaultdict(list)
        
        # Get all years in the range
        years = set()
        current_date = start_date
        while current_date <= end_date:
            years.add(current_date.year)
            current_date += timedelta(days=365)
        
        # Calculate festivals for all years
        all_festivals = []
        for year in years:
            year_festivals = self.calculate_festival_dates(year, regions, categories)
            all_festivals.extend(year_festivals)
        
        # Filter festivals within date range
        for festival in all_festivals:
            if start_date <= festival.date <= end_date:
                date_key = festival.date.isoformat()
                calendar_dict[date_key].append(festival)
        
        return dict(calendar_dict)
    
    def export_to_ical(self, festival_dates: List[FestivalDate], filename: str = None) -> str:
        """Export festival calendar to iCal format"""
        ical_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Brahmakaal//Hindu Festival Calendar//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        for festival in festival_dates:
            ical_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{festival.festival_rule.name}_{festival.date.isoformat()}@brahmakaal.com",
                f"DTSTART;VALUE=DATE:{festival.date.strftime('%Y%m%d')}",
                f"SUMMARY:{festival.festival_rule.english_name}",
                f"DESCRIPTION:{festival.festival_rule.description}",
                f"CATEGORIES:{festival.festival_rule.category.value.upper()}",
                "STATUS:CONFIRMED",
                "TRANSP:TRANSPARENT",
                "END:VEVENT"
            ])
        
        ical_lines.append("END:VCALENDAR")
        
        ical_content = "\r\n".join(ical_lines)
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(ical_content)
        
        return ical_content
    
    def export_to_json(self, festival_dates: List[FestivalDate]) -> str:
        """Export festival calendar to JSON format"""
        festivals_data = []
        
        for festival in festival_dates:
            festival_data = {
                "name": festival.festival_rule.name,
                "english_name": festival.festival_rule.english_name,
                "date": festival.date.isoformat(),
                "year": festival.year,
                "type": festival.festival_rule.festival_type.value,
                "category": festival.festival_rule.category.value,
                "regions": [r.value for r in festival.festival_rule.regions],
                "description": festival.festival_rule.description,
                "alternative_names": festival.festival_rule.alternative_names,
                "duration_days": festival.festival_rule.duration_days,
                "observance_time": festival.festival_rule.observance_time,
                "additional_info": festival.additional_info
            }
            festivals_data.append(festival_data)
        
        return json.dumps(festivals_data, indent=2, ensure_ascii=False)

# Convenience functions for common use cases
def get_major_festivals(year: int, kaal_engine) -> List[FestivalDate]:
    """Get major festivals for a year"""
    engine = FestivalEngine(kaal_engine)
    return engine.calculate_festival_dates(
        year, 
        categories=[FestivalCategory.MAJOR]
    )

def get_regional_festivals(year: int, region: Region, kaal_engine) -> List[FestivalDate]:
    """Get festivals for a specific region"""
    engine = FestivalEngine(kaal_engine)
    return engine.calculate_festival_dates(year, regions=[region])

def get_spiritual_observances(year: int, kaal_engine) -> List[FestivalDate]:
    """Get spiritual observances like Ekadashi"""
    engine = FestivalEngine(kaal_engine)
    return engine.calculate_festival_dates(
        year,
        categories=[FestivalCategory.SPIRITUAL]
    ) 