"""
Ayanamsha Calculation Endpoints
Traditional astronomical reference system calculations
"""

import time
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AyanamshaComparisonResponse
from ...db.database import get_db
from ...db.models import AyanamshaComparison
from ...core.ayanamsha import AyanamshaEngine

router = APIRouter()

@router.get("/ayanamsha", response_model=AyanamshaComparisonResponse)
async def compare_ayanamsha(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    ayanamsha_engine: AyanamshaEngine = Depends(lambda: None),  # Will be injected in main app
    cache = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare all supported ayanamsha systems for a given date
    
    **Ayanamsha Systems Supported:**
    - **Lahiri**: Official Indian government standard (most widely used)
    - **Raman**: B.V. Raman's system, popular in South India
    - **Krishnamurti**: K.S. Krishnamurti's system for KP astrology
    - **Yukteshwar**: Sri Yukteshwar's calculation from 'Holy Science'
    - **Suryasiddhanta**: Classical text-based calculation
    - **Fagan-Bradley**: Western sidereal astrology standard
    - **DeLuce**: Robert DeLuce's system
    - **Pushya Paksha**: Traditional calculation method
    - **Galactic Center**: Modern astronomical alignment
    - **True Citra**: Star-based traditional calculation
    
    **Returns:**
    - All ayanamsha values in degrees for the date
    - Differences from Lahiri system (reference)
    - System descriptions and historical context
    - Julian day calculation for astronomical reference
    
    **Perfect for:**
    - Astrological software requiring multiple systems
    - Academic research and comparison studies
    - Understanding calculation differences between traditions
    """
    try:
        start_time = time.time()
        
        # Parse date
        if date is None:
            calc_date = date.today()
        else:
            calc_date = datetime.strptime(date, "%Y-%m-%d").date()
        
        # Create cache key
        if cache:
            cache_key = cache.make_key('ayanamsha', calc_date)
            
            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Calculate Julian day
        from skyfield.api import load
        ts = load.timescale()
        t = ts.utc(calc_date.year, calc_date.month, calc_date.day)
        julian_day = t.tt
        
        # Calculate all ayanamsha values
        if not ayanamsha_engine:
            raise HTTPException(status_code=503, detail="Ayanamsha engine not available")
        
        ayanamsha_values = ayanamsha_engine.compare_all_systems(julian_day)
        
        # Calculate differences from Lahiri (reference system)
        lahiri_value = ayanamsha_values.get('LAHIRI', 0)
        differences_from_lahiri = {}
        for system, value in ayanamsha_values.items():
            if system != 'LAHIRI':
                differences_from_lahiri[system] = round(value - lahiri_value, 6)
        
        # System descriptions
        systems_info = {
            'LAHIRI': 'Official Indian government standard (Chitrapaksha), most widely used',
            'RAMAN': 'B.V. Raman system, popular in South Indian astrology',
            'KRISHNAMURTI': 'K.S. Krishnamurti system for KP (Krishnamurti Paddhati) astrology',
            'YUKTESHWAR': 'Sri Yukteshwar calculation from "The Holy Science"',
            'SURYASIDDHANTA': 'Classical Sanskrit astronomical text calculation',
            'FAGAN_BRADLEY': 'Western sidereal astrology standard by Fagan & Bradley',
            'DELUCE': 'Robert DeLuce system used in Western sidereal astrology',
            'PUSHYA_PAKSHA': 'Traditional calculation based on Pushya nakshatra',
            'GALACTIC_CENTER': 'Modern system aligned with galactic center',
            'TRUE_CITRA': 'Star-based calculation using Spica (Chitra) star position'
        }
        
        # Create response
        response = AyanamshaComparisonResponse(
            date=calc_date,
            julian_day=julian_day,
            ayanamsha_values=ayanamsha_values,
            differences_from_lahiri=differences_from_lahiri,
            systems_info=systems_info,
            request_timestamp=datetime.utcnow()
        )
        
        # Cache result
        if cache:
            cache.set(cache_key, response, data_type='ayanamsha')
        
        # Store in database (async, don't wait)
        try:
            db_record = AyanamshaComparison(
                comparison_date=calc_date,
                julian_day=julian_day,
                lahiri=ayanamsha_values.get('LAHIRI'),
                raman=ayanamsha_values.get('RAMAN'),
                krishnamurti=ayanamsha_values.get('KRISHNAMURTI'),
                yukteshwar=ayanamsha_values.get('YUKTESHWAR'),
                suryasiddhanta=ayanamsha_values.get('SURYASIDDHANTA'),
                fagan_bradley=ayanamsha_values.get('FAGAN_BRADLEY'),
                deluce=ayanamsha_values.get('DELUCE'),
                pushya_paksha=ayanamsha_values.get('PUSHYA_PAKSHA'),
                galactic_center=ayanamsha_values.get('GALACTIC_CENTER'),
                true_citra=ayanamsha_values.get('TRUE_CITRA'),
                comparison_data=ayanamsha_values
            )
            db.add(db_record)
            await db.commit()
        except Exception as e:
            print(f"Database storage warning: {e}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ayanamsha calculation failed: {str(e)}"
        )

@router.get("/ayanamsha/systems", response_model=dict)
async def get_ayanamsha_systems():
    """
    Get information about all supported ayanamsha systems
    """
    return {
        "LAHIRI": {
            "name": "Lahiri (Chitrapaksha)",
            "description": "Official Indian government standard, most widely used",
            "year_established": "1955",
            "authority": "Government of India",
            "usage": "Official calendars, most astrology software"
        },
        "RAMAN": {
            "name": "B.V. Raman",
            "description": "Popular system in South Indian astrology",
            "year_established": "1920s",
            "authority": "B.V. Raman",
            "usage": "South Indian astrologers, classical texts"
        },
        "KRISHNAMURTI": {
            "name": "Krishnamurti Paddhati (KP)",
            "description": "System for KP astrology method",
            "year_established": "1960s", 
            "authority": "K.S. Krishnamurti",
            "usage": "KP astrology practitioners"
        },
        "YUKTESHWAR": {
            "name": "Sri Yukteshwar",
            "description": "Calculation from 'The Holy Science'",
            "year_established": "1894",
            "authority": "Sri Yukteshwar Giri",
            "usage": "Kriya Yoga tradition, spiritual astrology"
        },
        "SURYASIDDHANTA": {
            "name": "Surya Siddhanta",
            "description": "Ancient Sanskrit astronomical text",
            "year_established": "~400 CE",
            "authority": "Classical Sanskrit texts",
            "usage": "Traditional calculations, historical research"
        },
        "FAGAN_BRADLEY": {
            "name": "Fagan-Bradley",
            "description": "Western sidereal astrology standard",
            "year_established": "1950s",
            "authority": "Cyril Fagan & Donald Bradley",
            "usage": "Western sidereal astrologers"
        },
        "DELUCE": {
            "name": "Robert DeLuce",
            "description": "Alternative Western sidereal system",
            "year_established": "1960s",
            "authority": "Robert DeLuce", 
            "usage": "Some Western sidereal schools"
        },
        "PUSHYA_PAKSHA": {
            "name": "Pushya Paksha",
            "description": "Traditional nakshatra-based calculation",
            "year_established": "Ancient",
            "authority": "Traditional texts",
            "usage": "Orthodox traditional astrology"
        },
        "GALACTIC_CENTER": {
            "name": "Galactic Center",
            "description": "Modern astronomical alignment",
            "year_established": "Modern",
            "authority": "Astronomical observation",
            "usage": "Modern astronomical astrology"
        },
        "TRUE_CITRA": {
            "name": "True Chitra (Spica)",
            "description": "Star-based traditional calculation",
            "year_established": "Ancient",
            "authority": "Stellar observation",
            "usage": "Star-based traditional systems"
        }
    } 