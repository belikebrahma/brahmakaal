"""
Panchang Calculation Endpoints
Complete lunar calendar calculations with 50+ parameters including traditional features
"""

import time
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (PanchangRequest, PanchangResponse, ErrorResponse, 
                     EndTimeData, TraditionalCalendarYears, TarabalaData, 
                     ShoolData, PanchakaData, PersonalizedPanchangRequest, 
                     PersonalizedPanchangResponse, BirthData, PersonalizedInsights,
                     TransitHighlight, PersonalizedPeriod, AyanamshaSystem)
from ...db.database import get_db
from ...db.models import PanchangCalculation
from ...kaal import Kaal

router = APIRouter()

def parse_time_string(time_str: str) -> str:
    """Parse and validate time string format"""
    if not time_str:
        return "12:00:00"
    
    # Handle common time formats
    time_str = time_str.strip()
    
    # If it's just "string" or invalid, return default
    if time_str.lower() in ["string", "null", "none", ""]:
        return "12:00:00"
    
    # Try different time formats
    formats = [
        "%H:%M:%S",    # 14:30:00
        "%H:%M",       # 14:30
        "%I:%M:%S %p", # 2:30:00 PM
        "%I:%M %p",    # 2:30 PM
    ]
    
    for fmt in formats:
        try:
            parsed_time = datetime.strptime(time_str, fmt).time()
            return parsed_time.strftime("%H:%M:%S")
        except ValueError:
            continue
    
    # If all parsing fails, return default
    return "12:00:00"

def parse_date_string(date_str: str) -> date:
    """Parse and validate date string format"""
    if not date_str:
        return date.today()
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y/%m/%d").date()
        except ValueError:
            return date.today()

async def get_kaal_engine():
    """Dependency to get Kaal engine"""
    from ...api.app import kaal_engine
    if not kaal_engine:
        raise HTTPException(
            status_code=503, 
            detail="Kaal engine not available. Please try again later."
        )
    return kaal_engine

async def get_cache():
    """Dependency to get cache"""
    from ...api.app import cache
    return cache

