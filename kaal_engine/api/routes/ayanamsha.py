"""
Ayanamsha Calculation Endpoints  
Multiple traditional astronomical reference systems
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

async def get_ayanamsha_engine():
    """Dependency to get Ayanamsha engine"""
    try:
        return AyanamshaEngine()
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail="Ayanamsha engine not available. Please try again later."
        )

async def get_cache():
    """Dependency to get cache"""
    from ...api.app import cache
    return cache

@router.get("/ayanamsha", response_model=AyanamshaComparisonResponse)
async def compare_ayanamsha(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    ayanamsha_engine: AyanamshaEngine = Depends(get_ayanamsha_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare all supported ayanamsha systems for a given date
    
    **Supported Ayanamsha Systems (10 types):**
    - **Lahiri (Chitrapaksha)**: Government of India standard
    - **Raman**: B.V. Raman's system
    - **Krishnamurti (KP)**: K.S. Krishnamurti's system  
    - **Yukteshwar**: Swami Sri Yukteshwar's calculations
    - **Suryasiddhanta**: Classical Surya Siddhanta method
    - **Fagan-Bradley**: Western sidereal standard
    - **De Luce**: Cyril Fagan and Donald Bradley system
    - **Pushya Paksha**: Ancient nakshatra-based system
    - **Galactic Center**: Modern astronomical alignment
    - **True Citra**: Spica star-based calculations
    
    **Applications:**
    - Horoscope calculations and chart rectification
    - Planetary position accuracy verification  
    - Historical astronomical research
    - Comparative astrological analysis
    
    **Example:** `/v1/ayanamsha?date=2025-07-02`
    """
    try:
        start_time = time.time()
        
        # Parse date
        if date is None:
            calc_date = date.today()
        else:
            try:
                calc_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        
        # Validate date range
        if calc_date.year < 1900 or calc_date.year > 2100:
            raise HTTPException(
                status_code=400, 
                detail="Date must be between 1900 and 2100"
            )
        
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
    Get available ayanamsha systems with descriptions
    """
    return {
        "systems": {
            "LAHIRI": "Lahiri (Chitrapaksha) - Government of India standard",
            "RAMAN": "B.V. Raman's system",
            "KRISHNAMURTI": "K.S. Krishnamurti's system",
            "YUKTESHWAR": "Swami Sri Yukteshwar's calculations",
            "SURYASIDDHANTA": "Classical Surya Siddhanta method",
            "FAGAN_BRADLEY": "Western sidereal standard",
            "DELUCE": "Cyril Fagan and Donald Bradley system",
            "PUSHYA_PAKSHA": "Ancient nakshatra-based system",
            "GALACTIC_CENTER": "Modern astronomical alignment",
            "TRUE_CITRA": "Spica star-based calculations"
        },
        "default": "LAHIRI",
        "most_popular": ["LAHIRI", "RAMAN", "KRISHNAMURTI"],
        "applications": {
            "vedic_astrology": ["LAHIRI", "RAMAN", "KRISHNAMURTI"],
            "western_sidereal": ["FAGAN_BRADLEY", "DELUCE"],
            "research": ["YUKTESHWAR", "SURYASIDDHANTA", "TRUE_CITRA"],
            "modern": ["GALACTIC_CENTER"]
        }
    } 