"""
Pydantic Models for Brahmakaal API
Request and Response models with validation
"""

from datetime import datetime as DateTime
from datetime import date as Date
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

# Type alias for flexible time fields (datetime or human-readable string)
TimeField = Union[DateTime, str]

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
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees", examples=[28.6139])
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees", examples=[77.209])
    date: str = Field(..., description="Date in YYYY-MM-DD format", examples=["2024-03-15"])
    time: str = Field(..., description="Time in HH:MM:SS format", examples=["14:30:00"])
    elevation: float = Field(default=0.0, ge=-1000, le=10000, description="Elevation in meters", examples=[0.0])
    timezone_offset: float = Field(default=5.5, description="Timezone offset from UTC in hours", examples=[5.5])
    ayanamsha: str = Field(default="LAHIRI", description="Ayanamsha system to use", examples=["LAHIRI"])
    human_readable_times: bool = Field(default=False, description="Return times in human-readable format (e.g., '5:41 AM' instead of ISO)", examples=[True])

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

class EndTimeData(BaseModel):
    """End time data for tithi/nakshatra"""
    end_time: DateTime = Field(..., description="Exact end time")
    hours_remaining: int = Field(..., description="Hours remaining")
    minutes_remaining: int = Field(..., description="Minutes remaining")
    percentage_complete: float = Field(..., description="Percentage complete (0-100)")

class TraditionalCalendarYears(BaseModel):
    """Traditional Hindu calendar years"""
    vikram_samvat: int = Field(..., description="Vikram Samvat year")
    shaka_samvat: int = Field(..., description="Shaka Samvat year")
    kali_yuga: int = Field(..., description="Kali Yuga year")
    bengali_san: int = Field(..., description="Bengali San year")
    tamil_year: str = Field(..., description="Tamil calendar year name")

class TarabalaData(BaseModel):
    """Tarabala and Chandrabala calculations"""
    tarabala: str = Field(..., description="Tarabala classification (Janma, Sampat, Vipat, etc.)")
    tarabala_number: int = Field(..., description="Tarabala number (1-9)")
    tarabala_result: str = Field(..., description="Favorable/Unfavorable result")
    chandrabala: str = Field(..., description="Chandrabala classification")
    chandrabala_points: int = Field(..., description="Chandrabala points (0-6)")

class ShoolData(BaseModel):
    """Shool direction and Nivas calculations"""
    shool_direction: str = Field(..., description="Shool direction (North, South, East, West)")
    shool_deity: str = Field(..., description="Ruling deity of the direction")
    nivas: str = Field(..., description="Current nivas (residence) of deity")
    favorable_direction: str = Field(..., description="Most favorable direction for today")

class PanchakaData(BaseModel):
    """Panchaka classification"""
    panchaka_type: str = Field(..., description="Panchaka type (Agni, Raja, Mrityu, etc.)")
    panchaka_description: str = Field(..., description="Description of the panchaka")
    favorable_activities: List[str] = Field(..., description="Favorable activities")
    activities_to_avoid: List[str] = Field(..., description="Activities to avoid")

