"""
Horoscope/Natal Chart Generation Routes
Complete birth chart calculations with insights and yogas
"""

import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    NatalChartRequest, NatalChartResponse, BirthData, PlanetaryInfo, 
    YogaInfo, AyanamshaSystem, ErrorResponse
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

def calculate_planetary_dignity(planet_name: str, sign: str, degree: float) -> str:
    """Calculate planetary dignity (exalted, own, neutral, debilitated)"""
    
    # Exaltation degrees and signs
    exaltations = {
        "sun": {"sign": "Aries", "degree": 10},
        "moon": {"sign": "Taurus", "degree": 3},
        "mars": {"sign": "Capricorn", "degree": 28},
        "mercury": {"sign": "Virgo", "degree": 15},
        "jupiter": {"sign": "Cancer", "degree": 5},
        "venus": {"sign": "Pisces", "degree": 27},
        "saturn": {"sign": "Libra", "degree": 20},
        "rahu": {"sign": "Gemini", "degree": 15},  # Approximate
        "ketu": {"sign": "Sagittarius", "degree": 15}  # Approximate
    }
    
    # Own signs
    own_signs = {
        "sun": ["Leo"],
        "moon": ["Cancer"],
        "mars": ["Aries", "Scorpio"],
        "mercury": ["Gemini", "Virgo"],
        "jupiter": ["Sagittarius", "Pisces"],
        "venus": ["Taurus", "Libra"],
        "saturn": ["Capricorn", "Aquarius"],
        "rahu": [],  # No own signs
        "ketu": []   # No own signs
    }
    
    # Debilitation signs (opposite of exaltation)
    debilitations = {
        "sun": "Libra",
        "moon": "Scorpio", 
        "mars": "Cancer",
        "mercury": "Pisces",
        "jupiter": "Capricorn",
        "venus": "Virgo",
        "saturn": "Aries",
        "rahu": "Sagittarius",
        "ketu": "Gemini"
    }
    
    planet_lower = planet_name.lower()
    
    # Check exaltation
    if planet_lower in exaltations:
        exalt_info = exaltations[planet_lower]
        if sign == exalt_info["sign"]:
            # Check if within orb of exact exaltation degree
            if abs(degree - exalt_info["degree"]) <= 5:
                return "exalted"
    
    # Check own sign
    if planet_lower in own_signs:
        if sign in own_signs[planet_lower]:
            return "own"
    
    # Check debilitation
    if planet_lower in debilitations:
        if sign == debilitations[planet_lower]:
            return "debilitated"
    
    return "neutral"

