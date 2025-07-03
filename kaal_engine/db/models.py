"""
SQLAlchemy Database Models for Brahmakaal API
PostgreSQL schemas for all astronomical data
"""

from datetime import datetime, date
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, JSON, Boolean, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship

# Import Base from database module to ensure consistency
from .database import Base

class PanchangCalculation(Base):
    """Store panchang calculation results"""
    __tablename__ = "panchang_calculations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float, default=0.0)
    
    # Time data
    calculation_date = Column(Date, nullable=False)
    calculation_time = Column(DateTime, nullable=False)
    timezone_offset = Column(Float, default=0.0)
    
    # Ayanamsha system
    ayanamsha = Column(String(50), default="LAHIRI")
    
    # Panchang elements
    tithi = Column(Float)
    tithi_name = Column(String(100))
    nakshatra = Column(String(50))
    nakshatra_lord = Column(String(20))
    yoga = Column(Float)
    yoga_name = Column(String(50))
    karana = Column(Float)
    karana_name = Column(String(50))
    
    # Solar calculations
    sunrise = Column(DateTime)
    sunset = Column(DateTime)
    solar_noon = Column(DateTime)
    day_length = Column(Float)
    
    # Lunar calculations
    moonrise = Column(DateTime)
    moonset = Column(DateTime)
    moon_phase = Column(String(50))
    moon_illumination = Column(Float)
    
    # Complete data (JSON)
    full_panchang_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    calculation_time_ms = Column(Integer)  # Performance tracking
    
    __table_args__ = (
        Index('idx_panchang_location_date', 'latitude', 'longitude', 'calculation_date'),
        Index('idx_panchang_date', 'calculation_date'),
    )

class MuhurtaCalculation(Base):
    """Store muhurta calculation results"""
    __tablename__ = "muhurta_calculations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request data
    muhurta_type = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    duration_minutes = Column(Integer, default=60)
    
    # Result data
    recommended_datetime = Column(DateTime)
    quality = Column(String(20))  # EXCELLENT, VERY_GOOD, GOOD, AVERAGE
    score = Column(Float)
    description = Column(Text)
    
    # Analysis factors
    factors = Column(JSON)
    recommendations = Column(JSON)
    warnings = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    results_count = Column(Integer)
    
    __table_args__ = (
        Index('idx_muhurta_type_location', 'muhurta_type', 'latitude', 'longitude'),
        Index('idx_muhurta_date_range', 'start_date', 'end_date'),
    )

class FestivalCalendar(Base):
    """Store festival calendar data"""
    __tablename__ = "festival_calendars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Festival data
    festival_name = Column(String(100), nullable=False)
    english_name = Column(String(100))
    festival_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    
    # Classification
    festival_type = Column(String(20))  # LUNAR, SOLAR, NAKSHATRA, etc.
    category = Column(String(20))       # MAJOR, RELIGIOUS, SEASONAL, etc.
    regions = Column(JSON)              # List of applicable regions
    
    # Details
    description = Column(Text)
    alternative_names = Column(JSON)
    duration_days = Column(Integer, default=1)
    observance_time = Column(String(20), default="full_day")
    
    # Astronomical data
    lunar_month = Column(String(20))
    paksha = Column(String(10))
    tithi = Column(Integer)
    nakshatra = Column(String(30))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_festival_date_year', 'festival_date', 'year'),
        Index('idx_festival_name_year', 'festival_name', 'year'),
        Index('idx_festival_category', 'category'),
    )

class AyanamshaComparison(Base):
    """Store ayanamsha comparison data"""
    __tablename__ = "ayanamsha_comparisons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Date for comparison
    comparison_date = Column(Date, nullable=False)
    julian_day = Column(Float, nullable=False)
    
    # All ayanamsha values
    lahiri = Column(Float)
    raman = Column(Float)
    krishnamurti = Column(Float)
    yukteshwar = Column(Float)
    suryasiddhanta = Column(Float)
    fagan_bradley = Column(Float)
    deluce = Column(Float)
    pushya_paksha = Column(Float)
    galactic_center = Column(Float)
    true_citra = Column(Float)
    
    # Full comparison data
    comparison_data = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ayanamsha_date', 'comparison_date'),
        Index('idx_ayanamsha_jd', 'julian_day'),
    )

class ApiUsageLog(Base):
    """Track API usage and performance"""
    __tablename__ = "api_usage_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request data
    endpoint = Column(String(100), nullable=False)
    method = Column(String(10), nullable=False)
    client_ip = Column(String(45))
    user_agent = Column(Text)
    
    # Request parameters
    query_params = Column(JSON)
    request_body = Column(JSON)
    
    # Response data
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    response_size_bytes = Column(Integer)
    
    # Performance data
    cache_hit = Column(Boolean, default=False)
    database_queries = Column(Integer, default=0)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_api_usage_endpoint', 'endpoint'),
        Index('idx_api_usage_timestamp', 'timestamp'),
    )

class CacheStatistics(Base):
    """Track cache performance"""
    __tablename__ = "cache_statistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Cache data
    cache_backend = Column(String(20), nullable=False)
    cache_key_pattern = Column(String(100))
    
    # Statistics
    total_requests = Column(Integer, default=0)
    cache_hits = Column(Integer, default=0)
    cache_misses = Column(Integer, default=0)
    hit_rate = Column(Float)
    
    # Performance
    avg_response_time_ms = Column(Float)
    memory_usage_mb = Column(Float)
    
    # Time period
    timestamp = Column(DateTime, default=datetime.utcnow)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    
    __table_args__ = (
        Index('idx_cache_stats_backend', 'cache_backend'),
        Index('idx_cache_stats_timestamp', 'timestamp'),
    ) 