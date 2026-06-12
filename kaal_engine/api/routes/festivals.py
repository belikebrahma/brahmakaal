"""
Festival Calendar Endpoints
Hindu festival calendar with regional variations, DB-backed serving, and location-specific timings
"""

import asyncio
import time
from datetime import datetime, date
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..models import FestivalRequest, FestivalResponse, FestivalData, Region, FestivalCategory
from ...db.database import get_db
from ...db.models import FestivalCalendar

router = APIRouter()


async def get_festival_engine():
    """Dependency to get Festival engine with proper kaal_engine initialization"""
    try:
        from ...api.app import kaal_engine
        if not kaal_engine:
            raise HTTPException(status_code=503, detail="Kaal engine not available")
        from ...core.festivals import FestivalEngine
        return FestivalEngine(kaal_engine)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Festival engine init failed: {str(e)}")


async def get_kaal_engine():
    """Dependency to get the raw Kaal engine."""
    from ...api.app import kaal_engine
    if not kaal_engine:
        raise HTTPException(status_code=503, detail="Kaal engine not available")
    return kaal_engine


async def get_cache():
    """Dependency to get cache"""
    from ...api.app import cache
    return cache


async def _db_festivals_response(
    db: AsyncSession,
    year: int,
    month: Optional[int],
    request_summary: dict,
) -> Optional[dict]:
    """Try to fetch festivals from DB. Returns a response dict or None."""
    try:
        query = select(FestivalCalendar).where(FestivalCalendar.year == year)
        if month:
            query = query.where(
                and_(
                    FestivalCalendar.festival_date >= date(year, month, 1),
                    FestivalCalendar.festival_date <= date(year, month, 31),
                )
            )
        
        result = await db.execute(query)
        rows = result.scalars().all()
        
        if not rows:
            return None
        
        # If we have < 30% of expected festivals, something is missing — recompute
        # For a full year we expect ~150+ festivals; for a month ~10-20
        expected = 150 if not month else 15
        if len(rows) < expected * 0.3:
            return None
        
        api_festivals = []
        for row in rows:
            api_festivals.append(
                FestivalData(
                    name=row.festival_name,
                    english_name=row.english_name or "",
                    date=row.festival_date,
                    category=row.category or "major",
                    regions=row.regions or ["all_india"],
                    description=row.description or "",
                    alternative_names=row.alternative_names or [],
                    duration_days=row.duration_days or 1,
                    observance_time=row.observance_time or "full_day",
                )
            )
        
        api_festivals.sort(key=lambda x: x.date)
        
        response = FestivalResponse(
            request_summary=request_summary,
            festivals=api_festivals,
            total_festivals=len(api_festivals),
            request_timestamp=datetime.utcnow(),
            from_db=True,
        )
        return response.model_dump()
    except Exception as e:
        print(f"DB festival fetch warning: {e}")
        return None


async def _store_festivals_in_db(
    db: AsyncSession,
    year: int,
    api_festivals: list,
):
    """Bulk store festivals in the database."""
    try:
        from ...db.models import FestivalCalendar as FCModel
        
        stored = 0
        for festival in api_festivals:
            record = FCModel(
                festival_name=festival.name,
                english_name=festival.english_name,
                festival_date=festival.date,
                year=year,
                category=festival.category,
                regions=festival.regions,
                description=festival.description,
                alternative_names=festival.alternative_names,
                duration_days=festival.duration_days,
                observance_time=festival.observance_time,
            )
            db.add(record)
            stored += 1
        
        await db.commit()
        print(f"✅ Stored {stored} festivals for {year} in DB")
    except Exception as e:
        print(f"Database storage warning: {e}")


