#!/usr/bin/env python3
"""
Populate the festival_calendars table with pre-computed festival data.
Run once and festivals are served from DB instantly.
"""
import asyncio
import os
import sys
from datetime import datetime, date
from typing import List, Optional, Set

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from kaal_engine.kaal import Kaal
from kaal_engine.core.festivals import (
    FestivalEngine, FestivalCategory, Region as EngineRegion,
    FestivalType, FestivalRule, FestivalDate
)
from kaal_engine.config import settings
from kaal_engine.db.models import FestivalCalendar
from kaal_engine.db.database import Base


async def populate_festivals(
    start_year: int = 2020,
    end_year: int = 2030,
    database_url: Optional[str] = None,
    ephemeris_path: str = "de421.bsp",
    batch_size: int = 100,
    verbose: bool = True,
):
    """Compute and store all festivals in the database."""
    
    db_url = database_url or settings.database_url
    if not db_url:
        print("❌ No DATABASE_URL set. Use --db-url or set DATABASE_URL env var.")
        return 1
    
    print(f"📅 Populating festivals from {start_year} to {end_year}")
    print(f"🗄️  Database: {db_url[:50]}...")
    print(f"🌌 Ephemeris: {ephemeris_path}")
    print()
    
    # Init engine
    print("🔄 Initializing Kaal engine...")
    kaal = Kaal(ephemeris_path)
    festival_engine = FestivalEngine(kaal)
    print("✅ Engine ready")
    
    # Connect to DB
    print(f"🔄 Connecting to database...")
    engine = create_async_engine(db_url, echo=False)
    
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # All categories and regions to compute
    all_categories = [
        FestivalCategory.MAJOR,
        FestivalCategory.RELIGIOUS,
        FestivalCategory.SEASONAL,
        FestivalCategory.REGIONAL,
        FestivalCategory.SPIRITUAL,
        FestivalCategory.CULTURAL,
        FestivalCategory.ASTRONOMICAL,
    ]
    all_regions = [r for r in EngineRegion]
    
    total_stored = 0
    total_skipped = 0
    
    for year in range(start_year, end_year + 1):
        if verbose:
            print(f"\n📆 Year {year}: computing...")
        
        # Compute ALL festivals for this year
        festivals = festival_engine.calculate_festival_dates(
            year=year,
            regions=all_regions,
            categories=all_categories,
        )
        
        if verbose:
            print(f"   → {len(festivals)} festival dates computed")
        
        if not festivals:
            continue
        
        # Store in DB
        async with async_session() as session:
            # Delete existing entries for this year
            await session.execute(
                delete(FestivalCalendar).where(FestivalCalendar.year == year)
            )
            
            stored = 0
            for fd in festivals:
                rule = fd.festival_rule
                
                record = FestivalCalendar(
                    festival_name=rule.name,
                    english_name=rule.english_name,
                    festival_date=fd.date,
                    year=year,
                    festival_type=rule.festival_type.value if rule.festival_type else None,
                    category=rule.category.value if rule.category else None,
                    regions=list(set(r.value for r in (rule.regions or [EngineRegion.ALL_INDIA]))),
                    description=rule.description,
                    alternative_names=rule.alternative_names or [],
                    duration_days=rule.duration_days or 1,
                    observance_time=rule.observance_time or "full_day",
                    lunar_month=rule.month if hasattr(rule, 'month') else None,
                    paksha=rule.paksha if hasattr(rule, 'paksha') else None,
                    tithi=rule.tithi if hasattr(rule, 'tithi') else None,
                )
                session.add(record)
                stored += 1
            
            await session.commit()
            total_stored += stored
        
        if verbose:
            print(f"   ✅ {stored} festivals stored for {year}")
    
    print(f"\n{'='*50}")
    print(f"✅ Done! {total_stored} total festival entries stored ({start_year}-{end_year})")
    print(f"{'='*50}")
    
    await engine.dispose()
    return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-populate festival database")
    parser.add_argument("--start-year", type=int, default=2025, help="Start year (default: 2025)")
    parser.add_argument("--end-year", type=int, default=2027, help="End year (default: 2027)")
    parser.add_argument("--db-url", type=str, help="Database URL (default: from env)")
    parser.add_argument("--ephemeris", type=str, default="de421.bsp", help="Ephemeris file path")
    parser.add_argument("--verbose", "-v", action="store_true", default=True, help="Verbose output")
    
    args = parser.parse_args()
    
    exit(asyncio.run(populate_festivals(
        start_year=args.start_year,
        end_year=args.end_year,
        database_url=args.db_url,
        ephemeris_path=args.ephemeris,
        verbose=args.verbose,
    )))