def detect_yogas(planetary_positions: Dict[str, PlanetaryInfo]) -> List[YogaInfo]:
    """Detect traditional Vedic yogas in the birth chart"""
    yogas = []
    
    try:
        # Get planetary positions
        sun_house = planetary_positions.get("sun", {}).house if hasattr(planetary_positions.get("sun", {}), 'house') else None
        moon_house = planetary_positions.get("moon", {}).house if hasattr(planetary_positions.get("moon", {}), 'house') else None
        jupiter_house = planetary_positions.get("jupiter", {}).house if hasattr(planetary_positions.get("jupiter", {}), 'house') else None
        venus_house = planetary_positions.get("venus", {}).house if hasattr(planetary_positions.get("venus", {}), 'house') else None
        mars_house = planetary_positions.get("mars", {}).house if hasattr(planetary_positions.get("mars", {}), 'house') else None
        
        # Gaja Kesari Yoga: Moon and Jupiter in kendras (1,4,7,10) from each other
        if moon_house and jupiter_house:
            kendra_houses = [1, 4, 7, 10]
            house_diff = abs(moon_house - jupiter_house)
            if house_diff in [0, 3, 6, 9] or (house_diff == 9 and moon_house in kendra_houses):
                yogas.append(YogaInfo(
                    name="Gaja_Kesari_Yoga",
                    strength="strong" if moon_house in kendra_houses and jupiter_house in kendra_houses else "moderate",
                    description="Moon and Jupiter in favorable positions",
                    effects=["wisdom", "prosperity", "respect", "good fortune"]
                ))
        
        # Raj Yoga: Sun and Moon in good positions
        if sun_house and moon_house:
            if sun_house in [1, 4, 7, 10] and moon_house in [1, 4, 7, 10]:
                yogas.append(YogaInfo(
                    name="Raj_Yoga",
                    strength="strong",
                    description="Sun and Moon both in kendra houses",
                    effects=["leadership", "authority", "royal status", "fame"]
                ))
        
        # Chandra Mangal Yoga: Moon and Mars together or in good aspect
        if moon_house and mars_house:
            if abs(moon_house - mars_house) <= 1 or moon_house == mars_house:
                yogas.append(YogaInfo(
                    name="Chandra_Mangal_Yoga",
                    strength="moderate",
                    description="Moon and Mars in close association",
                    effects=["financial prosperity", "property acquisition", "material success"]
                ))
        
        # Guru Shukra Yoga: Jupiter and Venus in good positions
        if jupiter_house and venus_house:
            if jupiter_house in [1, 4, 7, 10] and venus_house in [1, 4, 7, 10]:
                yogas.append(YogaInfo(
                    name="Guru_Shukra_Yoga",
                    strength="strong",
                    description="Jupiter and Venus both in kendra houses",
                    effects=["wisdom", "artistic talents", "spiritual growth", "harmonious relationships"]
                ))
    
    except Exception as e:
        # If yoga detection fails, just return empty list
        pass
    
    return yogas

def generate_personality_insights(planetary_positions: Dict[str, PlanetaryInfo], ascendant: PlanetaryInfo) -> Dict[str, Any]:
    """Generate personality insights based on planetary positions"""
    
    insights = {
        "personality_traits": [],
        "life_themes": [],
        "strengths": [],
        "challenges": []
    }
    
    try:
        # Ascendant-based traits
        ascendant_sign = ascendant.sign
        ascendant_traits = {
            "Aries": {"traits": ["energetic", "pioneering", "independent"], "themes": ["leadership", "new beginnings"]},
            "Taurus": {"traits": ["stable", "practical", "determined"], "themes": ["security", "material comfort"]},
            "Gemini": {"traits": ["communicative", "adaptable", "curious"], "themes": ["learning", "communication"]},
            "Cancer": {"traits": ["nurturing", "intuitive", "emotional"], "themes": ["family", "emotional security"]},
            "Leo": {"traits": ["confident", "creative", "dramatic"], "themes": ["self-expression", "recognition"]},
            "Virgo": {"traits": ["analytical", "perfectionist", "helpful"], "themes": ["service", "health", "improvement"]},
            "Libra": {"traits": ["harmonious", "diplomatic", "artistic"], "themes": ["relationships", "balance", "beauty"]},
            "Scorpio": {"traits": ["intense", "transformative", "mysterious"], "themes": ["transformation", "depth", "power"]},
            "Sagittarius": {"traits": ["adventurous", "philosophical", "optimistic"], "themes": ["knowledge", "travel", "expansion"]},
            "Capricorn": {"traits": ["ambitious", "disciplined", "practical"], "themes": ["career", "achievement", "structure"]},
            "Aquarius": {"traits": ["innovative", "humanitarian", "independent"], "themes": ["social causes", "technology", "uniqueness"]},
            "Pisces": {"traits": ["compassionate", "imaginative", "spiritual"], "themes": ["spirituality", "creativity", "service"]}
        }
        
        if ascendant_sign in ascendant_traits:
            asc_data = ascendant_traits[ascendant_sign]
            insights["personality_traits"].extend(asc_data["traits"])
            insights["life_themes"].extend(asc_data["themes"])
        
        # Sun sign influence
        sun_info = planetary_positions.get("sun")
        if sun_info:
            if sun_info.house == 1:
                insights["strengths"].append("strong self-identity")
            elif sun_info.house == 10:
                insights["life_themes"].append("career success")
                insights["strengths"].append("natural leadership")
        
        # Moon sign influence  
        moon_info = planetary_positions.get("moon")
        if moon_info:
            if moon_info.house == 4:
                insights["life_themes"].append("family focus")
                insights["strengths"].append("emotional intelligence")
            elif moon_info.dignity == "exalted":
                insights["strengths"].append("emotional stability")
        
        # Add some general challenges
        insights["challenges"] = ["work-life balance", "managing expectations", "decision-making under pressure"]
        
    except Exception:
        # Default insights if calculation fails
        insights = {
            "personality_traits": ["determined", "thoughtful", "adaptable"],
            "life_themes": ["personal growth", "relationships", "career development"],
            "strengths": ["resilience", "intuition", "communication"],
            "challenges": ["balancing priorities", "self-doubt", "overthinking"]
        }
    
    return insights

