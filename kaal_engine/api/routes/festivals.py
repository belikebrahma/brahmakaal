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

@router.post("/festivals", response_model=FestivalResponse)
async def get_festivals(
    request: FestivalRequest,
    festival_engine: FestivalEngine = Depends(lambda: None),  # Will be injected in main app
    cache = Depends(lambda: None),
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
        
        # Validate year
        if request.year < 1900 or request.year > 2100:
            raise HTTPException(status_code=400, detail="Year must be between 1900 and 2100")
        
        # Convert API regions to engine regions
        from ...core.festivals import Region as EngineRegion
        engine_regions = []
        for region in request.regions:
            engine_regions.append(EngineRegion[region.value.upper()])
        
        # Convert API categories to engine categories  
        from ...core.festivals import FestivalCategory as EngineCategory
        engine_categories = []
        for category in request.categories:
            engine_categories.append(EngineCategory[category.value.upper()])
        
        # Get festivals from engine
        if not festival_engine:
            raise HTTPException(status_code=503, detail="Festival engine not available")
            
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
                name=festival.name,
                english_name=festival.english_name,
                date=festival.date,
                category=festival.category.value,
                regions=[r.value for r in festival.regions],
                description=festival.description,
                alternative_names=festival.alternative_names,
                duration_days=festival.duration_days,
                observance_time=festival.observance_time
            )
            api_festivals.append(api_festival)
        
        # Sort by date
        api_festivals.sort(key=lambda x: x.date)
        
        # Handle export formats
        export_url = None
        if request.export_format == "ical":
            # Generate iCal data
            ical_data = festival_engine.export_ical(festivals, request.year)
            # In production, this would be stored and a URL returned
            export_url = f"/v1/festivals/export/{request.year}.ics"
        elif request.export_format == "csv":
            # Generate CSV data  
            csv_data = festival_engine.export_csv(festivals)
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
    festival_engine: FestivalEngine = Depends(lambda: None),
    cache = Depends(lambda: None),
    db: AsyncSession = Depends(get_db)
):
    """
    GET endpoint for festival calendar
    
    Convenient GET interface for simple festival requests.
    For advanced options, use the POST endpoint.
    """
    # Parse regions
    region_list = [Region.ALL_INDIA]
    if regions != "all_india":
        try:
            region_names = regions.split(",")
            region_list = [Region[name.strip().upper()] for name in region_names]
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid region: {e}")
    
    # Parse categories
    category_list = [FestivalCategory.MAJOR]
    if categories != "major":
        try:
            category_names = categories.split(",")
            category_list = [FestivalCategory[name.strip().upper()] for name in category_names]
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid category: {e}")
    
    # Create request
    request = FestivalRequest(
        year=year,
        month=month,
        regions=region_list,
        categories=category_list,
        export_format=export_format
    )
    
    return await get_festivals(request, festival_engine, cache, db)

@router.get("/festivals/regions", response_model=dict)
async def get_regions():
    """
    Get available regions with descriptions
    """
    return {
        "all_india": "Pan-Indian festivals celebrated nationwide",
        "north_india": "Northern Indian regional festivals",
        "south_india": "Southern Indian regional festivals", 
        "west_india": "Western Indian regional festivals",
        "east_india": "Eastern Indian regional festivals",
        "maharashtra": "Maharashtra state festivals",
        "gujarat": "Gujarat state festivals",
        "bengal": "Bengal region festivals (West Bengal & Bangladesh)",
        "tamil_nadu": "Tamil Nadu state festivals",
        "kerala": "Kerala state festivals",
        "karnataka": "Karnataka state festivals",
        "andhra_pradesh": "Andhra Pradesh & Telangana festivals",
        "rajasthan": "Rajasthan state festivals",
        "punjab": "Punjab region festivals",
        "odisha": "Odisha state festivals",
        "assam": "Assam & Northeast festivals"
    }

@router.get("/festivals/categories", response_model=dict)
async def get_categories():
    """
    Get available festival categories with descriptions
    """
    return {
        "major": "Primary festivals celebrated across India",
        "religious": "Deity-specific religious observances",
        "seasonal": "Harvest and seasonal celebrations",
        "regional": "Location-specific cultural festivals",
        "spiritual": "Spiritual observance days and fasting",
        "cultural": "Traditional cultural celebrations",
        "astronomical": "Eclipse days, solstices, astronomical events"
    } 