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
import logging

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
    evening_start: bool = False  # When True, DP assigns to the day the tithi STARTED (after sunset)

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
    
    def __init__(self, kaal_engine, lat: float = 23.1765, lod: float = 75.7885,
                 timezone_offset: float = 5.5, elevation: float = 0.0):
        """
        Initialize festival engine with astronomical calculations
        
        Args:
            kaal_engine: Instance of Kaal class for astronomical calculations
            lat: Latitude of observation (default: Ujjain, traditional center)
            lon: Longitude of observation
            timezone_offset: Hours from UTC (default: IST = 5.5)
            elevation: Elevation in meters
        """
        self.kaal = kaal_engine
        self.lat = lat
        self.lon = lod
        self.timezone_offset = timezone_offset
        self.elevation = elevation
        self.calendar = HinduCalendar()
        self.festival_rules = []
        self.cache = {}
        self._scanner = None
        
        # Initialize festival database
        self._initialize_festival_database()
    
    def _get_scanner(self):
        """Lazy-init TithiScanner for festival calculation"""
        if self._scanner is None:
            from kaal_engine.core.festival_scanner import TithiScanner
            self._scanner = TithiScanner(
                self.kaal, self.lat, self.lon,
                timezone_offset=self.timezone_offset,
                elevation=self.elevation
            )
        return self._scanner
    
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
        
        # All missing festivals mapped from DP reference
        self._add_all_missing_festivals()
    
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
                month="Ashwin",
                paksha="krishna",
                tithi=15,  # Amavasya
                description="Festival of lights, worship of Goddess Lakshmi",
                alternative_names=["Deepavali", "Lakshmi Puja"],
                evening_start=True
            ),
            FestivalRule(
                name="Govardhan Puja",
                english_name="Govardhan Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Margashirsha",  # Amanta: was Kartik in Purnimanta
                paksha="shukla",
                tithi=1,
                description="Fourth day of Diwali, worship of Mount Govardhan",
                alternative_names=["Annakut"],
                special_rules={
                    "kshaya_tithi": True,
                    "offset_from_festival": "Diwali",
                    "offset_days": 1
                }
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
                month="Phalguna",  # Amanta: was Chaitra in Purnimanta
                paksha="krishna",
                tithi=1,
                description="Festival of colors, celebration of spring",
                alternative_names=["Rangwali Holi", "Dhulandi"],
                special_rules={
                    "kshaya_tithi": True,
                    "offset_from_festival": "Holika Dahan",
                    "offset_days": 1
                }
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
                name="Sharad Saraswati Puja",
                english_name="Sharad Saraswati Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=7,
                description="Saraswati Puja during Sharad Navaratri"
            ),
            FestivalRule(
                name="Maha Navami",
                english_name="Maha Navami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=9,
                description="Ninth day of Sharad Navaratri",
                alternative_names=["Durga Puja (Maha Navami)"]
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
            FestivalRule(
                name="Anant Chaturdashi",
                english_name="Anant Chaturdashi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=14,
                description="Ganesh Visarjan, worship of the eternal one",
                alternative_names=["Ganesh Visarjan"]
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
                name="Vasant Panchami",
                english_name="Vasant Panchami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.BENGAL, Region.EAST_INDIA],
                month="Magha",
                paksha="shukla",
                tithi=5,
                description="Arrival of spring, worship of Goddess Saraswati",
                alternative_names=["Basant Panchami", "Saraswati Puja"]
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
                name="Vasant Panchami",
                english_name="Vasant Panchami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.ALL_INDIA],
                month="Magha",
                paksha="shukla",
                tithi=5,
                description="Arrival of spring, worship of Saraswati",
                alternative_names=["Basant Panchami", "Saraswati Puja"]
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
        """Calculate lunar festival dates using TithiScanner"""
        festival_dates = []
        
        if not rule.month or rule.tithi is None:
            return festival_dates
        
        try:
            # Handle kshaya tithi: compute as offset from another festival
            special = rule.special_rules or {}
            if special.get("kshaya_tithi"):
                offset_festival = special.get("offset_from_festival")
                offset_days = special.get("offset_days", 1)
                if offset_festival:
                    for other_rule in self.festival_rules:
                        if other_rule.name == offset_festival:
                            base_dates = self._calculate_lunar_festival(other_rule, year)
                            if base_dates:
                                base_date = base_dates[0].date
                                result = base_date + timedelta(days=offset_days)
                                festival_dates.append(FestivalDate(
                                    festival_rule=rule,
                                    date=result,
                                    year=year,
                                    additional_info={
                                        "lunar_month": rule.month,
                                        "paksha": rule.paksha,
                                        "tithi": rule.tithi,
                                        "kshaya_from": str(base_date),
                                        "offset_days": offset_days
                                    }
                                ))
                                return festival_dates
            
            # Use cached result if available
            cache_key = f"lunar_{year}_{rule.month}_{rule.paksha}_{rule.tithi}"
            if cache_key in self.cache:
                cached_date = self.cache[cache_key]
                festival_dates.append(FestivalDate(
                    festival_rule=rule,
                    date=cached_date,
                    year=year,
                    additional_info={
                        "lunar_month": rule.month,
                        "paksha": rule.paksha,
                        "tithi": rule.tithi
                    }
                ))
                return festival_dates
            
            # Use TithiScanner to find exact date
            scanner = self._get_scanner()
            result = scanner.find_tithi_date(
                year, rule.month, rule.paksha, rule.tithi,
                search_padding_days=20,
                evening_start=getattr(rule, 'evening_start', False)
            )
            
            if result:
                self.cache[cache_key] = result
                festival_dates.append(FestivalDate(
                    festival_rule=rule,
                    date=result,
                    year=year,
                    additional_info={
                        "lunar_month": rule.month,
                        "paksha": rule.paksha,
                        "tithi": rule.tithi
                    }
                ))
            else:
                print(f"Warning: Could not find date for {rule.name} "
                      f"({rule.month} {rule.paksha} {rule.tithi})")
            
        except Exception as e:
            print(f"Error in lunar calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def _calculate_solar_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate solar festival dates using Kaal engine"""
        festival_dates = []
        today = date(year, 1, 1)
        
        try:
            if rule.name == "Makar Sankranti":
                # Scan for Sun entering Makara (Capricorn) ≈ Jan 14-15
                for day in range(10, 25):
                    test_dt = datetime(year, 1, day, 12, 0, 0)
                    p = self.kaal.get_panchang(
                        self.lat, self.lon, test_dt,
                        elevation=self.elevation, timezone_offset=self.timezone_offset
                    )
                    rashi = p.get('rashi_of_sun', '')
                    if rashi == 'Makara':
                        festival_dates.append(FestivalDate(
                            festival_rule=rule, date=test_dt.date(), year=year,
                            additional_info={"solar_event": "Capricorn_entry"}
                        ))
                        return festival_dates
                        
            elif rule.name == "Baisakhi" or rule.name == "Pongal":
                # Scan for Sun entering Mesha (Aries) ≈ Apr 13-14
                for day in range(10, 20):
                    test_dt = datetime(year, 4, day, 12, 0, 0)
                    p = self.kaal.get_panchang(
                        self.lat, self.lon, test_dt,
                        elevation=self.elevation, timezone_offset=self.timezone_offset
                    )
                    rashi = p.get('rashi_of_sun', '')
                    if rashi == 'Mesha':
                        festival_dates.append(FestivalDate(
                            festival_rule=rule, date=test_dt.date(), year=year,
                            additional_info={"solar_event": "Aries_entry"}
                        ))
                        return festival_dates
            
            # Fallback for other solar festivals
            if rule.solar_month and rule.solar_day:
                approx = date(year, rule.solar_month, rule.solar_day)
                festival_dates.append(FestivalDate(
                    festival_rule=rule, date=approx, year=year,
                    additional_info={"solar_event": "approximate"}
                ))
            
        except Exception as e:
            print(f"Error in solar calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def _calculate_nakshatra_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate nakshatra-based festival dates"""
        festival_dates = []
        
        try:
            if rule.name == "Onam":
                # Scan for Shravana nakshatra in Bhadrapada month (Aug-Sep)
                scanner = self._get_scanner()
                result = scanner.find_tithi_date(year, "Bhadrapada", "shukla", 15,
                                                search_padding_days=20)
                if result:
                    # Onam is around the Purnima of Bhadrapada with specific nakshatra
                    festival_date = FestivalDate(
                        festival_rule=rule,
                        date=result,
                        year=year,
                        additional_info={"nakshatra": "Shravana"}
                    )
                    festival_dates.append(festival_date)
                else:
                    onam_date = date(year, 9, 15)
                    festival_dates.append(FestivalDate(
                        festival_rule=rule, date=onam_date, year=year,
                        additional_info={"nakshatra": "Shravana", "note": "approximate"}
                    ))
        except Exception as e:
            print(f"Error in nakshatra calculation for {rule.name}: {e}")
        
        return festival_dates
    
    def _calculate_special_festival(self, rule: FestivalRule, year: int) -> List[FestivalDate]:
        """Calculate special festivals like Ekadashi using TithiScanner"""
        festival_dates = []
        
        try:
            if rule.name == "Ekadashi":
                scanner = self._get_scanner()
                all_ekadashis = scanner.find_all_ekadashis(year)
                for ekadashi_date, month_name, paksha_name in all_ekadashis:
                    festival_date = FestivalDate(
                        festival_rule=rule,
                        date=ekadashi_date,
                        year=year,
                        additional_info={
                            "lunar_month": month_name,
                            "paksha": paksha_name,
                            "tithi": 11
                        }
                    )
                    festival_dates.append(festival_date)
                    
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
                f"UID:{festival.festival_rule.name}_{festival.date.isoformat()}@brah.ma",
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

    def _add_all_missing_festivals(self):
        """Add all remaining festivals mapped from DP reference dataset (~152 total)"""
        missing = []
        
        # ── All 12 Purnimas (full moons) ──
        purnima_months = [
            ("Pausha", "Pausha Purnima"),
            ("Magha", "Magha Purnima"),
            ("Phalguna", "Phalguna Purnima"),
            ("Chaitra", "Chaitra Purnima"),
            ("Vaishakha", "Vaishakha Purnima"),
            ("Jyeshtha", "Jyeshtha Purnima"),
            ("Ashadha", "Ashadha Purnima"),
            ("Shravana", "Shravana Purnima"),
            ("Bhadrapada", "Bhadrapada Purnima"),
            ("Ashwin", "Sharad Purnima"),  # Ashwina Purnima = Sharad Purnima
            ("Kartik", "Kartika Purnima"),
            ("Margashirsha", "Margashirsha Purnima"),
        ]
        for hmonth, name in purnima_months:
            missing.append(FestivalRule(
                name=name,
                english_name=name,
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month=hmonth,
                paksha="shukla",
                tithi=15,
                description=f"Full moon of {hmonth}"
            ))
        
        # ── All 12 Sankrantis (Sun entering each rashi) ──
        sankranti_data = [
            ("Mesha Sankranti", 1, "Solar New Year, Baisakhi"),
            ("Vrishabha Sankranti", 2, "Sun enters Taurus"),
            ("Mithuna Sankranti", 3, "Sun enters Gemini"),
            ("Karka Sankranti", 4, "Sun enters Cancer"),
            ("Simha Sankranti", 5, "Sun enters Leo"),
            ("Kanya Sankranti", 6, "Sun enters Virgo"),
            ("Tula Sankranti", 7, "Sun enters Libra"),
            ("Vrishchika Sankranti", 8, "Sun enters Scorpio"),
            ("Dhanu Sankranti", 9, "Sun enters Sagittarius"),
            ("Makara Sankranti", 10, "Winter solstice entry"),  # already exists
            ("Kumbha Sankranti", 11, "Sun enters Aquarius"),
            ("Meena Sankranti", 12, "Sun enters Pisces"),
        ]
        for name, solar_m, desc in sankranti_data:
            # Skip Makara Sankranti — already added in _add_seasonal_festivals
            if name == "Makara Sankranti":
                continue
            missing.append(FestivalRule(
                name=name,
                english_name=name,
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                solar_month=solar_m,
                solar_day=1,
                description=desc
            ))
        
        # ── All 24 named Ekadashis (12 months × shukla/krishna 11) ──
        # Krishna 11 (first half of month)
        krishna_ekadashis = [
            ("Margashirsha", "Saphala Ekadashi"),
            ("Pausha", "Pausha Putrada Ekadashi"),
            ("Magha", "Shattila Ekadashi"),
            ("Phalguna", "Jaya Ekadashi"),
            ("Chaitra", "Kamada Ekadashi"),
            ("Vaishakha", "Varuthini Ekadashi"),
            ("Jyeshtha", "Mohini Ekadashi"),
            ("Ashadha", "Yogini Ekadashi"),
            ("Shravana", "Kamika Ekadashi"),
            ("Bhadrapada", "Parsva Ekadashi"),
            ("Ashwin", "Indira Ekadashi"),
            ("Kartik", "Utpanna Ekadashi"),
        ]
        # Shukla 11 (second half of month)
        # NOTE: Pausha Shukla 11 is NOT "Pausha Putrada" — DP only uses
        # that name for Krishna 11. The Shukla 11 of Pausha period is
        # either unnamed or falls in Magha as "Vijaya Ekadashi".
        shukla_ekadashis = [
            ("Margashirsha", "Mokshada Ekadashi"),
            ("Magha", "Vijaya Ekadashi"),
            ("Phalguna", "Amalaki Ekadashi"),
            ("Chaitra", "Papamochani Ekadashi"),
            ("Vaishakha", "Apara Ekadashi"),
            ("Jyeshtha", "Nirjala Ekadashi"),
            ("Ashadha", "Devshayani Ekadashi"),
            ("Shravana", "Shravana Putrada Ekadashi"),
            ("Bhadrapada", "Aja Ekadashi"),
            ("Ashwin", "Papankusha Ekadashi"),
            ("Kartik", "Devutthana Ekadashi"),
        ]
        ekadashi_map = [
            *[(m, "krishna", n) for m, n in krishna_ekadashis],
            *[(m, "shukla", n) for m, n in shukla_ekadashis],
        ]
        for hmonth, paksha, name in ekadashi_map:
            missing.append(FestivalRule(
                name=name,
                english_name=name,
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SPIRITUAL,
                regions=[Region.ALL_INDIA],
                month=hmonth,
                paksha=paksha,
                tithi=11,
                description=f"Ekadashi fast in {hmonth} {paksha} paksha"
            ))
        
        # ── Amavasyas ──
        amavasyas = [
            FestivalRule(
                name="Mauni Amavas",
                english_name="Mauni Amavas",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Magha",
                paksha="krishna",
                tithi=15,
                description="Sacred silent full moon (actually Amavasya) of Magha"
            ),
            FestivalRule(
                name="Sarva Pitru Amavasya",
                english_name="Sarva Pitru Amavasya",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="krishna",
                tithi=15,
                description="Amavasya during Pitru Paksha for ancestor worship"
            ),
        ]
        missing.extend(amavasyas)
        
        # ── Major remaining festivals from DP that are tithi-based ──
        major_remaining = [
            # Chaturthis (tithi 4)
            FestivalRule(
                name="Sakat Chauth",
                english_name="Sakat Chauth",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.NORTH_INDIA],
                month="Magha",
                paksha="krishna",
                tithi=4,
                description="Fast for children's well-being"
            ),
            FestivalRule(
                name="Ahoi Ashtami",
                english_name="Ahoi Ashtami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=8,
                description="Fast by mothers for children's prosperity"
            ),
            # Saptamis (tithi 7)
            FestivalRule(
                name="Ratha Saptami",
                english_name="Ratha Saptami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Magha",
                paksha="shukla",
                tithi=7,
                description="Sun's birthday, Surya Jayanti, Rathotsava"
            ),
            # Ashtamis (tithi 8)
            FestivalRule(
                name="Bhishma Ashtami",
                english_name="Bhishma Ashtami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Magha",
                paksha="shukla",
                tithi=8,
                description="Bhishma Pitamah's body expired on this day"
            ),
            FestivalRule(
                name="Durga Ashtami",
                english_name="Durga Ashtami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=8,
                description="Eighth day of Navaratri, worship of Durga"
            ),
            # Tritiya (tithi 3)
            FestivalRule(
                name="Hariyali Teej",
                english_name="Hariyali Teej",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.NORTH_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=3,
                description="Monsoon festival, swinging and worship of Parvati"
            ),
            FestivalRule(
                name="Kajari Teej",
                english_name="Kajari Teej",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.NORTH_INDIA],
                month="Bhadrapada",
                paksha="krishna",
                tithi=3,
                description="Teej festival celebrated in central India"
            ),
            FestivalRule(
                name="Hartalika Teej",
                english_name="Hartalika Teej",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.NORTH_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=3,
                description="Major Teej festival, worship of Parvati and Shiva"
            ),
            # Dwadashi (tithi 12)
            FestivalRule(
                name="Govatsa Dwadashi",
                english_name="Govatsa Dwadashi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=12,
                description="Worship of cow and calf, first day of Diwali in some traditions"
            ),
            # Panchami (tithi 5)
            FestivalRule(
                name="Nag Panchami",
                english_name="Nag Panchami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=5,
                description="Worship of snakes/cobras"
            ),
            FestivalRule(
                name="Rishi Panchami",
                english_name="Rishi Panchami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.SOUTH_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=5,
                description="Worship of seven sages (Sapta Rishis)"
            ),
            # Tritiya (tithi 3, other)
            FestivalRule(
                name="Akshaya Tritiya",
                english_name="Akshaya Tritiya",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="shukla",
                tithi=3,
                description="Auspicious day for new beginnings, buying gold"
            ),
            # Dashami (tithi 10)
            FestivalRule(
                name="Vijayadashami",
                english_name="Vijayadashami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=10,
                description="Victory day, also known as Dussehra"
            ),
            # The festivals below are NOT simple tithi-based — we skip them for now
            # (they require nakshatra, specific tithi combinations, or approximations)
        ]
        missing.extend(major_remaining)

        # ── Phase 2: Remaining 30+ DP festivals (minor/regional/special) ──
        remaining_festivals = [
            # --- Simple tithi-based (lunar) ---
            FestivalRule(
                name="Ganga Dussehra",
                english_name="Ganga Dussehra",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Jyeshtha",
                paksha="shukla",
                tithi=10,
                description="Descent of Ganga to Earth, bathing festival"
            ),
            FestivalRule(
                name="Ganga Saptami",
                english_name="Ganga Saptami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="shukla",
                tithi=7,
                description="Birth of Goddess Ganga"
            ),
            FestivalRule(
                name="Gayatri Jayanti",
                english_name="Gayatri Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Jyeshtha",
                paksha="shukla",
                tithi=11,
                description="Appearance day of Goddess Gayatri"
            ),
            FestivalRule(
                name="Gita Jayanti",
                english_name="Gita Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Margashirsha",
                paksha="shukla",
                tithi=11,
                description="Birthday of Bhagavad Gita, same as Mokshada Ekadashi",
                alternative_names=["Mokshada Ekadashi"]
            ),
            FestivalRule(
                name="Jagannath Rathyatra",
                english_name="Jagannath Rath Yatra",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ODISHA],
                month="Ashadha",
                paksha="shukla",
                tithi=2,
                description="Chariot festival of Lord Jagannath",
                alternative_names=["Rath Yatra"]
            ),
            FestivalRule(
                name="Kalabhairav Jayanti",
                english_name="Kalabhairav Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Margashirsha",
                paksha="krishna",
                tithi=8,
                description="Birthday of Lord Kalabhairava"
            ),
            FestivalRule(
                name="Narasimha Jayanti",
                english_name="Narasimha Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="shukla",
                tithi=14,
                description="Appearance day of Lord Narasimha"
            ),
            FestivalRule(
                name="Parashurama Jayanti",
                english_name="Parashurama Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="shukla",
                tithi=3,
                description="Birthday of Lord Parashurama"
            ),
            FestivalRule(
                name="Radha Ashtami",
                english_name="Radha Ashtami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=8,
                description="Birthday of Radha Rani"
            ),
            FestivalRule(
                name="Sita Navami",
                english_name="Sita Navami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="shukla",
                tithi=9,
                description="Appearance day of Goddess Sita"
            ),
            FestivalRule(
                name="Sheetala Ashtami",
                english_name="Sheetala Ashtami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.NORTH_INDIA],
                month="Chaitra",
                paksha="krishna",
                tithi=8,
                description="Worship of Goddess Sheetala"
            ),
            FestivalRule(
                name="Shani Jayanti",
                english_name="Shani Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Jyeshtha",
                paksha="krishna",
                tithi=15,
                description="Birthday of Lord Shani",
                evening_start=True
            ),
            FestivalRule(
                name="Swaminarayan Jayanti",
                english_name="Swaminarayan Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.GUJARAT],
                month="Chaitra",
                paksha="shukla",
                tithi=9,
                description="Birthday of Lord Swaminarayan"
            ),
            FestivalRule(
                name="Tulasi Vivah",
                english_name="Tulasi Vivah",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Kartik",
                paksha="shukla",
                tithi=12,
                description="Marriage of Tulasi plant to Lord Vishnu"
            ),
            FestivalRule(
                name="Vivah Panchami",
                english_name="Vivah Panchami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Margashirsha",
                paksha="shukla",
                tithi=5,
                description="Marriage anniversary of Lord Rama and Sita"
            ),
            FestivalRule(
                name="Vat Savitri Vrat",
                english_name="Vat Savitri Vrat",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.NORTH_INDIA],
                month="Jyeshtha",
                paksha="krishna",
                tithi=15,
                description="Savitri fast for husband's longevity, Amavasya",
                evening_start=True
            ),
            FestivalRule(
                name="Yamuna Chhath",
                english_name="Yamuna Chhath",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=6,
                description="Worship of Yamuna river, Chhath Puja alternative"
            ),
            FestivalRule(
                name="Kali Chaudas",
                english_name="Kali Chaudas",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.GUJARAT],
                month="Kartik",
                paksha="krishna",
                tithi=14,
                description="Gujarati Diwali, worship of Kali",
                alternative_names=["Narak Chaturdashi"]
            ),
            FestivalRule(
                name="Narada Jayanti",
                english_name="Narada Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="krishna",
                tithi=1,
                description="Birthday of Sage Narada"
            ),
            # --- Solar festivals ---
            FestivalRule(
                name="Solar New Year",
                english_name="Solar New Year",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                solar_month=1,
                solar_day=1,
                description="Sun enters Mesha (Aries) — solar new year"
            ),
        ]
        missing.extend(remaining_festivals)

        # ── Phase 3: Critical aliases & remaining tithi-based festivals ──
        critical_remaining = [
            # --- Chhath Puja & Balarama Jayanti ---
            FestivalRule(
                name="Chhath Puja",
                english_name="Chhath Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.EAST_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=6,
                description="Sun worship festival of Bihar/U.P., Kartik Krishna Shashthi",
                observance_time="sunset",
                evening_start=True
            ),
            FestivalRule(
                name="Balarama Jayanti",
                english_name="Balarama Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="krishna",
                tithi=7,
                description="Birthday of Balarama, Krishna's elder brother"
            ),
            FestivalRule(
                name="Vishwakarma Puja",
                english_name="Vishwakarma Puja",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.ALL_INDIA],
                solar_month=6,  # Kanya Sankranti = Sun enters Kanya (Virgo)
                solar_day=1,
                description="Worship of divine architect Vishwakarma on Kanya Sankranti"
            ),
            FestivalRule(
                name="Gangaur",
                english_name="Gangaur",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.RAJASTHAN],
                month="Chaitra",
                paksha="shukla",
                tithi=3,
                description="Rajasthani festival of Gauri and Ishar"
            ),
            FestivalRule(
                name="Gauri Puja",
                english_name="Gauri Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.WEST_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=3,
                description="Goddess Gauri worship in western India"
            ),
            FestivalRule(
                name="Raksha Bandhan",
                english_name="Raksha Bandhan",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=15,
                description="Sister ties rakhi on brother's wrist",
                alternative_names=["Rakhi", "Raksha Bandhana"]
            ),
            # --- Alias entries for DP name variants ---
            # Each maps to the same tithi as the canonical rule but with the DP name
            FestivalRule(
                name="Bhaiya Dooj",
                english_name="Bhaiya Dooj",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Margashirsha",
                paksha="shukla",
                tithi=2,
                description="Sisters pray for brothers, same as Bhai Dooj"
            ),
            FestivalRule(
                name="Basoda",
                english_name="Basoda",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.NORTH_INDIA],
                month="Bhadrapada",
                paksha="krishna",
                tithi=8,
                description="Day after Krishna Janmashtami in some traditions"
            ),
            FestivalRule(
                name="Kansa Vadh",
                english_name="Kansa Vadh",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.NORTH_INDIA],
                month="Bhadrapada",
                paksha="krishna",
                tithi=9,
                description="Killing of Kansa by Krishna"
            ),
            FestivalRule(
                name="Rama Ekadashi",
                english_name="Rama Ekadashi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.SPIRITUAL,
                regions=[Region.ALL_INDIA],
                month="Margashirsha",
                paksha="krishna",
                tithi=11,
                description="Ekadashi of Margashirsha Krishna paksha",
                alternative_names=["Saphala Ekadashi"]
            ),
            FestivalRule(
                name="Ganesh Visarjan",
                english_name="Ganesh Visarjan",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.MAHARASHTRA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=14,
                description="Immersion of Ganesh idols, same as Anant Chaturdashi",
                alternative_names=["Anant Chaturdashi", "Ganesh Visarjan"]
            ),
            FestivalRule(
                name="Saraswati Avahan",
                english_name="Saraswati Avahan",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=7,
                description="Invocation of Saraswati on Navaratri Saptami",
                alternative_names=["Sharad Saraswati Puja"]
            ),
            # Note: Somavati Amavasya depends on weekday, not month;
            # cannot compute with simple tithi-based rule. Skip.
        ]
        missing.extend(critical_remaining)

        # ── Phase 4: Name-aliases for remaining DP variants ──
        # These are same-tithi aliases that different regions call by different names
        alias_festivals = [
            FestivalRule(
                name="Ashwina Purnima",
                english_name="Ashwina Purnima",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=15,
                description="Full moon of Ashwin month, also called Sharad Purnima",
                alternative_names=["Sharad Purnima"]
            ),
            FestivalRule(
                name="Chhoti Holi",
                english_name="Chhoti Holi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Phalguna",
                paksha="shukla",
                tithi=15,
                description="Holika Dahan eve, same day",
                evening_start=True
            ),
            FestivalRule(
                name="Dattatreya Jayanti",
                english_name="Dattatreya Jayanti",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Margashirsha",
                paksha="shukla",
                tithi=15,
                description="Birthday of Lord Dattatreya, same as Margashirsha Purnima"
            ),
            FestivalRule(
                name="Hanuman Janmotsava",
                english_name="Hanuman Janmotsava",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=15,
                description="Birthday of Lord Hanuman, same as Chaitra Purnima"
            ),
            FestivalRule(
                name="Buddha Purnima",
                english_name="Buddha Purnima",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Vaishakha",
                paksha="shukla",
                tithi=15,
                description="Birth of Buddha, same as Vaishakha Purnima"
            ),
            FestivalRule(
                name="Pitrupaksha Begins",
                english_name="Pitrupaksha Begins",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Bhadrapada",
                paksha="shukla",
                tithi=15,
                description="Start of Pitru Paksha, same as Bhadrapada Purnima"
            ),
            FestivalRule(
                name="Vat Purnima Vrat",
                english_name="Vat Purnima Vrat",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.WEST_INDIA],
                month="Jyeshtha",
                paksha="shukla",
                tithi=15,
                description="Vat Purnima Vrat, same as Jyeshtha Purnima"
            ),
            FestivalRule(
                name="Kojagara Puja",
                english_name="Kojagara Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.BENGAL],
                month="Ashwin",
                paksha="shukla",
                tithi=15,
                description="Bengali Lakshmi Puja on Sharad Purnima"
            ),
            FestivalRule(
                name="Lakshmi Puja",
                english_name="Lakshmi Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="krishna",
                tithi=15,
                description="Worship of Lakshmi on Diwali Amavasya",
                evening_start=True
            ),
            FestivalRule(
                name="Rakhi",
                english_name="Rakhi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.ALL_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=15,
                description="Raksha Bandhan, same as Shravana Purnima"
            ),
            FestivalRule(
                name="Narak Chaturdashi",
                english_name="Narak Chaturdashi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=14,
                description="Choti Diwali, defeat of Narakasura",
                alternative_names=["Naraka Chaturdashi", "Choti Diwali"],
                evening_start=True
            ),
            FestivalRule(
                name="Karwa Chauth",
                english_name="Karwa Chauth",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Kartik",
                paksha="krishna",
                tithi=4,
                description="North Indian wives' fast, alternate spelling of Karva Chauth"
            ),
            FestivalRule(
                name="Makara Sankranti",
                english_name="Makara Sankranti",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.SEASONAL,
                regions=[Region.ALL_INDIA],
                solar_month=10,
                solar_day=1,
                description="Sun enters Capricorn, alternate name for Makar Sankranti"
            ),
            FestivalRule(
                name="Ugadi",
                english_name="Ugadi",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.SOUTH_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=1,
                description="Telugu and Kannada New Year, same as Gudi Padwa"
            ),
            FestivalRule(
                name="Nutan Varsh Prarambha",
                english_name="Nutan Varsh Prarambha",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.GUJARAT],
                month="Kartik",
                paksha="shukla",
                tithi=1,
                description="Gujarati New Year, day after Diwali"
            ),
            FestivalRule(
                name="Navratri Begins",
                english_name="Navratri Begins",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Ashwin",
                paksha="shukla",
                tithi=1,
                description="First day of Navaratri",
                alternative_names=["Navaratri Begins"]
            ),
            FestivalRule(
                name="Saraswati Puja",
                english_name="Saraswati Puja",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.REGIONAL,
                regions=[Region.BENGAL],
                month="Magha",
                paksha="shukla",
                tithi=5,
                description="Worship of Saraswati on Vasant Panchami",
                alternative_names=["Vasant Panchami", "Basant Panchami"]
            ),
            FestivalRule(
                name="Varalakshmi Vrat",
                english_name="Varalakshmi Vrat",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.RELIGIOUS,
                regions=[Region.SOUTH_INDIA],
                month="Shravana",
                paksha="shukla",
                tithi=15,
                description="South Indian women's worship of Lakshmi",
                alternative_names=["Varalakshmi Vratam"]
            ),
            FestivalRule(
                name="Chaitra Navratri",
                english_name="Chaitra Navratri",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.NORTH_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=1,
                description="Nine nights starting Chaitra Shukla Pratipada",
                duration_days=9,
                alternative_names=["Chaitra Navaratri"]
            ),
            # Note: Gauna Ekadashis, Padmini Ekadashi, Parama Ekadashi
            # are adhika-month variants — cannot compute without adhika month detection.
            # Jyeshtha Adhika Purnima is an adhika-month Purnima — same issue.
            # All eclipses need Skyfield — skip.
            # Kumbh Melas are multi-year events — skip.
            # Somavati Amavasya is weekday-dependent — skip.
            FestivalRule(
                name="Rama Navami",
                english_name="Rama Navami",
                festival_type=FestivalType.LUNAR,
                category=FestivalCategory.MAJOR,
                regions=[Region.ALL_INDIA],
                month="Chaitra",
                paksha="shukla",
                tithi=9,
                description="Rama Navami (alternate spelling of Ram Navami)",
                alternative_names=["Ram Navami"]
            ),
            FestivalRule(
                name="Agastya Arghya",
                english_name="Agastya Arghya",
                festival_type=FestivalType.SOLAR,
                category=FestivalCategory.ASTRONOMICAL,
                regions=[Region.ALL_INDIA],
                solar_month=10,  # Approx: when Canopus rises after Makar Sankranti
                solar_day=1,
                description="Offering to Sage Agastya when star Canopus rises"
            ),
        ]
        missing.extend(alias_festivals)

        self.festival_rules.extend(missing)
        logger = logging.getLogger(__name__)
        logger.info(f"Added {len(missing)} missing DP-mapped festival rules")


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