class PanchangResponse(BaseModel):
    """Response model for panchang calculation"""
    # Basic panchang elements
    tithi: float = Field(..., description="Tithi (lunar day)")
    tithi_name: str = Field(..., description="Tithi name")
    tithi_end_time: EndTimeData = Field(..., description="Tithi end time details")
    nakshatra: str = Field(..., description="Nakshatra (lunar mansion)")
    nakshatra_lord: str = Field(..., description="Nakshatra ruling planet")
    nakshatra_end_time: EndTimeData = Field(..., description="Nakshatra end time details")
    yoga: float = Field(..., description="Yoga")
    yoga_name: str = Field(..., description="Yoga name")
    karana: float = Field(..., description="Karana")
    karana_name: str = Field(..., description="Karana name")
    
    # Solar calculations
    sunrise: TimeField = Field(..., description="Sunrise time (DateTime or human-readable string)")
    sunset: TimeField = Field(..., description="Sunset time (DateTime or human-readable string)")
    solar_noon: TimeField = Field(..., description="Solar noon time (DateTime or human-readable string)")
    day_length: float = Field(..., description="Day length in hours")
    
    # Lunar calculations
    moonrise: Optional[TimeField] = Field(None, description="Moonrise time (DateTime or human-readable string)")
    moonset: Optional[TimeField] = Field(None, description="Moonset time (DateTime or human-readable string)")
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
    
    # NEW: Enhanced traditional features
    traditional_years: TraditionalCalendarYears = Field(..., description="Traditional Hindu calendar years")
    tarabala: TarabalaData = Field(..., description="Tarabala and Chandrabala calculations")
    shool_data: ShoolData = Field(..., description="Shool direction and Nivas information")
    panchaka: PanchakaData = Field(..., description="Panchaka classification")
    
    # NEW: Advanced systems
    nakshatra_detailed: Optional[Dict[str, Any]] = Field(None, description="Detailed nakshatra pada system with transitions")
    ritu_ayana: Optional[Dict[str, Any]] = Field(None, description="Seasonal and solar movement data")
    
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

# =============================================================================
# PHASE 4: PERSONALIZED ASTROLOGY MODELS
# =============================================================================

class BirthData(BaseModel):
    """Birth data for personalized calculations"""
    birth_date: Date = Field(..., description="Date of birth", examples=["1990-05-15"])
    birth_time: str = Field(..., description="Time of birth in HH:MM:SS format", examples=["14:30:00"])
    birth_latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude", examples=[28.6139])
    birth_longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude", examples=[77.2090])
    birth_timezone: Optional[str] = Field("UTC", description="Birth timezone (e.g., 'Asia/Kolkata')", examples=["Asia/Kolkata"])
    birth_location_name: Optional[str] = Field(None, description="Birth location name", examples=["New Delhi, India"])

# Natal Chart Models
class PlanetaryInfo(BaseModel):
    """Detailed planetary information"""
    sign: str = Field(..., description="Zodiac sign")
    degree: float = Field(..., description="Degree within sign")
    house: int = Field(..., description="House number (1-12)")
    nakshatra: str = Field(..., description="Nakshatra")
    dignity: str = Field(..., description="Planetary dignity (exalted, own, neutral, debilitated)")
    retrograde: bool = Field(False, description="Is planet retrograde")

class YogaInfo(BaseModel):
    """Yoga information"""
    name: str = Field(..., description="Yoga name")
    strength: str = Field(..., description="Yoga strength (strong, moderate, weak)")
    description: str = Field(..., description="Yoga description")
    effects: List[str] = Field(..., description="Expected effects")

class NatalChartRequest(BaseModel):
    """Request for natal chart generation"""
    birth_data: BirthData = Field(..., description="Birth information")
    ayanamsha: AyanamshaSystem = Field(AyanamshaSystem.LAHIRI, description="Ayanamsha system")
    include_insights: bool = Field(True, description="Include personality insights", examples=[True])
    include_yogas: bool = Field(True, description="Include yoga calculations", examples=[True])

class NatalChartResponse(BaseModel):
    """Natal chart calculation response"""
    birth_details: BirthData = Field(..., description="Birth information used")
    chart_data: Dict[str, Any] = Field(..., description="Complete chart data")
    planetary_positions: Dict[str, PlanetaryInfo] = Field(..., description="All planetary positions")
    house_cusps: List[float] = Field(..., description="House cusp degrees")
    ascendant: PlanetaryInfo = Field(..., description="Ascendant information")
    
    # Optional insights
    key_insights: Optional[Dict[str, Any]] = Field(None, description="Personality and life insights")
    planetary_yogas: Optional[List[YogaInfo]] = Field(None, description="Detected yogas")
    planetary_strengths: Optional[Dict[str, Any]] = Field(None, description="Planetary strength analysis")
    
    # Metadata
    calculation_time_ms: int = Field(..., description="Calculation time in milliseconds")
    ayanamsha_used: str = Field(..., description="Ayanamsha system used")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

