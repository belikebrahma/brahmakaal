"""
Muhurta Calculation Endpoints
Electional astrology for finding auspicious timings
"""

import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (MuhurtaRequest, MuhurtaResponse, ErrorResponse,
                     PersonalizedMuhurtaRequest, PersonalizedMuhurtaResponse,
                     BirthData, PersonalizedMuhurtaResult, AyanamshaSystem)
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

# =============================================================================
# PHASE 4: PERSONALIZED MUHURTA ENDPOINT
# =============================================================================

async def get_kaal_engine():
    """Dependency to get Kaal engine - will be overridden by main app"""
    raise HTTPException(
        status_code=503, 
        detail="Astrological calculation engine not available. Please try again later."
    )

@router.post("/muhurta/personalized", response_model=PersonalizedMuhurtaResponse)
async def find_personalized_muhurta(
    request: PersonalizedMuhurtaRequest,
    muhurta_engine: MuhurtaEngine = Depends(get_muhurta_engine),
    kaal_engine = Depends(get_kaal_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    Find personalized muhurta timing based on individual birth chart
    
    **Features:**
    - **Standard Muhurta**: Traditional auspicious timing calculations
    - **Birth Chart Integration**: Consider individual planetary positions
    - **Personalized Scoring**: Weight factors based on natal chart strengths
    - **Transit Analysis**: Current planetary transits affecting the individual
    - **Custom Recommendations**: Activity-specific guidance based on personal chart
    - **Dual Scoring**: Both standard and personalized quality scores
    
    **Perfect for:**
    - Personal ceremony timing (marriage, business launch)
    - Individualized activity planning
    - Maximizing personal astrological support
    - Custom event scheduling based on birth chart
    """
    start_time = time.time()
    
    try:
        # Extract request data
        birth_data = request.birth_data
        activity_type = request.activity_type.value
        start_date = request.start_date
        end_date = request.end_date
        location_lat = request.location_latitude
        location_lon = request.location_longitude
        duration_minutes = request.duration_minutes
        max_results = request.max_results
        
        # Validate required fields
        if not all([birth_data, start_date, end_date, location_lat, location_lon]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: birth_data, date range, location coordinates"
            )
        
        # Use datetime objects directly (already parsed by Pydantic)
        start_dt = start_date
        end_dt = end_date
        
        # Create cache key
        cache_key = f"personalized_muhurta_{birth_data.birth_date}_{activity_type}_{start_date}_{end_date}_{location_lat}_{location_lon}"
        
        # Check cache
        cached_result = None
        if cache:
            try:
                cached_result = cache.get(cache_key)
            except:
                pass
        
        if cached_result:
            return cached_result
        
        # Get birth chart data
        birth_datetime = datetime.strptime(
            f"{birth_data.birth_date} {birth_data.birth_time}", 
            "%Y-%m-%d %H:%M:%S"
        )
        
        # Will use dependency injection for kaal_engine
        
        birth_panchang = kaal_engine.get_panchang(
            lat=birth_data.birth_latitude,
            lon=birth_data.birth_longitude,
            dt=birth_datetime,
            elevation=0.0,
            ayanamsha="LAHIRI"
        )
        
        # Create standard muhurta request
        standard_request = MuhurtaRequest(
            muhurta_type=activity_type.lower(),  # Use string directly
            latitude=location_lat,
            longitude=location_lon,
            start_date=start_dt,
            end_date=end_dt,
            duration_minutes=duration_minutes,
            min_quality="good",
            max_results=max_results * 2  # Get more results for personalization
        )
        
        # Get standard muhurta results
        standard_response = await find_muhurta(standard_request, muhurta_engine, cache, db)
        standard_results = standard_response.results
        
        # Personalize each result
        personalized_results = []
        
        for result in standard_results:
            # Calculate personalized score adjustments
            personal_score = result.score
            
            # Get current planetary positions for this muhurta time
            muhurta_panchang = kaal_engine.get_panchang(
                lat=location_lat,
                lon=location_lon,
                dt=result.datetime,
                elevation=0.0,
                ayanamsha="LAHIRI"
            )
            
            # Personal factors analysis
            personal_factors = {
                "natal_moon_sign": birth_panchang.get("rashi_of_moon", "Unknown"),
                "natal_sun_sign": birth_panchang.get("rashi_of_sun", "Unknown"), 
                "current_tithi_compatibility": "favorable",  # Simplified
                "nakshatra_harmony": "moderate",  # Simplified
                "planetary_support": []
            }
            
            # Analyze planetary support
            birth_graha = birth_panchang.get("graha_positions", {})
            current_graha = muhurta_panchang.get("graha_positions", {})
            
            # Check for beneficial transits
            transit_support = []
            for planet in ["jupiter", "venus", "mercury"]:
                if planet in birth_graha and planet in current_graha:
                    # Simplified transit analysis
                    birth_pos = birth_graha[planet].get('longitude', 0) if hasattr(birth_graha[planet], 'get') else 0
                    current_pos = current_graha[planet].get('longitude', 0) if hasattr(current_graha[planet], 'get') else 0
                    
                    # If beneficial planet is in good aspect (simplified)
                    if abs(current_pos - birth_pos) % 120 < 10:  # Rough trine check
                        transit_support.append(f"{planet.title()} trine natal position")
                        personal_score += 5
            
            personal_factors["planetary_support"] = transit_support
            
            # Activity-specific personalizations
            if activity_type == "marriage":
                # Check Venus and 7th house considerations
                if "venus" in transit_support:
                    personal_score += 10
                    personal_factors["venus_support"] = "strong"
            elif activity_type == "business":
                # Check Mercury and Jupiter
                if "jupiter" in transit_support:
                    personal_score += 8
                if "mercury" in transit_support:
                    personal_score += 6
                personal_factors["business_support"] = "favorable"
            
            # Generate personalized recommendations
            personalized_recommendations = result.recommendations.copy()
            
            if transit_support:
                personalized_recommendations.insert(0, f"Strong personal planetary support from: {', '.join(transit_support)}")
            
            # Activity-specific personal recommendations
            if activity_type == "marriage" and personal_factors.get("venus_support") == "strong":
                personalized_recommendations.append("Venus strongly supports your marital harmony at this time")
            
            if birth_panchang.get("rashi_of_moon") == muhurta_panchang.get("rashi_of_moon"):
                personalized_recommendations.append("Moon returns to your birth sign - highly favorable for new beginnings")
                personal_score += 8
            
            # Personalized warnings
            personalized_warnings = result.warnings.copy()
            
            # Check for challenging transits
            if "mars" in current_graha:
                # Simplified Mars transit check
                mars_pos = current_graha["mars"].get('longitude', 0) if hasattr(current_graha["mars"], 'get') else 0
                if birth_graha.get("mars"):
                    birth_mars_pos = birth_graha["mars"].get('longitude', 0) if hasattr(birth_graha["mars"], 'get') else 0
                    if abs(mars_pos - birth_mars_pos) % 90 < 10:  # Rough square check
                        personalized_warnings.append("Mars square natal Mars - avoid confrontational decisions")
                        personal_score -= 5
            
            # Ensure score stays within bounds
            personal_score = max(0, min(100, personal_score))
            
            # Create personalized result
            personalized_result = {
                "datetime": result.datetime.isoformat(),
                "quality": result.quality,
                "personal_score": round(personal_score, 1),
                "standard_score": result.score,
                "description": result.description,
                "personal_factors": personal_factors,
                "transit_support": transit_support,
                "recommendations": personalized_recommendations,
                "warnings": personalized_warnings
            }
            
            personalized_results.append(personalized_result)
        
        # Sort by personalized score
        personalized_results.sort(key=lambda x: x["personal_score"], reverse=True)
        
        # Limit to requested number
        personalized_results = personalized_results[:max_results]
        
        # Birth chart factors summary
        birth_chart_factors = {
            "moon_sign": birth_panchang.get("rashi_of_moon", "Unknown"),
            "sun_sign": birth_panchang.get("rashi_of_sun", "Unknown"),
            "birth_nakshatra": birth_panchang.get("nakshatra", "Unknown"),
            "key_strengths": [],  # Will be populated based on dignities
            "considerations": [f"Born under {birth_panchang.get('nakshatra', 'Unknown')} nakshatra"]
        }
        
        # Personalization notes
        personalization_notes = [
            f"Muhurta timing personalized for {birth_chart_factors['moon_sign']} Moon sign",
            f"Considered natal chart from {birth_data.birth_date} {birth_data.birth_time}",
            f"Transit analysis included for {activity_type} activity",
            "Personal planetary support and challenges evaluated"
        ]
        
        # Create response
        response = {
            "request_summary": {
                "activity_type": activity_type,
                "birth_date": birth_data.get("birth_date"),
                "date_range": f"{start_date} to {end_date}",
                "location": f"{location_lat}°N, {location_lon}°E",
                "duration_minutes": duration_minutes
            },
            "birth_chart_factors": birth_chart_factors,
            "results": personalized_results,
            "total_found": len(personalized_results),
            "personalization_notes": personalization_notes,
            "calculation_time_ms": int((time.time() - start_time) * 1000),
            "request_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache for 1 hour
        if cache:
            try:
                cache.set(cache_key, response, ttl=3600)
            except:
                pass
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Personalized muhurta calculation failed: {str(e)}"
        ) 