"""
Transit Analysis Routes
Daily planetary transit analysis against natal charts
"""

import time
from datetime import datetime, date, timezone, timedelta
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    DailyTransitRequest, DailyTransitResponse, TransitAspect, 
    BirthData, AyanamshaSystem, ErrorResponse
)
from ...db.database import get_db
from ...kaal import Kaal

router = APIRouter()

async def get_kaal_engine():
    """Dependency to get Kaal engine - will be overridden by main app"""
    raise HTTPException(
        status_code=503, 
        detail="Astrological calculation engine not available. Please try again later."
    )

def calculate_aspect_type(angle_diff: float) -> str:
    """Calculate the type of aspect based on angular difference"""
    angle_diff = abs(angle_diff) % 360
    if angle_diff > 180:
        angle_diff = 360 - angle_diff
    
    if angle_diff <= 8:
        return "conjunction"
    elif 52 <= angle_diff <= 68:
        return "sextile"
    elif 82 <= angle_diff <= 98:
        return "square"
    elif 112 <= angle_diff <= 128:
        return "trine"
    elif 172 <= angle_diff <= 188:
        return "opposition"
    else:
        return "none"

def assess_aspect_impact(transiting_planet: str, natal_planet: str, aspect_type: str) -> str:
    """Assess the impact of a transit aspect"""
    
    # Beneficial aspects
    beneficial_aspects = ["trine", "sextile"]
    challenging_aspects = ["square", "opposition"]
    neutral_aspects = ["conjunction"]
    
    # Planet combinations impact
    beneficial_planets = ["jupiter", "venus", "moon"]
    challenging_planets = ["saturn", "mars", "rahu", "ketu"]
    neutral_planets = ["sun", "mercury"]
    
    if aspect_type in beneficial_aspects:
        return "beneficial"
    elif aspect_type in challenging_aspects:
        if transiting_planet in challenging_planets:
            return "challenging"
        else:
            return "neutral"
    elif aspect_type == "conjunction":
        if transiting_planet in beneficial_planets:
            return "beneficial"
        elif transiting_planet in challenging_planets:
            return "challenging"
        else:
            return "neutral"
    
    return "neutral"

def get_life_areas_for_planets(natal_planet: str, natal_house: int) -> List[str]:
    """Get life areas affected by planetary transits"""
    
    # Planet-based life areas
    planet_areas = {
        "sun": ["identity", "career", "leadership", "vitality"],
        "moon": ["emotions", "family", "home", "intuition"],
        "mars": ["energy", "action", "conflicts", "passion"],
        "mercury": ["communication", "learning", "travel", "business"],
        "jupiter": ["wisdom", "growth", "spirituality", "fortune"],
        "venus": ["relationships", "love", "art", "beauty", "money"],
        "saturn": ["discipline", "responsibilities", "career", "limitations"],
        "rahu": ["ambitions", "unconventional paths", "foreign connections"],
        "ketu": ["spirituality", "detachment", "past-life karma"]
    }
    
    # House-based life areas
    house_areas = {
        1: ["personality", "appearance", "new beginnings"],
        2: ["money", "values", "speech", "family wealth"],
        3: ["communication", "siblings", "short travel", "courage"],
        4: ["home", "mother", "property", "emotional security"],
        5: ["creativity", "children", "romance", "education"],
        6: ["health", "work", "service", "daily routine"],
        7: ["relationships", "partnerships", "marriage"],
        8: ["transformation", "occult", "shared resources"],
        9: ["philosophy", "higher learning", "spirituality", "luck"],
        10: ["career", "reputation", "authority", "public image"],
        11: ["friends", "hopes", "gains", "social networks"],
        12: ["spirituality", "isolation", "foreign lands", "liberation"]
    }
    
    areas = []
    
    # Add planet-specific areas
    if natal_planet in planet_areas:
        areas.extend(planet_areas[natal_planet])
    
    # Add house-specific areas  
    if natal_house in house_areas:
        areas.extend(house_areas[natal_house])
    
    return list(set(areas))  # Remove duplicates

def generate_recommendations_for_aspect(transiting_planet: str, natal_planet: str, 
                                      aspect_type: str, impact: str) -> List[str]:
    """Generate specific recommendations for a transit aspect"""
    
    recommendations = []
    
    if impact == "beneficial":
        if aspect_type == "trine":
            recommendations.extend([
                f"Excellent time to focus on {natal_planet}-related activities",
                "Trust your intuition and take positive action",
                "This is a favorable period for new initiatives"
            ])
        elif aspect_type == "sextile":
            recommendations.extend([
                "Good opportunities available with some effort",
                f"Communicate and network around {natal_planet} themes",
                "Take moderate risks and explore new possibilities"
            ])
        elif transiting_planet == "jupiter":
            recommendations.extend([
                "Seek growth and expansion opportunities",
                "This is a time for learning and teaching",
                "Be generous and optimistic in your approach"
            ])
    
    elif impact == "challenging":
        if aspect_type == "square":
            recommendations.extend([
                "Face challenges with patience and determination",
                f"Review and restructure {natal_planet}-related areas",
                "Avoid hasty decisions during this period"
            ])
        elif aspect_type == "opposition":
            recommendations.extend([
                "Seek balance and avoid extremes",
                "This period brings important awareness",
                "Consider other perspectives and compromise"
            ])
        elif transiting_planet == "saturn":
            recommendations.extend([
                "Focus on discipline and long-term planning",
                "This is a time for important life lessons",
                "Be patient as progress may be slow but steady"
            ])
    
    else:  # neutral
        recommendations.extend([
            f"Pay attention to {natal_planet}-related themes",
            "This is a time of adjustment and awareness",
            "Stay flexible and adapt to changing circumstances"
        ])
    
    return recommendations

