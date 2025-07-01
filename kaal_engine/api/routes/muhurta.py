"""
Muhurta Calculation Endpoints
Electional astrology for finding auspicious timings
"""

import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import MuhurtaRequest, MuhurtaResponse, ErrorResponse
from ...db.database import get_db
from ...db.models import MuhurtaCalculation
from ...core.muhurta import MuhurtaEngine, MuhurtaType

router = APIRouter()

@router.post("/muhurta", response_model=MuhurtaResponse)
async def find_muhurta(
    request: MuhurtaRequest,
    muhurta_engine: MuhurtaEngine = Depends(lambda: None),  # Will be injected in main app
    cache = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    """
    Find auspicious muhurta timings using traditional Vedic electional astrology
    
    **Muhurta Types Supported:**
    - **Marriage**: Wedding ceremonies with comprehensive traditional rules
    - **Business**: New venture launches, important meetings
    - **Travel**: Journey commencement times
    - **Education**: Study initiation, exam scheduling
    - **Property**: Real estate transactions, construction
    - **General**: Multi-purpose auspicious timings
    
    **Analysis Factors:**
    - Tithi (lunar day) favorability
    - Nakshatra (lunar mansion) strength
    - Vara (weekday) compatibility
    - Yoga combinations
    - Planetary positions
    - Time period quality (avoiding Rahu Kaal, etc.)
    
    **Quality Levels:**
    - **Excellent**: 80-100 score, highest traditional support
    - **Very Good**: 70-79 score, strong recommendations
    - **Good**: 60-69 score, suitable with minor considerations
    - **Average**: 50-59 score, acceptable with precautions
    """
    try:
        start_time = time.time()
        
        # Create cache key
        if cache:
            cache_key = cache.make_key(
                'muhurta',
                request.muhurta_type.value,
                request.latitude,
                request.longitude,
                request.start_date,
                request.end_date,
                request.duration_minutes,
                request.min_quality
            )
            
            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Validate date range
        if request.start_date >= request.end_date:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        
        # Limit search range to prevent excessive computation
        max_days = 365
        if (request.end_date - request.start_date).days > max_days:
            raise HTTPException(
                status_code=400, 
                detail=f"Date range too large. Maximum {max_days} days allowed"
            )
        
        # Create muhurta request for engine
        from ...core.muhurta import MuhurtaRequest as EngineMuhurtaRequest
        
        engine_request = EngineMuhurtaRequest(
            muhurta_type=MuhurtaType[request.muhurta_type.value.upper()],
            start_date=request.start_date,
            end_date=request.end_date,
            latitude=request.latitude,
            longitude=request.longitude,
            duration_minutes=request.duration_minutes
        )
        
        # Find muhurtas
        if not muhurta_engine:
            raise HTTPException(status_code=503, detail="Muhurta engine not available")
            
        results = muhurta_engine.find_muhurta(engine_request)
        
        # Filter by quality
        quality_map = {
            "excellent": ["excellent"],
            "very_good": ["excellent", "very_good"], 
            "good": ["excellent", "very_good", "good"],
            "average": ["excellent", "very_good", "good", "average"]
        }
        
        allowed_qualities = quality_map.get(request.min_quality, ["good", "very_good", "excellent"])
        filtered_results = [r for r in results if r.quality.value in allowed_qualities]
        
        # Limit results
        limited_results = filtered_results[:request.max_results]
        
        # Convert to API models
        from ..models import MuhurtaResult
        api_results = []
        
        for result in limited_results:
            api_result = MuhurtaResult(
                datetime=result.datetime,
                quality=result.quality.value,
                score=result.score,
                description=result.description,
                duration_minutes=result.duration_minutes,
                factors=result.factors,
                recommendations=result.recommendations,
                warnings=result.warnings
            )
            api_results.append(api_result)
        
        # Calculate processing time
        calculation_time_ms = int((time.time() - start_time) * 1000)
        
        # Create response
        response = MuhurtaResponse(
            request_summary={
                "muhurta_type": request.muhurta_type.value,
                "location": f"{request.latitude}°N, {request.longitude}°E",
                "date_range": f"{request.start_date.date()} to {request.end_date.date()}",
                "duration_minutes": request.duration_minutes,
                "min_quality": request.min_quality,
                "total_days_searched": (request.end_date - request.start_date).days
            },
            results=api_results,
            total_found=len(api_results),
            calculation_time_ms=calculation_time_ms,
            request_timestamp=datetime.utcnow()
        )
        
        # Cache result
        if cache:
            cache.set(cache_key, response, data_type='muhurta')
        
        # Store in database (async, don't wait)
        try:
            if api_results:  # Only store if we found results
                best_result = api_results[0]
                db_record = MuhurtaCalculation(
                    muhurta_type=request.muhurta_type.value,
                    start_date=request.start_date,
                    end_date=request.end_date,
                    latitude=request.latitude,
                    longitude=request.longitude,
                    duration_minutes=request.duration_minutes,
                    recommended_datetime=best_result.datetime,
                    quality=best_result.quality,
                    score=best_result.score,
                    description=best_result.description,
                    factors=best_result.factors,
                    recommendations=best_result.recommendations,
                    warnings=best_result.warnings,
                    results_count=len(api_results)
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
            detail=f"Muhurta calculation failed: {str(e)}"
        )

@router.get("/muhurta/types", response_model=dict)
async def get_muhurta_types():
    """
    Get available muhurta types with descriptions
    """
    return {
        "marriage": {
            "name": "Marriage",
            "description": "Wedding ceremonies with comprehensive traditional rules",
            "factors": ["Favorable tithis", "Compatible nakshatras", "Auspicious yogas", "Planetary positions"],
            "duration": "2-4 hours typically"
        },
        "business": {
            "name": "Business",
            "description": "New venture launches, important meetings",
            "factors": ["Growth-oriented tithis", "Prosperity nakshatras", "Jupiter influence"],
            "duration": "1-2 hours typically"
        },
        "travel": {
            "name": "Travel", 
            "description": "Journey commencement times",
            "factors": ["Mobile nakshatras", "Safe travel yogas", "Directional considerations"],
            "duration": "15-60 minutes typically"
        },
        "education": {
            "name": "Education",
            "description": "Study initiation, exam scheduling",
            "factors": ["Knowledge nakshatras", "Mercury strength", "Learning yogas"],
            "duration": "1-3 hours typically"
        },
        "property": {
            "name": "Property",
            "description": "Real estate transactions, construction",
            "factors": ["Fixed nakshatras", "Earth element strength", "Stability yogas"],
            "duration": "1-2 hours typically"
        },
        "general": {
            "name": "General",
            "description": "Multi-purpose auspicious timings",
            "factors": ["Overall favorability", "Balanced influences", "General prosperity"],
            "duration": "1-2 hours typically"
        }
    } 