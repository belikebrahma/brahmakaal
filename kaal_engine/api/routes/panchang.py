"""
Panchang Calculation Endpoints
Complete lunar calendar calculations with 50+ parameters
"""

import time
from datetime import datetime, date, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import PanchangRequest, PanchangResponse, ErrorResponse
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
    
    **Returns 50+ Vedic astronomical parameters including:**
    - **Panchang Elements**: Tithi, Nakshatra, Yoga, Karana
    - **Solar Times**: Sunrise, sunset, solar noon, day length
    - **Lunar Times**: Moonrise, moonset, phase, illumination
    - **Time Periods**: Rahu Kaal, Gulika Kaal, Brahma Muhurta
    - **Planetary Positions**: All 9 Grahas with signs and nakshatras
    - **Advanced**: Ayanamsha, sidereal time, seasonal information
    
    **Perfect for:**
    - Calendar applications
    - Daily panchang displays  
    - Astrological software
    - Research and analysis
    """
    try:
        start_time = time.time()
        
        # Validate and parse time
        time_str = parse_time_string(request.time) if request.time else "12:00:00"
        
        # Create cache key
        if cache:
            cache_key = cache.make_key(
                'panchang',
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
        
        # Create response
        response = PanchangResponse(
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
    GET endpoint for panchang calculation
    
    Convenient GET interface for simple panchang requests.
    For advanced options, use the POST endpoint.
    
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