# Personalized Panchang Models
class PersonalizedPeriod(BaseModel):
    """Personalized favorable/unfavorable period"""
    start_time: str = Field(..., description="Start time (HH:MM)")
    end_time: str = Field(..., description="End time (HH:MM)")
    activity_type: str = Field(..., description="Recommended activity type")
    strength: str = Field(..., description="Strength level (high, medium, low)")
    reason: str = Field(..., description="Astrological reason")
    transit_influence: Optional[str] = Field(None, description="Current transit influence")

class PersonalizedInsights(BaseModel):
    """Personalized astrological insights"""
    favorable_periods: List[PersonalizedPeriod] = Field(..., description="Favorable time periods")
    unfavorable_periods: List[PersonalizedPeriod] = Field(..., description="Periods to avoid")
    daily_guidance: str = Field(..., description="Personalized daily guidance")
    recommended_activities: List[str] = Field(..., description="Recommended activities")
    avoid_activities: List[str] = Field(..., description="Activities to avoid")
    energy_level: str = Field(..., description="Overall energy level (high, medium, low)")
    emotional_state: str = Field(..., description="Expected emotional state")

class TransitHighlight(BaseModel):
    """Current transit highlight"""
    transit_type: str = Field(..., description="Type of transit")
    transiting_planet: str = Field(..., description="Planet making the transit")
    natal_planet: str = Field(..., description="Natal planet being affected")
    aspect_type: str = Field(..., description="Type of aspect")
    impact: str = Field(..., description="Expected impact (beneficial, challenging, neutral)")
    duration: str = Field(..., description="Duration of influence")

class PersonalizedPanchangRequest(BaseModel):
    """Request for personalized panchang"""
    birth_data: BirthData = Field(..., description="Birth information")
    target_date: Date = Field(..., description="Date for personalized panchang", examples=["2025-07-09"])
    target_time: Optional[str] = Field("12:00:00", description="Time for calculation", examples=["12:00:00"])
    location_latitude: float = Field(..., ge=-90, le=90, description="Current location latitude", examples=[28.6139])
    location_longitude: float = Field(..., ge=-180, le=180, description="Current location longitude", examples=[77.2090])
    ayanamsha: AyanamshaSystem = Field(AyanamshaSystem.LAHIRI, description="Ayanamsha system")
    include_transit_analysis: bool = Field(True, description="Include transit analysis")
    recommendation_depth: str = Field("standard", description="Depth level (basic, standard, detailed)", examples=["standard"])

class PersonalizedPanchangResponse(BaseModel):
    """Personalized panchang response"""
    basic_panchang: PanchangResponse = Field(..., description="Standard panchang data")
    personalized_insights: PersonalizedInsights = Field(..., description="Personalized insights")
    transit_highlights: List[TransitHighlight] = Field(..., description="Current transit influences")
    birth_chart_summary: Dict[str, Any] = Field(..., description="Relevant birth chart info")
    calculation_time_ms: int = Field(..., description="Total calculation time")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

# Transit Analysis Models
class TransitAspect(BaseModel):
    """Individual transit aspect"""
    transiting_planet: str = Field(..., description="Planet making the transit")
    aspect_type: str = Field(..., description="Type of aspect (conjunction, trine, square, etc.)")
    natal_planet: str = Field(..., description="Natal planet being aspected")
    exactness: str = Field(..., description="How exact the aspect is")
    peak_date: Optional[Date] = Field(None, description="Date when aspect is most exact")
    duration_days: int = Field(..., description="Duration of influence in days")
    impact_rating: str = Field(..., description="Impact rating (highly beneficial, beneficial, neutral, challenging, difficult)")
    life_areas: List[str] = Field(..., description="Life areas affected")
    recommendations: List[str] = Field(..., description="Specific recommendations")

