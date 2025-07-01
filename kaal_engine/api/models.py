"""
Pydantic Models for Brahmakaal API
Request and Response models with validation
"""

from datetime import datetime as DateTime
from datetime import date as Date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

# Enums for API
class AyanamshaSystem(str, Enum):
    LAHIRI = "LAHIRI"
    RAMAN = "RAMAN"
    KRISHNAMURTI = "KRISHNAMURTI"
    YUKTESHWAR = "YUKTESHWAR"
    SURYASIDDHANTA = "SURYASIDDHANTA"
    FAGAN_BRADLEY = "FAGAN_BRADLEY"
    DELUCE = "DELUCE"
    PUSHYA_PAKSHA = "PUSHYA_PAKSHA"
    GALACTIC_CENTER = "GALACTIC_CENTER"
    TRUE_CITRA = "TRUE_CITRA"

class MuhurtaType(str, Enum):
    MARRIAGE = "marriage"
    BUSINESS = "business"
    TRAVEL = "travel"
    EDUCATION = "education"
    PROPERTY = "property"
    GENERAL = "general"

class FestivalCategory(str, Enum):
    MAJOR = "major"
    RELIGIOUS = "religious"
    SEASONAL = "seasonal"
    REGIONAL = "regional"
    SPIRITUAL = "spiritual"
    CULTURAL = "cultural"
    ASTRONOMICAL = "astronomical"

class Region(str, Enum):
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

