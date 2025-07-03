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

async def get_muhurta_engine():
    """Dependency to get Muhurta engine with proper kaal_engine initialization"""
    try:
        # Get the kaal_engine from the main app
        from ...api.app import kaal_engine
        if not kaal_engine:
            raise HTTPException(
                status_code=503, 
                detail="Kaal engine not available for muhurta calculations"
            )
        return MuhurtaEngine(kaal_engine)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Muhurta engine initialization failed: {str(e)}"
        )

async def get_cache():
    """Dependency to get cache"""
    from ...api.app import cache
    return cache

@router.post("/muhurta", response_model=MuhurtaResponse)
async def find_muhurta(
    request: MuhurtaRequest,
    muhurta_engine: MuhurtaEngine = Depends(get_muhurta_engine),
    cache = Depends(get_cache),
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
        
        # Create muhurta request for engine
        from ...core.muhurta import MuhurtaRequest as EngineMuhurtaRequest
        
        try:
            engine_request = EngineMuhurtaRequest(
                muhurta_type=MuhurtaType[request.muhurta_type.value.upper()],
                start_date=request.start_date,
                end_date=request.end_date,
                latitude=request.latitude,
                longitude=request.longitude,
                duration_minutes=request.duration_minutes
            )
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid muhurta type: {request.muhurta_type.value}"
            )
        
        # Find muhurtas
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
            "typical_duration": "2-4 hours",
            "key_factors": ["tithi", "nakshatra", "vara", "guru_chandal_check"]
        },
        "business": {
            "name": "Business",
            "description": "New venture launches, shop openings, important meetings",
            "typical_duration": "1-2 hours",
            "key_factors": ["mercury_strength", "jupiter_position", "lunar_strength"]
        },
        "travel": {
            "name": "Travel", 
            "description": "Journey commencement, pilgrimage start",
            "typical_duration": "30-60 minutes",
            "key_factors": ["direction_consideration", "vara", "nakshatra"]
        },
        "education": {
            "name": "Education",
            "description": "Study initiation, exam scheduling, learning commencement", 
            "typical_duration": "1-2 hours",
            "key_factors": ["mercury_strength", "jupiter_aspects", "saraswati_yoga"]
        },
        "property": {
            "name": "Property",
            "description": "Real estate transactions, house warming, construction start",
            "typical_duration": "1-3 hours", 
            "key_factors": ["mars_position", "venus_aspects", "fourth_house_strength"]
        },
        "general": {
            "name": "General",
            "description": "Multi-purpose auspicious timings for any activity",
            "typical_duration": "1-2 hours",
            "key_factors": ["basic_panchang", "inauspicious_period_avoidance"]
        }
    } 