class DailyTransitRequest(BaseModel):
    """Request for daily transit analysis"""
    birth_data: BirthData = Field(..., description="Birth information")
    analysis_date: Date = Field(..., description="Date for transit analysis", examples=["2025-07-09"])
    ayanamsha: AyanamshaSystem = Field(AyanamshaSystem.LAHIRI, description="Ayanamsha system")
    include_predictions: bool = Field(True, description="Include predictive insights", examples=[True])
    transit_types: List[str] = Field(["all"], description="Types to include (beneficial, challenging, neutral, all)", examples=[["all"]])

class DailyTransitResponse(BaseModel):
    """Daily transit analysis response"""
    analysis_date: Date = Field(..., description="Date of analysis")
    birth_chart_reference: Dict[str, Any] = Field(..., description="Relevant natal chart data")
    active_transits: List[TransitAspect] = Field(..., description="Active transit aspects")
    daily_summary: str = Field(..., description="Overall daily transit summary")
    key_influences: List[str] = Field(..., description="Key astrological influences")
    timing_recommendations: Dict[str, Any] = Field(..., description="Best timing for activities")
    calculation_time_ms: int = Field(..., description="Calculation time")
    request_timestamp: DateTime = Field(..., description="Request timestamp")

# Personalized Muhurta Models
class PersonalizedMuhurtaRequest(BaseModel):
    """Request for personalized muhurta timing"""
    birth_data: BirthData = Field(..., description="Birth information")
    activity_type: MuhurtaType = Field(..., description="Type of activity", examples=["marriage"])
    start_date: DateTime = Field(..., description="Search start date", examples=["2025-07-09T00:00:00Z"])
    end_date: DateTime = Field(..., description="Search end date", examples=["2025-07-12T23:59:59Z"])
    location_latitude: float = Field(..., ge=-90, le=90, description="Activity location latitude", examples=[28.6139])
    location_longitude: float = Field(..., ge=-180, le=180, description="Activity location longitude", examples=[77.2090])
    duration_minutes: int = Field(60, ge=15, le=1440, description="Required duration", examples=[120])
    ayanamsha: AyanamshaSystem = Field(AyanamshaSystem.LAHIRI, description="Ayanamsha system")
    custom_preferences: Optional[Dict[str, Any]] = Field(None, description="Custom preferences", examples=[{}])
    min_quality: str = Field("good", description="Minimum quality level", examples=["good"])
    max_results: int = Field(10, ge=1, le=50, description="Maximum results", examples=[10])

class PersonalizedMuhurtaResult(BaseModel):
    """Personalized muhurta result"""
    datetime: DateTime = Field(..., description="Recommended date and time")
    quality: str = Field(..., description="Quality level")
    personal_score: float = Field(..., description="Personalized score (0-100)")
    standard_score: float = Field(..., description="Standard muhurta score")
    description: str = Field(..., description="Description")
    personal_factors: Dict[str, Any] = Field(..., description="Personal astrological factors")
    transit_support: List[str] = Field(..., description="Supporting transits")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    warnings: List[str] = Field(..., description="Personalized warnings")

class PersonalizedMuhurtaResponse(BaseModel):
    """Personalized muhurta response"""
    request_summary: Dict[str, Any] = Field(..., description="Request summary")
    birth_chart_factors: Dict[str, Any] = Field(..., description="Relevant birth chart factors")
    results: List[PersonalizedMuhurtaResult] = Field(..., description="Personalized muhurta results")
    total_found: int = Field(..., description="Total results found")
    personalization_notes: List[str] = Field(..., description="Notes about personalization")
    calculation_time_ms: int = Field(..., description="Calculation time")
    request_timestamp: DateTime = Field(..., description="Request timestamp") 