# Request Models
class PanchangRequest(BaseModel):
    """Request model for panchang calculation"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    date: Date = Field(..., description="Date for calculation")
    time: Optional[str] = Field(None, description="Time in HH:MM:SS format (optional)")
    elevation: float = Field(0.0, ge=-1000, le=10000, description="Elevation in meters")
    ayanamsha: AyanamshaSystem = Field(AyanamshaSystem.LAHIRI, description="Ayanamsha system")
    timezone_offset: float = Field(0.0, ge=-12, le=12, description="Timezone offset in hours")

class MuhurtaRequest(BaseModel):
    """Request model for muhurta calculation"""
    muhurta_type: MuhurtaType = Field(..., description="Type of muhurta")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    start_date: DateTime = Field(..., description="Start date for search")
    end_date: DateTime = Field(..., description="End date for search")
    duration_minutes: int = Field(60, ge=15, le=1440, description="Duration in minutes")
    min_quality: str = Field("good", description="Minimum quality level")
    max_results: int = Field(10, ge=1, le=50, description="Maximum number of results")

class FestivalRequest(BaseModel):
    """Request model for festival calendar"""
    year: int = Field(..., ge=1900, le=2100, description="Year for calendar")
    month: Optional[int] = Field(None, ge=1, le=12, description="Specific month (optional)")
    regions: List[Region] = Field([Region.ALL_INDIA], description="Regions to include")
    categories: List[FestivalCategory] = Field([FestivalCategory.MAJOR], description="Categories to include")
    export_format: str = Field("json", description="Export format: json, ical, csv")

# Response Models
class PlanetaryPosition(BaseModel):
    """Planetary position data"""
    longitude: float = Field(..., description="Longitude in degrees")
    latitude: float = Field(..., description="Latitude in degrees")
    rashi: str = Field(..., description="Zodiac sign")
    nakshatra: str = Field(..., description="Nakshatra")

class TimeData(BaseModel):
    """Time-related data"""
    start: DateTime
    end: DateTime

class PanchangResponse(BaseModel):
    """Response model for panchang calculation"""
    # Basic panchang elements
    tithi: float = Field(..., description="Tithi (lunar day)")
    tithi_name: str = Field(..., description="Tithi name")
    nakshatra: str = Field(..., description="Nakshatra (lunar mansion)")
    nakshatra_lord: str = Field(..., description="Nakshatra ruling planet")
    yoga: float = Field(..., description="Yoga")
    yoga_name: str = Field(..., description="Yoga name")
    karana: float = Field(..., description="Karana")
    karana_name: str = Field(..., description="Karana name")
    
    # Solar calculations
    sunrise: DateTime = Field(..., description="Sunrise time")
    sunset: DateTime = Field(..., description="Sunset time")
    solar_noon: DateTime = Field(..., description="Solar noon time")
    day_length: float = Field(..., description="Day length in hours")
    
    # Lunar calculations
    moonrise: Optional[DateTime] = Field(None, description="Moonrise time")
    moonset: Optional[DateTime] = Field(None, description="Moonset time")
    moon_phase: str = Field(..., description="Moon phase")
    moon_illumination: float = Field(..., description="Moon illumination percentage")
    
    # Time periods
    rahu_kaal: TimeData = Field(..., description="Rahu Kaal period")
    gulika_kaal: TimeData = Field(..., description="Gulika Kaal period")
    yamaganda_kaal: TimeData = Field(..., description="Yamaganda Kaal period")
    brahma_muhurta: TimeData = Field(..., description="Brahma Muhurta period")
    abhijit_muhurta: TimeData = Field(..., description="Abhijit Muhurta period")
    
    # Planetary positions
    graha_positions: Dict[str, PlanetaryPosition] = Field(..., description="All planetary positions")
    
    # Advanced calculations
    ayanamsha: float = Field(..., description="Ayanamsha value")
    local_mean_time: str = Field(..., description="Local mean time")
    sidereal_time: float = Field(..., description="Local sidereal time")
    rashi_of_moon: str = Field(..., description="Moon's zodiac sign")
    rashi_of_sun: str = Field(..., description="Sun's zodiac sign")
    season: str = Field(..., description="Current season")
    
    # Metadata
    calculation_time_ms: int = Field(..., description="Calculation time in milliseconds")
    location: Dict[str, float] = Field(..., description="Location data")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

class MuhurtaResult(BaseModel):
    """Single muhurta result"""
    datetime: DateTime = Field(..., description="Recommended date and time")
    quality: str = Field(..., description="Quality level")
    score: float = Field(..., description="Score (0-100)")
    description: str = Field(..., description="Description")
    duration_minutes: int = Field(..., description="Duration in minutes")
    factors: Dict[str, Any] = Field(..., description="Analysis factors")
    recommendations: List[str] = Field(..., description="Recommendations")
    warnings: List[str] = Field(..., description="Warnings")

class MuhurtaResponse(BaseModel):
    """Response model for muhurta calculation"""
    request_summary: Dict[str, Any] = Field(..., description="Request summary")
    results: List[MuhurtaResult] = Field(..., description="Muhurta results")
    total_found: int = Field(..., description="Total results found")
    calculation_time_ms: int = Field(..., description="Calculation time in milliseconds")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

class FestivalData(BaseModel):
    """Single festival data"""
    name: str = Field(..., description="Festival name")
    english_name: str = Field(..., description="English name")
    date: Date = Field(..., description="Festival date")
    category: str = Field(..., description="Festival category")
    regions: List[str] = Field(..., description="Applicable regions")
    description: str = Field(..., description="Festival description")
    alternative_names: List[str] = Field([], description="Alternative names")
    duration_days: int = Field(1, description="Duration in days")
    observance_time: str = Field("full_day", description="Observance time")

class FestivalResponse(BaseModel):
    """Response model for festival calendar"""
    request_summary: Dict[str, Any] = Field(..., description="Request summary")
    festivals: List[FestivalData] = Field(..., description="Festival list")
    total_festivals: int = Field(..., description="Total festivals")
    export_url: Optional[str] = Field(None, description="Export file URL")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

class AyanamshaComparisonResponse(BaseModel):
    """Response model for ayanamsha comparison"""
    date: Date = Field(..., description="Comparison date")
    julian_day: float = Field(..., description="Julian day")
    ayanamsha_values: Dict[str, float] = Field(..., description="All ayanamsha values")
    differences_from_lahiri: Dict[str, float] = Field(..., description="Differences from Lahiri")
    systems_info: Dict[str, str] = Field(..., description="System descriptions")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    uptime_seconds: int = Field(..., description="Uptime in seconds")
    database_connected: bool = Field(..., description="Database connection status")
    cache_connected: bool = Field(..., description="Cache connection status")
    ephemeris_loaded: bool = Field(..., description="Ephemeris file status")
    timestamp: DateTime = Field(..., description="Response timestamp")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: DateTime = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracking") 