@router.post("/festivals")
async def get_festivals(
    request: FestivalRequest,
    festival_engine=Depends(get_festival_engine),
    cache=Depends(get_cache),
    db: AsyncSession = Depends(get_db),
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
        
        if request.year < 1900 or request.year > 2100:
            raise HTTPException(status_code=400, detail="Year must be between 1900 and 2100")
        
        request_summary = {
            "year": request.year,
            "month": request.month or "all",
            "regions": [r.value for r in request.regions],
            "categories": [c.value for c in request.categories],
            "export_format": request.export_format,
        }
        
        # === Try DB first (fastest) ===
        db_result = await _db_festivals_response(db, request.year, request.month, request_summary)
        if db_result:
            return db_result
        
        # === Try cache second ===
        if cache:
            regions_str = ",".join([r.value for r in request.regions])
            categories_str = ",".join([c.value for c in request.categories])
            cache_key = cache.make_key(
                'festivals', request.year, request.month or 'all',
                regions_str, categories_str, request.export_format,
            )
            cached_result = await cache.get(cache_key)
            if cached_result and not isinstance(cached_result, str):
                if hasattr(cached_result, 'model_dump'):
                    return cached_result.model_dump()
                return cached_result
        
        # === Compute (fallback) ===
        from ...core.festivals import Region as EngineRegion, FestivalCategory as EngineCategory
        
        engine_regions = [
            EngineRegion[r.value.upper()] if r.value.upper() in EngineRegion.__members__ else EngineRegion.ALL_INDIA
            for r in request.regions
        ]
        engine_categories = [
            EngineCategory[c.value.upper()] if c.value.upper() in EngineCategory.__members__ else EngineCategory.MAJOR
            for c in request.categories
        ]
        
        loop = asyncio.get_event_loop()
        festivals = await loop.run_in_executor(
            None,
            lambda: festival_engine.calculate_festival_dates(
                year=request.year, regions=engine_regions, categories=engine_categories
            ),
        )
        
        if request.month:
            festivals = [f for f in festivals if f.date.month == request.month]
        
        api_festivals = []
        for festival in festivals:
            rule = festival.festival_rule
            api_festivals.append(FestivalData(
                name=rule.name,
                english_name=rule.english_name,
                date=festival.date,
                category=rule.category.value if rule.category else "major",
                regions=[r.value for r in (rule.regions or [EngineRegion.ALL_INDIA])],
                description=rule.description,
                alternative_names=rule.alternative_names or [],
                duration_days=rule.duration_days or 1,
                observance_time=rule.observance_time or "full_day",
            ))
        
        api_festivals.sort(key=lambda x: x.date)
        
        response = FestivalResponse(
            request_summary=request_summary,
            festivals=api_festivals,
            total_festivals=len(api_festivals),
            request_timestamp=datetime.utcnow(),
        )
        
        # Cache
        if cache:
            await cache.set(cache_key, response.model_dump(), ttl=86400)
        
        # Store in DB in background
        asyncio.create_task(_store_festivals_in_db(db, request.year, api_festivals))
        
        return response.model_dump()
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Festival calculation failed: {str(e)}")


@router.get("/festivals")
async def get_festivals_simple(
    year: int = Query(..., ge=1900, le=2100),
    month: Optional[int] = Query(None, ge=1, le=12),
    regions: str = Query("all_india"),
    categories: str = Query("major"),
    export_format: str = Query("json"),
    festival_engine=Depends(get_festival_engine),
    cache=Depends(get_cache),
    db: AsyncSession = Depends(get_db),
):
    """GET endpoint for festival calendar. Convenient interface to /festivals POST."""
    try:
        region_list = []
        for r in regions.split(","):
            r = r.strip().upper()
            try:
                region_list.append(Region[r])
            except KeyError:
                region_list.append(Region.ALL_INDIA)
        
        category_list = []
        for c in categories.split(","):
            c = c.strip().upper()
            try:
                category_list.append(FestivalCategory[c])
            except KeyError:
                category_list.append(FestivalCategory.MAJOR)
        
        request = FestivalRequest(
            year=year, month=month,
            regions=region_list, categories=category_list,
            export_format=export_format,
        )
        return await get_festivals(request, festival_engine, cache, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameters: {str(e)}")


@router.get("/festivals/regions")
async def get_regions():
    """Get available regions with descriptions"""
    return {
        "regions": {
            "ALL_INDIA": "Pan-Indian festivals celebrated across India",
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
            "ASSAM": "Assam state festivals",
        },
        "default": "ALL_INDIA",
        "most_popular": ["ALL_INDIA", "NORTH_INDIA", "SOUTH_INDIA", "MAHARASHTRA", "GUJARAT"],
    }


@router.get("/festivals/categories")
async def get_categories():
    """Get available festival categories with descriptions"""
    return {
        "categories": {
            "MAJOR": "Major festivals (Diwali, Holi, etc.)",
            "RELIGIOUS": "Deity-specific religious observances",
            "SEASONAL": "Harvest and seasonal celebrations",
            "REGIONAL": "Location-specific cultural festivals",
            "SPIRITUAL": "Spiritual observances (Ekadashi, Pradosh)",
            "CULTURAL": "Traditional cultural celebrations",
            "ASTRONOMICAL": "Astronomical events and eclipse days",
        },
        "default": "MAJOR",
        "most_popular": ["MAJOR", "RELIGIOUS", "SPIRITUAL", "SEASONAL"],
    }


# ──────────────────────────────────────────────────────────────────────
# Festival + Location Timings Endpoint
# ──────────────────────────────────────────────────────────────────────

@router.get("/festivals/search")
async def search_festivals(
    q: str = Query(..., min_length=2, description="Search festival name"),
    festival_engine=Depends(get_festival_engine),
):
    """Search for festivals by name. Returns matching festival rules."""
    results = []
    seen = set()
    
    for rule in festival_engine.festival_rules:
        if q.lower() in rule.name.lower() or q.lower() in rule.english_name.lower():
            if rule.name not in seen:
                seen.add(rule.name)
                results.append({
                    "name": rule.name,
                    "english_name": rule.english_name,
                    "category": rule.category.value if rule.category else "major",
                    "type": rule.festival_type.value if rule.festival_type else "lunar",
                    "month": rule.month,
                    "paksha": rule.paksha,
                    "tithi": rule.tithi,
                    "description": rule.description[:200] if rule.description else "",
                    "alternative_names": rule.alternative_names[:5],
                })
    
    return {"query": q, "results": results, "total": len(results)}


@router.get("/festivals/{festival_name}/timings")
async def get_festival_timings(
    festival_name: str,
    year: int = Query(..., ge=1900, le=2100),
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    timezone_offset: float = Query(5.5, ge=-12, le=14),
    elevation: float = Query(0.0, ge=0),
    festival_engine=Depends(get_festival_engine),
    kaal=Depends(get_kaal_engine),
):
    """
    Get precise timings for a festival at a specific location.
    
    Returns the exact date, tithi start/end, sunrise/sunset, muhurta,
    and other timing details for the festival at the given coordinates.
    
    **Example:** GET /v1/festivals/Diwali/timings?year=2026&latitude=28.61&longitude=77.20&timezone_offset=5.5
    """
    try:
        # 1. Find the festival rule by name (exact or partial match)
        rule = None
        for r in festival_engine.festival_rules:
            if r.name.lower() == festival_name.lower():
                rule = r
                break
        
        if not rule:
            # Try alternative names
            for r in festival_engine.festival_rules:
                if any(festival_name.lower() in alt.lower() for alt in (r.alternative_names or [])):
                    rule = r
                    break
        
        if not rule:
            # Try partial match — return suggestions
            matches = [r.name for r in festival_engine.festival_rules if festival_name.lower() in r.name.lower()]
            matches = matches[:10]
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"Festival '{festival_name}' not found",
                    "suggestions": matches,
                    "hint": "Use /v1/festivals/search?q=<name> to find the exact name",
                },
            )
        
        # 2. Compute the festival date using the scanner
        from ...core.festival_scanner import TithiScanner
        
        scanner = TithiScanner(kaal)
        
        if rule.festival_type.value == "LUNAR" and rule.month and rule.tithi:
            # Lunar festival — scan for the tithi
            paksha_num = rule.tithi if rule.paksha == "shukla" else rule.tithi + 15
            result = scanner.scan_festival(
                year=year,
                month_name=rule.month,
                tithi_number=paksha_num,
                evening_start=rule.evening_start,
            )
            festival_date = result["date"]
            method = "lunar_scan"
            
        else:
            # For non-lunar festivals, compute via engine
            from ...core.festivals import FestivalCategory as EC, Region as ER
            
            e_regions = [ER.ALL_INDIA]
            e_categories = [rule.category] if rule.category else [EC.MAJOR]
            
            festivals = festival_engine.calculate_festival_dates(
                year=year, regions=e_regions, categories=e_categories
            )
            
            matching = [f for f in festivals if f.festival_rule.name == rule.name]
            if not matching:
                raise HTTPException(status_code=404, detail=f"No date found for '{festival_name}' in {year}")
            
            festival_date = matching[0].date
            method = "engine"
        
        # 3. Compute panchang for that date at the user's location
        from datetime import timezone, timedelta
        
        # Use local noon as reference time
        dt_local = datetime(festival_date.year, festival_date.month, festival_date.day, 12, 0, 0)
        dt_utc = dt_local - timedelta(hours=timezone_offset)
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        
        panchang = kaal.get_panchang(
            lat=latitude,
            lon=longitude,
            dt=dt_utc,
            elevation=elevation,
            timezone_offset=timezone_offset,
        )
        
        # 4. Get tithi boundaries (start/end times)
        tithi_start = panchang.get("tithi_start")
        tithi_end = panchang.get("tithi_end_time", {})
        
        # 5. Build timing response
        result = {
            "festival": {
                "name": rule.name,
                "english_name": rule.english_name,
                "description": rule.description,
                "alternative_names": rule.alternative_names,
                "category": rule.category.value if rule.category else None,
                "type": rule.festival_type.value if rule.festival_type else None,
                "duration_days": rule.duration_days,
                "observance_time": rule.observance_time,
                "evening_start": rule.evening_start,
            },
            "date": str(festival_date),
            "year": year,
            "calculation_method": method,
            "location": {
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
                "timezone_offset": timezone_offset,
            },
            "tithi": {
                "number": float(panchang.get("tithi", 0)),
                "name": panchang.get("tithi_name", ""),
                "paksha": rule.paksha,
                "start_time": str(tithi_end.get("end_time")) if isinstance(tithi_end, dict) else None,
                "end_time": str(tithi_end.get("end_time")) if isinstance(tithi_end, dict) else None,
            },
            "sun_timings": {
                "sunrise": str(panchang.get("sunrise", "")),
                "sunset": str(panchang.get("sunset", "")),
                "solar_noon": str(panchang.get("solar_noon", "")),
            },
            "moon_timings": {
                "moonrise": str(panchang.get("moonrise", "")),
                "moonset": str(panchang.get("moonset", "")),
                "phase": panchang.get("moon_phase", ""),
                "illumination": float(panchang.get("moon_illumination", 0)),
            },
            "auspicious_timings": {
                "brahma_muhurta": {
                    "start": str(panchang.get("brahma_muhurta", {}).get("start", "")),
                    "end": str(panchang.get("brahma_muhurta", {}).get("end", "")),
                },
                "abhijit_muhurta": {
                    "start": str(panchang.get("abhijit_muhurta", {}).get("start", "")),
                    "end": str(panchang.get("abhijit_muhurta", {}).get("end", "")),
                },
            },
            "avoidance_timings": {
                "rahu_kaal": {
                    "start": str(panchang.get("rahu_kaal", {}).get("start", "")),
                    "end": str(panchang.get("rahu_kaal", {}).get("end", "")),
                },
                "yamaganda": {
                    "start": str(panchang.get("yamaganda_kaal", {}).get("start", "")),
                    "end": str(panchang.get("yamaganda_kaal", {}).get("end", "")),
                },
                "gulika": {
                    "start": str(panchang.get("gulika_kaal", {}).get("start", "")),
                    "end": str(panchang.get("gulika_kaal", {}).get("end", "")),
                },
            },
            "nakshatra": {
                "current": panchang.get("nakshatra", ""),
                "lord": panchang.get("nakshatra_lord", ""),
            },
            "yoga": {
                "number": float(panchang.get("yoga", 0)),
                "name": panchang.get("yoga_name", ""),
            },
            "karana": {
                "number": float(panchang.get("karana", 0)),
                "name": panchang.get("karana_name", ""),
            },
            "graha_positions": {
                p: {
                    "longitude": float(g.get("longitude", 0)),
                    "latitude": float(g.get("latitude", 0)),
                    "rashi": g.get("rashi", ""),
                    "nakshatra": g.get("nakshatra", ""),
                }
                for p, g in panchang.get("graha_positions", {}).items()
            },
            "chandrabala_tarabala": {
                "tarabala": panchang.get("tarabala", {}).get("tarabala", ""),
                "chandrabala": panchang.get("tarabala", {}).get("chandrabala", ""),
            },
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Festival timing calculation failed: {str(e)}",
        )