@router.post("/horoscope/natal-chart", response_model=NatalChartResponse)
async def generate_natal_chart(
    request: NatalChartRequest,
    kaal_engine: Kaal = Depends(get_kaal_engine),
    cache = Depends(lambda: None),  # Will be properly injected in main app
    db: AsyncSession = Depends(get_db)
):
    """
    Generate complete natal chart with planetary positions, houses, and insights
    
    **Features:**
    - **Complete Planetary Positions**: All 9 Grahas with signs, houses, nakshatras
    - **House System**: Equal house calculations with accurate cusps
    - **Planetary Dignities**: Exaltation, own sign, debilitation analysis
    - **Traditional Yogas**: Detection of major Vedic yogas
    - **Personality Insights**: AI-generated character analysis based on chart
    - **Life Themes**: Key areas of focus based on planetary positions
    
    **Perfect for:**
    - Personal astrological analysis
    - Understanding individual birth chart patterns
    - Personalized recommendation systems
    - Astrological research and study
    """
    start_time = time.time()
    
    try:
        birth_data = request.birth_data
        
        # Create a cache key for birth chart (for performance)
        cache_key = f"natal_chart_{birth_data.birth_date}_{birth_data.birth_time}_{birth_data.birth_latitude}_{birth_data.birth_longitude}_{request.ayanamsha.value}"
        
        # Check cache first
        cached_result = None
        if cache:
            try:
                cached_result = await cache.get(cache_key)
            except:
                pass
        
        if cached_result:
            return cached_result
        
        # Calculate basic panchang for birth date and time
        birth_datetime = datetime.combine(birth_data.birth_date, datetime.strptime(birth_data.birth_time, "%H:%M:%S").time())
        
        # Get planetary positions for birth chart
        # Calculate timezone offset from birth_timezone string
        def get_timezone_offset(tz_string):
            """Convert timezone string to offset hours"""
            tz_map = {
                "Asia/Kolkata": 5.5,
                "Asia/Mumbai": 5.5,
                "Asia/Delhi": 5.5,
                "Asia/Calcutta": 5.5,
                "IST": 5.5,
                "UTC": 0.0,
                "GMT": 0.0
            }
            return tz_map.get(tz_string, 5.5)  # Default to IST
        
        timezone_offset = get_timezone_offset(birth_data.birth_timezone)
        
        panchang_data = kaal_engine.get_panchang(
            lat=birth_data.birth_latitude,
            lon=birth_data.birth_longitude,
            dt=birth_datetime,
            elevation=0.0,
            ayanamsha=request.ayanamsha.value,
            timezone_offset=timezone_offset
        )
        
        # Extract planetary positions and convert to PlanetaryInfo format
        planetary_positions = {}
        
        # Calculate houses using equal house system (30° each from ascendant)
        ascendant_degree = panchang_data.get("ascendant_longitude", 0.0)
        house_cusps = []
        for i in range(12):
            cusp = (ascendant_degree + (i * 30)) % 360
            house_cusps.append(cusp)
        
        # Process each planet
        graha_positions = panchang_data.get("graha_positions", {})
        
        for planet_name, planet_data in graha_positions.items():
            if hasattr(planet_data, 'longitude'):
                longitude = planet_data.longitude
            elif isinstance(planet_data, dict):
                longitude = planet_data.get('longitude', 0.0)
            else:
                continue
                
            # Calculate which house this planet is in
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
            
            # Get additional planet data
            rashi = planet_data.rashi if hasattr(planet_data, 'rashi') else planet_data.get('rashi', 'Unknown')
            nakshatra = planet_data.nakshatra if hasattr(planet_data, 'nakshatra') else planet_data.get('nakshatra', 'Unknown')
            
            # Calculate degree within sign
            degree_in_sign = longitude % 30
            
            # Calculate dignity
            dignity = calculate_planetary_dignity(planet_name, rashi, degree_in_sign)
            
            planetary_positions[planet_name] = PlanetaryInfo(
                sign=rashi,
                degree=degree_in_sign,
                house=planet_house,
                nakshatra=nakshatra,
                dignity=dignity,
                retrograde=False  # TODO: Add retrograde calculation
            )
        
        # Create ascendant info
        ascendant_rashi = panchang_data.get("rashi_of_ascendant", "Aries")
        ascendant = PlanetaryInfo(
            sign=ascendant_rashi,
            degree=ascendant_degree % 30,
            house=1,
            nakshatra="",  # Ascendant doesn't have nakshatra
            dignity="neutral",
            retrograde=False
        )
        
        # Generate insights and yogas if requested
        key_insights = None
        planetary_yogas = None
        
        if request.include_insights:
            key_insights = generate_personality_insights(planetary_positions, ascendant)
        
        if request.include_yogas:
            planetary_yogas = detect_yogas(planetary_positions)
        
        # Create complete chart data
        chart_data = {
            "ascendant_longitude": ascendant_degree,
            "house_system": "equal",
            "planetary_data": graha_positions,
            "calculation_method": "tropical_to_sidereal",
            "birth_location": {
                "latitude": birth_data.birth_latitude,
                "longitude": birth_data.birth_longitude,
                "name": birth_data.birth_location_name
            }
        }
        
        # Calculate planetary strengths (simplified)
        planetary_strengths = {}
        for planet_name, planet_info in planetary_positions.items():
            strength_score = 50.0  # Base score
            
            # Adjust based on dignity
            if planet_info.dignity == "exalted":
                strength_score += 30
            elif planet_info.dignity == "own":
                strength_score += 20
            elif planet_info.dignity == "debilitated":
                strength_score -= 30
            
            # Adjust based on house position (kendras are stronger)
            if planet_info.house in [1, 4, 7, 10]:
                strength_score += 15
            elif planet_info.house in [2, 5, 8, 11]:
                strength_score += 10
            
            planetary_strengths[planet_name] = {
                "score": max(0, min(100, strength_score)),
                "dignity": planet_info.dignity,
                "house_strength": "strong" if planet_info.house in [1, 4, 7, 10] else "moderate"
            }
        
        # Create response
        response = NatalChartResponse(
            birth_details=birth_data,
            chart_data=chart_data,
            planetary_positions=planetary_positions,
            house_cusps=house_cusps,
            ascendant=ascendant,
            key_insights=key_insights,
            planetary_yogas=planetary_yogas,
            planetary_strengths=planetary_strengths,
            calculation_time_ms=int((time.time() - start_time) * 1000),
            ayanamsha_used=request.ayanamsha.value,
            request_timestamp=datetime.now(timezone.utc)
        )
        
        # Cache the result for 24 hours (birth charts don't change)
        if cache:
            try:
                await cache.set(cache_key, response, ttl=86400)  # 24 hours
            except:
                pass
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating natal chart: {str(e)}"
        ) 