@router.post("/transits/daily", response_model=DailyTransitResponse)
async def analyze_daily_transits(
    request: DailyTransitRequest,
    kaal_engine: Kaal = Depends(get_kaal_engine),
    cache = Depends(lambda: None),  # Will be properly injected in main app
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze daily planetary transits against natal chart
    
    **Features:**
    - **Current vs Natal**: Compare current planetary positions with birth chart
    - **Active Aspects**: Identify all active transit aspects (conjunction, trine, square, etc.)
    - **Impact Assessment**: Beneficial, challenging, or neutral influence evaluation
    - **Life Areas**: Specific life areas affected by each transit
    - **Timing Predictions**: When transits will be most exact and impactful
    - **Personalized Recommendations**: Specific guidance based on individual chart
    
    **Perfect for:**
    - Daily astrological guidance
    - Understanding current planetary influences
    - Planning activities based on transit timing
    - Personal development and awareness
    """
    start_time = time.time()
    
    try:
        birth_data = request.birth_data
        analysis_date = request.analysis_date
        
        # Create cache key
        cache_key = f"transits_{birth_data.birth_date}_{birth_data.birth_time}_{analysis_date}_{request.ayanamsha.value}"
        
        # Check cache
        cached_result = None
        if cache:
            try:
                cached_result = await cache.get(cache_key)
            except:
                pass
        
        if cached_result:
            return cached_result
        
        # Get natal chart positions
        birth_datetime = datetime.combine(birth_data.birth_date, datetime.strptime(birth_data.birth_time, "%H:%M:%S").time())
        natal_panchang = kaal_engine.get_panchang(
            lat=birth_data.birth_latitude,
            lon=birth_data.birth_longitude,
            dt=birth_datetime,
            elevation=0.0,
            ayanamsha=request.ayanamsha.value
        )
        
        # Get current transit positions
        transit_datetime = datetime.combine(analysis_date, datetime.strptime("12:00:00", "%H:%M:%S").time())
        current_panchang = kaal_engine.get_panchang(
            lat=birth_data.birth_latitude,
            lon=birth_data.birth_longitude,
            dt=transit_datetime,
            elevation=0.0,
            ayanamsha=request.ayanamsha.value
        )
        
        # Extract planetary positions
        natal_positions = natal_panchang.get("graha_positions", {})
        current_positions = current_panchang.get("graha_positions", {})
        
        # Calculate house positions for natal chart
        ascendant_degree = natal_panchang.get("ascendant_longitude", 0.0)
        house_cusps = []
        for i in range(12):
            cusp = (ascendant_degree + (i * 30)) % 360
            house_cusps.append(cusp)
        
        # Calculate natal planet houses
        natal_houses = {}
        for planet_name, planet_data in natal_positions.items():
            if hasattr(planet_data, 'longitude'):
                longitude = planet_data.longitude
            elif isinstance(planet_data, dict):
                longitude = planet_data.get('longitude', 0.0)
            else:
                continue
                
            # Find house
            planet_house = 1
            for i in range(12):
                next_cusp = house_cusps[(i + 1) % 12]
                current_cusp = house_cusps[i]
                
                if current_cusp < next_cusp:
                    if current_cusp <= longitude < next_cusp:
                        planet_house = i + 1
                        break
                else:  # Cusp crosses 0°
                    if longitude >= current_cusp or longitude < next_cusp:
                        planet_house = i + 1
                        break
            
            natal_houses[planet_name] = planet_house
        
        # Analyze transits and find aspects
        active_transits = []
        
        for transiting_planet, transit_data in current_positions.items():
            if hasattr(transit_data, 'longitude'):
                transit_longitude = transit_data.longitude
            elif isinstance(transit_data, dict):
                transit_longitude = transit_data.get('longitude', 0.0)
            else:
                continue
            
            for natal_planet, natal_data in natal_positions.items():
                if hasattr(natal_data, 'longitude'):
                    natal_longitude = natal_data.longitude
                elif isinstance(natal_data, dict):
                    natal_longitude = natal_data.get('longitude', 0.0)
                else:
                    continue
                
                # Calculate aspect
                angle_diff = abs(transit_longitude - natal_longitude)
                aspect_type = calculate_aspect_type(angle_diff)
                
                if aspect_type != "none":
                    # Assess impact
                    impact = assess_aspect_impact(transiting_planet, natal_planet, aspect_type)
                    
                    # Get life areas
                    natal_house = natal_houses.get(natal_planet, 1)
                    life_areas = get_life_areas_for_planets(natal_planet, natal_house)
                    
                    # Generate recommendations
                    recommendations = generate_recommendations_for_aspect(
                        transiting_planet, natal_planet, aspect_type, impact
                    )
                    
                    # Calculate exactness
                    orb_tolerance = {
                        "conjunction": 8, "opposition": 8, "trine": 6, 
                        "square": 6, "sextile": 4
                    }
                    
                    max_orb = orb_tolerance.get(aspect_type, 5)
                    actual_orb = min(angle_diff % 360, 360 - (angle_diff % 360))
                    
                    if aspect_type in ["conjunction", "opposition"]:
                        exact_angles = [0, 180]
                    elif aspect_type == "trine":
                        exact_angles = [120, 240]
                    elif aspect_type == "square":
                        exact_angles = [90, 270]
                    elif aspect_type == "sextile":
                        exact_angles = [60, 300]
                    else:
                        exact_angles = [0]
                    
                    closest_exact = min(exact_angles, key=lambda x: abs(angle_diff - x))
                    exactness_orb = abs(angle_diff - closest_exact)
                    
                    if exactness_orb <= 1:
                        exactness = "exact"
                    elif exactness_orb <= 3:
                        exactness = "within_3_degrees"
                    elif exactness_orb <= 5:
                        exactness = "within_5_degrees"
                    else:
                        exactness = "wide_orb"
                    
                    # Estimate duration (simplified)
                    planet_speeds = {
                        "moon": 12, "sun": 1, "mercury": 1.5, "venus": 1.2,
                        "mars": 0.5, "jupiter": 0.08, "saturn": 0.03,
                        "rahu": 0.05, "ketu": 0.05
                    }
                    
                    speed = planet_speeds.get(transiting_planet, 1)
                    duration_days = int(max_orb * 2 / speed)
                    
                    # Create transit aspect
                    transit_aspect = TransitAspect(
                        transiting_planet=transiting_planet,
                        aspect_type=aspect_type,
                        natal_planet=natal_planet,
                        exactness=exactness,
                        peak_date=analysis_date,  # Simplified
                        duration_days=duration_days,
                        impact_rating=impact,
                        life_areas=life_areas,
                        recommendations=recommendations
                    )
                    
                    active_transits.append(transit_aspect)
        
        # Generate daily summary
        beneficial_count = len([t for t in active_transits if t.impact_rating == "beneficial"])
        challenging_count = len([t for t in active_transits if t.impact_rating == "challenging"])
        
        if beneficial_count > challenging_count:
            daily_summary = f"Today brings {beneficial_count} beneficial planetary influences. This is a favorable day for growth and positive action."
        elif challenging_count > beneficial_count:
            daily_summary = f"Today presents {challenging_count} challenging aspects. Use patience and wisdom to navigate obstacles."
        else:
            daily_summary = "Today offers a balanced mix of planetary influences. Stay aware and adapt to changing energies."
        
        # Key influences
        key_influences = []
        for transit in active_transits[:3]:  # Top 3 most significant
            key_influences.append(f"{transit.transiting_planet.title()} {transit.aspect_type} natal {transit.natal_planet.title()}")
        
        # Timing recommendations
        timing_recommendations = {
            "best_time_for_action": "06:00-10:00" if beneficial_count > 0 else "18:00-20:00",
            "avoid_major_decisions": "12:00-15:00" if challenging_count > 0 else "none",
            "meditation_time": "05:00-06:00",
            "social_activities": "evening hours" if "venus" in [t.transiting_planet for t in active_transits] else "afternoon"
        }
        
        # Birth chart reference
        birth_chart_reference = {
            "ascendant": natal_panchang.get("rashi_of_ascendant", "Unknown"),
            "moon_sign": natal_panchang.get("rashi_of_moon", "Unknown"),
            "sun_sign": natal_panchang.get("rashi_of_sun", "Unknown"),
            "birth_date": birth_data.birth_date,
            "ayanamsha": request.ayanamsha.value
        }
        
        # Create response
        response = DailyTransitResponse(
            analysis_date=analysis_date,
            birth_chart_reference=birth_chart_reference,
            active_transits=active_transits,
            daily_summary=daily_summary,
            key_influences=key_influences,
            timing_recommendations=timing_recommendations,
            calculation_time_ms=int((time.time() - start_time) * 1000),
            request_timestamp=datetime.now(timezone.utc)
        )
        
        # Cache for 4 hours (transits change slowly)
        if cache:
            try:
                await cache.set(cache_key, response, ttl=14400)  # 4 hours
            except:
                pass
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing daily transits: {str(e)}"
        ) 