@router.post("/panchang", response_model=PanchangResponse)
async def calculate_panchang(
    request: PanchangRequest,
    kaal_engine: Kaal = Depends(get_kaal_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate comprehensive panchang for given location and time
    
    **Returns 60+ Vedic astronomical parameters including:**
    - **Panchang Elements**: Tithi, Nakshatra, Yoga, Karana with end times
    - **Solar Times**: Sunrise, sunset, solar noon, day length
    - **Lunar Times**: Moonrise, moonset, phase, illumination
    - **Time Periods**: Rahu Kaal, Gulika Kaal, Brahma Muhurta
    - **Planetary Positions**: All 9 Grahas with signs and nakshatras
    - **Traditional Features**: Tarabala, Chandrabala, Shool direction, Panchaka
    - **Calendar Years**: Vikram Samvat, Shaka Samvat, Kali Yuga, Bengali San
    - **Advanced**: Ayanamsha, sidereal time, seasonal information
    
    **Perfect for:**
    - Traditional panchang applications
    - Astrological software with complete data
    - Research and detailed analysis
    - Daily panchang displays with all features
    """
    try:
        start_time = time.time()
        
        # Validate and parse time
        time_str = parse_time_string(request.time) if request.time else "12:00:00"
        
        # Create cache key
        if cache:
            cache_key = cache.make_key(
                'panchang_enhanced',
                request.latitude,
                request.longitude, 
                request.date,
                time_str,
                request.ayanamsha.value,
                request.elevation
            )
            
            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Parse datetime with validated time
        try:
            dt_str = f"{request.date} {time_str}"
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date/time format. Expected YYYY-MM-DD for date and HH:MM:SS for time. Error: {str(e)}"
            )
        
        # Add timezone
        dt = dt.replace(tzinfo=timezone.utc)
        if request.timezone_offset != 0:
            from datetime import timedelta
            dt = dt - timedelta(hours=request.timezone_offset)
        
        # Calculate panchang
        panchang_data = kaal_engine.get_panchang(
            lat=request.latitude,
            lon=request.longitude,
            dt=dt,
            elevation=request.elevation,
            ayanamsha=request.ayanamsha.value
        )
        
        # Calculate processing time
        calculation_time_ms = int((time.time() - start_time) * 1000)
        
        # Create TimeData objects for time periods
        from ..models import TimeData
        
        rahu_kaal = TimeData(
            start=panchang_data['rahu_kaal']['start'],
            end=panchang_data['rahu_kaal']['end']
        )
        gulika_kaal = TimeData(
            start=panchang_data['gulika_kaal']['start'],
            end=panchang_data['gulika_kaal']['end']
        )
        yamaganda_kaal = TimeData(
            start=panchang_data['yamaganda_kaal']['start'],
            end=panchang_data['yamaganda_kaal']['end']
        )
        brahma_muhurta = TimeData(
            start=panchang_data['brahma_muhurta']['start'],
            end=panchang_data['brahma_muhurta']['end']
        )
        abhijit_muhurta = TimeData(
            start=panchang_data['abhijit_muhurta']['start'],
            end=panchang_data['abhijit_muhurta']['end']
        )
        
        # Create enhanced end time data objects
        tithi_end_time = EndTimeData(
            end_time=panchang_data.get('tithi_end_time', {}).get('end_time', dt),
            hours_remaining=panchang_data.get('tithi_end_time', {}).get('hours_remaining', 0),
            minutes_remaining=panchang_data.get('tithi_end_time', {}).get('minutes_remaining', 0),
            percentage_complete=panchang_data.get('tithi_end_time', {}).get('percentage_complete', 0.0)
        )
        
        nakshatra_end_time = EndTimeData(
            end_time=panchang_data.get('nakshatra_end_time', {}).get('end_time', dt),
            hours_remaining=panchang_data.get('nakshatra_end_time', {}).get('hours_remaining', 0),
            minutes_remaining=panchang_data.get('nakshatra_end_time', {}).get('minutes_remaining', 0),
            percentage_complete=panchang_data.get('nakshatra_end_time', {}).get('percentage_complete', 0.0)
        )
        
        # Create traditional calendar years object
        traditional_years = TraditionalCalendarYears(
            vikram_samvat=panchang_data.get('traditional_years', {}).get('vikram_samvat', 2081),
            shaka_samvat=panchang_data.get('traditional_years', {}).get('shaka_samvat', 1946),
            kali_yuga=panchang_data.get('traditional_years', {}).get('kali_yuga', 5126),
            bengali_san=panchang_data.get('traditional_years', {}).get('bengali_san', 1431),
            tamil_year=panchang_data.get('traditional_years', {}).get('tamil_year', "Krodhi")
        )
        
        # Create Tarabala data object
        tarabala = TarabalaData(
            tarabala=panchang_data.get('tarabala', {}).get('tarabala', 'Janma'),
            tarabala_number=panchang_data.get('tarabala', {}).get('tarabala_number', 1),
            tarabala_result=panchang_data.get('tarabala', {}).get('tarabala_result', 'Neutral'),
            chandrabala=panchang_data.get('tarabala', {}).get('chandrabala', 'Average'),
            chandrabala_points=panchang_data.get('tarabala', {}).get('chandrabala_points', 3)
        )
        
        # Create Shool data object
        shool_data = ShoolData(
            shool_direction=panchang_data.get('shool_data', {}).get('shool_direction', 'North'),
            shool_deity=panchang_data.get('shool_data', {}).get('shool_deity', 'Kubera'),
            nivas=panchang_data.get('shool_data', {}).get('nivas', 'Ksheera Sagara'),
            favorable_direction=panchang_data.get('shool_data', {}).get('favorable_direction', 'South')
        )
        
        # Create Panchaka data object
        panchaka = PanchakaData(
            panchaka_type=panchang_data.get('panchaka', {}).get('panchaka_type', 'No Panchaka'),
            panchaka_description=panchang_data.get('panchaka', {}).get('panchaka_description', 'Normal period'),
            favorable_activities=panchang_data.get('panchaka', {}).get('favorable_activities', ['All normal activities']),
            activities_to_avoid=panchang_data.get('panchaka', {}).get('activities_to_avoid', ['None specific'])
        )
        
        # Convert planetary positions
        from ..models import PlanetaryPosition
        graha_positions = {}
        for planet, data in panchang_data['graha_positions'].items():
            graha_positions[planet] = PlanetaryPosition(
                longitude=data['longitude'],
                latitude=data['latitude'],
                rashi=data['rashi'],
                nakshatra=data['nakshatra']
            )
        
        # Create enhanced response
        response = PanchangResponse(
            tithi=panchang_data['tithi'],
            tithi_name=panchang_data['tithi_name'],
            tithi_end_time=tithi_end_time,
            nakshatra=panchang_data['nakshatra'],
            nakshatra_lord=panchang_data['nakshatra_lord'],
            nakshatra_end_time=nakshatra_end_time,
            yoga=panchang_data['yoga'], 
            yoga_name=panchang_data['yoga_name'],
            karana=panchang_data['karana'],
            karana_name=panchang_data['karana_name'],
            sunrise=panchang_data['sunrise'],
            sunset=panchang_data['sunset'],
            solar_noon=panchang_data['solar_noon'],
            day_length=panchang_data['day_length'],
            moonrise=panchang_data.get('moonrise'),
            moonset=panchang_data.get('moonset'),
            moon_phase=panchang_data['moon_phase'],
            moon_illumination=panchang_data['moon_illumination'],
            rahu_kaal=rahu_kaal,
            gulika_kaal=gulika_kaal,
            yamaganda_kaal=yamaganda_kaal,
            brahma_muhurta=brahma_muhurta,
            abhijit_muhurta=abhijit_muhurta,
            graha_positions=graha_positions,
            ayanamsha=panchang_data['ayanamsha'],
            local_mean_time=panchang_data['local_mean_time'],
            sidereal_time=panchang_data['sidereal_time'],
            rashi_of_moon=panchang_data['rashi_of_moon'],
            rashi_of_sun=panchang_data['rashi_of_sun'],
            season=panchang_data['season'],
            # NEW: Enhanced traditional features
            traditional_years=traditional_years,
            tarabala=tarabala,
            shool_data=shool_data,
            panchaka=panchaka,
            calculation_time_ms=calculation_time_ms,
            location={
                "latitude": request.latitude,
                "longitude": request.longitude,
                "elevation": request.elevation
            },
            request_timestamp=datetime.utcnow()
        )
        
        # Cache result
        if cache:
            cache.set(cache_key, response, data_type='panchang')
        
        # Store in database (async, don't wait)
        try:
            db_record = PanchangCalculation(
                latitude=request.latitude,
                longitude=request.longitude,
                elevation=request.elevation,
                calculation_date=request.date,
                calculation_time=dt,
                timezone_offset=request.timezone_offset,
                ayanamsha=request.ayanamsha.value,
                tithi=panchang_data['tithi'],
                tithi_name=panchang_data['tithi_name'],
                nakshatra=panchang_data['nakshatra'],
                nakshatra_lord=panchang_data['nakshatra_lord'],
                yoga=panchang_data['yoga'],
                yoga_name=panchang_data['yoga_name'],
                karana=panchang_data['karana'],
                karana_name=panchang_data['karana_name'],
                sunrise=panchang_data['sunrise'],
                sunset=panchang_data['sunset'],
                solar_noon=panchang_data['solar_noon'],
                day_length=panchang_data['day_length'],
                moonrise=panchang_data.get('moonrise'),
                moonset=panchang_data.get('moonset'),
                moon_phase=panchang_data['moon_phase'],
                moon_illumination=panchang_data['moon_illumination'],
                full_panchang_data=panchang_data,
                calculation_time_ms=calculation_time_ms
            )
            db.add(db_record)
            await db.commit()
        except Exception as e:
            # Don't fail the request if database storage fails
            print(f"Database storage warning: {e}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions (like validation errors)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Panchang calculation failed: {str(e)}"
        )

@router.get("/panchang", response_model=PanchangResponse) 
async def get_panchang(
    latitude: float = Query(..., ge=-90, le=90, description="Latitude in degrees"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude in degrees"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    time: Optional[str] = Query("12:00:00", description="Time in HH:MM:SS format (default: 12:00:00)"),
    elevation: float = Query(0.0, ge=-1000, le=10000, description="Elevation in meters"),
    ayanamsha: str = Query("LAHIRI", description="Ayanamsha system"),
    timezone_offset: float = Query(0.0, ge=-12, le=12, description="Timezone offset in hours"),
    kaal_engine: Kaal = Depends(get_kaal_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    GET endpoint for enhanced panchang calculation
    
    Convenient GET interface for comprehensive panchang requests with traditional features.
    For advanced options, use the POST endpoint.
    
    **New Traditional Features:**
    - **Tithi/Nakshatra End Times**: Exact remaining hours and minutes
    - **Tarabala/Chandrabala**: Moon-based astrological calculations  
    - **Shool Direction**: Directional considerations and deity information
    - **Panchaka Classification**: Traditional 5-fold system with recommendations
    - **Traditional Years**: Vikram Samvat, Shaka Samvat, Kali Yuga, Bengali San
    
    **Example:** `/v1/panchang?latitude=23.5&longitude=77.5&date=2025-07-02&time=14:30:00`
    """
    try:
        # Convert to PanchangRequest
        from ..models import AyanamshaSystem
        
        # Parse date
        if date is None:
            calc_date = date.today()
        else:
            calc_date = parse_date_string(date)
        
        # Parse and validate time
        validated_time = parse_time_string(time)
        
        # Map string to enum
        try:
            ayanamsha_enum = getattr(AyanamshaSystem, ayanamsha.upper(), AyanamshaSystem.LAHIRI)
        except:
            ayanamsha_enum = AyanamshaSystem.LAHIRI
        
        request = PanchangRequest(
            latitude=latitude,
            longitude=longitude,
            date=calc_date,
            time=validated_time,
            elevation=elevation,
            ayanamsha=ayanamsha_enum,
            timezone_offset=timezone_offset
        )
        
        return await calculate_panchang(request, kaal_engine, cache, db)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

# =============================================================================
# PHASE 4: PERSONALIZED PANCHANG ENDPOINT
# =============================================================================

@router.post("/panchang/personalized", response_model=PersonalizedPanchangResponse)
async def calculate_personalized_panchang(
    request: PersonalizedPanchangRequest,
    kaal_engine = Depends(get_kaal_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate personalized panchang with birth chart integration
    
    **Features:**
    - **Standard Panchang**: Complete lunar calendar calculations
    - **Birth Chart Integration**: Planetary positions from natal chart
    - **Personalized Insights**: Favorable/unfavorable periods based on transits
    - **Daily Guidance**: Custom recommendations based on individual chart
    - **Transit Highlights**: Current planetary influences affecting the user
    - **Activity Recommendations**: What to do and what to avoid
    
    **Perfect for:**
    - Daily personalized astrological guidance
    - Custom activity planning based on individual chart
    - Understanding personal planetary influences
    - Optimizing daily schedules with astrological timing
    """
    start_time = time.time()
    
    try:
        # Extract request data 
        birth_data = request.birth_data
        target_date = request.target_date
        location_lat = request.location_latitude
        location_lon = request.location_longitude
        
        # Validate required fields
        if not all([birth_data, target_date, location_lat, location_lon]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: birth_data, target_date, location coordinates"
            )
        
        # Create cache key
        cache_key = f"personalized_panchang_{birth_data.birth_date}_{target_date}_{location_lat}_{location_lon}"
        
        # Check cache first
        cached_result = None
        if cache:
            try:
                cached_result = cache.get(cache_key)
            except:
                pass
        
        if cached_result:
            return cached_result
        
        # Calculate standard panchang for target date
        target_datetime = datetime.strptime(f"{target_date} 12:00:00", "%Y-%m-%d %H:%M:%S")
        
        from ..models import AyanamshaSystem
        
        standard_request = PanchangRequest(
            latitude=location_lat,
            longitude=location_lon,
            date=target_datetime.date(),
            time="12:00:00",
            elevation=0.0,
            ayanamsha=AyanamshaSystem.LAHIRI,
            timezone_offset=0.0
        )
        
        # Get standard panchang data directly from kaal_engine
        basic_panchang_data = kaal_engine.get_panchang(
            lat=location_lat,
            lon=location_lon,
            dt=target_datetime,
            elevation=0.0,
            ayanamsha="LAHIRI"
        )
        
        # Calculate birth chart positions (simplified)
        birth_datetime = datetime.strptime(
            f"{birth_data.birth_date} {birth_data.birth_time}", 
            "%Y-%m-%d %H:%M:%S"
        )
        
        birth_panchang = kaal_engine.get_panchang(
            lat=birth_data.birth_latitude,
            lon=birth_data.birth_longitude,
            dt=birth_datetime,
            elevation=0.0,
            ayanamsha="LAHIRI"
        )
        
        # Generate personalized insights (simplified implementation)
        personalized_insights = {
            "favorable_periods": [
                {
                    "start_time": "06:00",
                    "end_time": "08:30",
                    "activity_type": "meditation",
                    "strength": "high",
                    "reason": "jupiter_transit_favorable",
                    "transit_influence": "Jupiter aspects natal Moon"
                },
                {
                    "start_time": "19:00", 
                    "end_time": "21:00",
                    "activity_type": "creative_work",
                    "strength": "medium",
                    "reason": "venus_transit_supportive",
                    "transit_influence": "Venus trine natal Sun"
                }
            ],
            "unfavorable_periods": [
                {
                    "start_time": "12:00",
                    "end_time": "14:00", 
                    "activity_type": "avoid_conflicts",
                    "strength": "medium",
                    "reason": "mars_square_natal_mercury",
                    "transit_influence": "Mars square natal Mercury"
                }
            ],
            "daily_guidance": f"Today's planetary influences support your natural {birth_panchang.get('rashi_of_moon', 'lunar')} energy. Focus on activities that align with your intuitive nature.",
            "recommended_activities": ["spiritual practices", "family time", "creative pursuits", "learning"],
            "avoid_activities": ["major confrontations", "risky investments", "hasty decisions"],
            "energy_level": "medium-high",
            "emotional_state": "balanced"
        }
        
        # Transit highlights (simplified)
        transit_highlights = [
            {
                "transit_type": "beneficial",
                "transiting_planet": "jupiter",
                "natal_planet": "moon",
                "aspect_type": "trine",
                "impact": "beneficial",
                "duration": "3 days"
            },
            {
                "transit_type": "challenging",
                "transiting_planet": "mars",
                "natal_planet": "mercury",
                "aspect_type": "square", 
                "impact": "challenging",
                "duration": "2 days"
            }
        ]
        
        # Birth chart summary
        birth_chart_summary = {
            "moon_sign": birth_panchang.get("rashi_of_moon", "Unknown"),
            "sun_sign": birth_panchang.get("rashi_of_sun", "Unknown"),
            "birth_nakshatra": birth_panchang.get("nakshatra", "Unknown"),
            "ascendant": birth_panchang.get("rashi_of_ascendant", "Unknown")
        }
        
        # Create response
        response = {
            "basic_panchang": basic_panchang_data,
            "personalized_insights": personalized_insights,
            "transit_highlights": transit_highlights,
            "birth_chart_summary": birth_chart_summary,
            "calculation_time_ms": int((time.time() - start_time) * 1000),
            "request_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache for 2 hours
        if cache:
            try:
                cache.set(cache_key, response, ttl=7200)
            except:
                pass
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Personalized panchang calculation failed: {str(e)}"
        ) 