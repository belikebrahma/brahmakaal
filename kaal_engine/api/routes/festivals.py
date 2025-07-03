"""
Festival Calendar Endpoints
Hindu festival calendar with regional variations
"""

import time
from datetime import datetime, date
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import FestivalRequest, FestivalResponse, FestivalData, Region, FestivalCategory
from ...db.database import get_db
from ...db.models import FestivalCalendar
from ...core.festivals import FestivalEngine

router = APIRouter()

async def get_festival_engine():
    """Dependency to get Festival engine with proper kaal_engine initialization"""
    try:
        # Get the kaal_engine from the main app
        from ...api.app import kaal_engine
        if not kaal_engine:
            raise HTTPException(
                status_code=503, 
                detail="Kaal engine not available for festival calculations"
            )
        return FestivalEngine(kaal_engine)
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Festival engine initialization failed: {str(e)}"
        )

async def get_cache():
    """Dependency to get cache"""
    from ...api.app import cache
    return cache

@router.post("/festivals", response_model=FestivalResponse)
async def get_festivals(
    request: FestivalRequest,
    festival_engine: FestivalEngine = Depends(get_festival_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Hindu festivals for specified year with regional and category filtering
    
    **Festival Categories:**
    - **Major**: Primary festivals celebrated across India (Diwali, Holi, etc.)
    - **Religious**: Deity-specific observances (Janmashtami, Maha Shivaratri)
    - **Seasonal**: Harvest and seasonal celebrations (Makar Sankranti, Pongal)
    - **Regional**: Location-specific festivals (Durga Puja, Onam, Karva Chauth)
    - **Spiritual**: Observance days (Ekadashi, Pradosh, Purnima)
    - **Cultural**: Traditional celebrations (Gudi Padwa, Baisakhi)
    - **Astronomical**: Eclipse days, solstices, equinoxes
    
    **Regional Coverage (16 regions):**
    - All India, North/South/East/West India
    - State-specific: Maharashtra, Gujarat, Bengal, Tamil Nadu, Kerala, Karnataka, etc.
    
    **Export Formats:**
    - **JSON**: Structured data for applications
    - **iCal**: Calendar import for Google Calendar, Apple Calendar, Outlook
    - **CSV**: Spreadsheet-compatible format
    """
    try:
        start_time = time.time()
        
        # Validate year
        if request.year < 1900 or request.year > 2100:
            raise HTTPException(status_code=400, detail="Year must be between 1900 and 2100")
        
        # Create cache key
        if cache:
            regions_str = ",".join([r.value for r in request.regions])
            categories_str = ",".join([c.value for c in request.categories])
            cache_key = cache.make_key(
                'festivals',
                request.year,
                request.month or 'all',
                regions_str,
                categories_str,
                request.export_format
            )
            
            # Try cache first
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # Convert API regions to engine regions
        from ...core.festivals import Region as EngineRegion
        engine_regions = []
        for region in request.regions:
            try:
                engine_regions.append(EngineRegion[region.value.upper()])
            except KeyError:
                engine_regions.append(EngineRegion.ALL_INDIA)
        
        # Convert API categories to engine categories  
        from ...core.festivals import FestivalCategory as EngineCategory
        engine_categories = []
        for category in request.categories:
            try:
                engine_categories.append(EngineCategory[category.value.upper()])
            except KeyError:
                engine_categories.append(EngineCategory.MAJOR)
        
        # Get festivals from engine
        festivals = festival_engine.calculate_festival_dates(
            year=request.year,
            regions=engine_regions,
            categories=engine_categories
        )
        
        # Filter by month if specified
        if request.month:
            festivals = [f for f in festivals if f.date.month == request.month]
        
        # Convert to API models
        api_festivals = []
        for festival in festivals:
            api_festival = FestivalData(
                name=festival.festival_rule.name,
                english_name=festival.festival_rule.english_name,
                date=festival.date,
                category=festival.festival_rule.category.value,
                regions=[r.value for r in festival.festival_rule.regions],
                description=festival.festival_rule.description,
                alternative_names=festival.festival_rule.alternative_names,
                duration_days=festival.festival_rule.duration_days,
                observance_time=festival.festival_rule.observance_time
            )
            api_festivals.append(api_festival)
        
        # Sort by date
        api_festivals.sort(key=lambda x: x.date)
        
        # Handle export formats
        export_url = None
        if request.export_format == "ical":
            # Generate iCal data
            ical_data = festival_engine.export_to_ical(festivals)
            # In production, this would be stored and a URL returned
            export_url = f"/v1/festivals/export/{request.year}.ics"
        elif request.export_format == "csv":
            # Generate CSV data  
            csv_data = festival_engine.export_to_json(festivals)  # Using JSON export for now
            export_url = f"/v1/festivals/export/{request.year}.csv"
        
        # Calculate processing time
        calculation_time_ms = int((time.time() - start_time) * 1000)
        
        # Create response
        response = FestivalResponse(
            request_summary={
                "year": request.year,
                "month": request.month or "all",
                "regions": [r.value for r in request.regions],
                "categories": [c.value for c in request.categories],
                "export_format": request.export_format
            },
            festivals=api_festivals,
            total_festivals=len(api_festivals),
            export_url=export_url,
            request_timestamp=datetime.utcnow()
        )
        
        # Cache result
        if cache:
            cache.set(cache_key, response, ttl=86400)  # Cache for 24 hours
        
        # Store in database (async, don't wait)
        try:
            for festival in api_festivals[:10]:  # Store first 10 to avoid overwhelming DB
                db_record = FestivalCalendar(
                    festival_name=festival.name,
                    english_name=festival.english_name,
                    festival_date=festival.date,
                    year=request.year,
                    category=festival.category,
                    regions=festival.regions,
                    description=festival.description,
                    alternative_names=festival.alternative_names,
                    duration_days=festival.duration_days,
                    observance_time=festival.observance_time
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
            detail=f"Festival calculation failed: {str(e)}"
        )

@router.get("/festivals", response_model=FestivalResponse)
async def get_festivals_simple(
    year: int = Query(..., ge=1900, le=2100, description="Year for festival calendar"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Specific month (optional)"),
    regions: str = Query("all_india", description="Comma-separated regions"),
    categories: str = Query("major", description="Comma-separated categories"),
    export_format: str = Query("json", description="Export format: json, ical, csv"),
    festival_engine: FestivalEngine = Depends(get_festival_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """
    GET endpoint for festival calendar
    
    Convenient GET interface for simple festival requests.
    For advanced options, use the POST endpoint.
    
    **Example:** `/v1/festivals?year=2025&month=7&regions=all_india&categories=major`
    """
    try:
        # Parse regions
        region_list = []
        for region_str in regions.split(","):
            region_str = region_str.strip().upper()
            try:
                region_list.append(Region[region_str])
            except KeyError:
                region_list.append(Region.ALL_INDIA)
        
        # Parse categories
        category_list = []
        for category_str in categories.split(","):
            category_str = category_str.strip().upper()
            try:
                category_list.append(FestivalCategory[category_str])
            except KeyError:
                category_list.append(FestivalCategory.MAJOR)
        
        # Create request object
        request = FestivalRequest(
            year=year,
            month=month,
            regions=region_list,
            categories=category_list,
            export_format=export_format
        )
        
        return await get_festivals(request, festival_engine, cache, db)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request parameters: {str(e)}"
        )

@router.get("/festivals/regions", response_model=dict)
async def get_regions():
    """
    Get available regions with descriptions
    """
    return {
        "regions": {
            "ALL_INDIA": "Pan-Indian festivals celebrated across the country",
            "NORTH_INDIA": "North Indian regional festivals",
            "SOUTH_INDIA": "South Indian regional festivals", 
            "WEST_INDIA": "Western Indian regional festivals",
            "EAST_INDIA": "Eastern Indian regional festivals",
            "MAHARASHTRA": "Maharashtra state festivals",
            "GUJARAT": "Gujarat state festivals",
            "BENGAL": "Bengal regional festivals",
            "TAMIL_NADU": "Tamil Nadu state festivals",
            "KERALA": "Kerala state festivals",
            "KARNATAKA": "Karnataka state festivals",
            "ANDHRA_PRADESH": "Andhra Pradesh state festivals",
            "RAJASTHAN": "Rajasthan state festivals",
            "PUNJAB": "Punjab state festivals",
            "ODISHA": "Odisha state festivals",
            "ASSAM": "Assam state festivals"
        },
        "default": "ALL_INDIA",
        "most_popular": ["ALL_INDIA", "NORTH_INDIA", "SOUTH_INDIA", "MAHARASHTRA", "GUJARAT"]
    }

@router.get("/festivals/categories", response_model=dict)
async def get_categories():
    """
    Get available festival categories with descriptions
    """
    return {
        "categories": {
            "MAJOR": "Major festivals celebrated across India (Diwali, Holi, etc.)",
            "RELIGIOUS": "Deity-specific religious observances",
            "SEASONAL": "Harvest and seasonal celebrations",
            "REGIONAL": "Location-specific cultural festivals",
            "SPIRITUAL": "Spiritual observances (Ekadashi, Pradosh, etc.)",
            "CULTURAL": "Traditional cultural celebrations",
            "ASTRONOMICAL": "Astronomical events and eclipse days"
        },
        "default": "MAJOR",
        "most_popular": ["MAJOR", "RELIGIOUS", "SPIRITUAL", "SEASONAL"]
    } 