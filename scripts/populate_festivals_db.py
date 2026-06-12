#!/usr/bin/env python3
"""
Populate the festival_calendars table with festival data.
Run once and festivals are served from DB instantly.

Strategy:
1. Fast path: Import existing DP reference data (2025-2027) — 30 seconds
2. Compute path: For other years, compute via engine (year by year, ~2-3 min each)
"""
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from kaal_engine.config import settings
from kaal_engine.db.models import FestivalCalendar
from kaal_engine.db.database import Base, process_database_url_for_asyncpg


async def populate_festivals(
    start_year: int = 2025,
    end_year: int = 2027,
    database_url: str = None,
    ephemeris_path: str = "de421.bsp",
    verbose: bool = True,
):
    """Populate festival DB using DP data (fast) + engine (batched)."""
    
    db_url = database_url or settings.database_url
    if not db_url or "postgresql" not in db_url:
        print("❌ No PostgreSQL DATABASE_URL set.")
        return 1
    
    processed_url, connect_args = process_database_url_for_asyncpg(db_url)
    engine = create_async_engine(processed_url, echo=False, connect_args=connect_args)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print(f"📅 Populating festivals: {start_year} to {end_year}")
    print(f"🗄️  DB: {db_url.split('@')[-1][:30]}...")
    
    # ─── Phase 1: Import DP data for years that match ───
    dp_years = range(max(start_year, 2025), min(end_year, 2027) + 1)
    
    from collections import defaultdict
    name_map = defaultdict(dict)
    entries = []
    
    import json
    for year in dp_years:
        path = f"data/reference/dp_calendar_{year}.json"
        if not os.path.exists(path):
            continue
        with open(path) as f:
            cal = json.load(f)
        for entry in cal:
            entries.append((entry["name"], entry["date"], entry["year"]))
            name_map[entry["name"]][entry["year"]] = entry["date"]
    
    if entries:
        print(f"\n📥 Phase 1: Importing {len(entries)} DP entries for {list(dp_years)}")
        
        # Load engine rules for enrichment
        try:
            from kaal_engine.kaal import Kaal
            from kaal_engine.core.festivals import FestivalEngine
            k = Kaal(ephemeris_path)
            fe = FestivalEngine(k)
            
            rule_by_name = {}
            for r in fe.festival_rules:
                rule_by_name[r.name] = r
                if r.english_name:
                    rule_by_name[r.english_name] = r
                for alt in (r.alternative_names or []):
                    rule_by_name[alt] = r
            print(f"   Loaded {len(fe.festival_rules)} engine rules for enrichment")
        except Exception as e:
            print(f"   ⚠️  Engine rules unavailable: {e}")
            rule_by_name = {}
        
        dp_stored = 0
        for year in dp_years:
            year_entries = [(n, d) for n, d, y in entries if y == year]
            if not year_entries:
                continue
            
            async with async_session() as session:
                await session.execute(delete(FestivalCalendar).where(FestivalCalendar.year == year))
                stored = 0
                for name, date_str, _ in year_entries:
                    try:
                        fest_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    except ValueError:
                        continue
                    
                    rule = rule_by_name.get(name)
                    session.add(FestivalCalendar(
                        festival_name=name,
                        english_name=rule.english_name if rule else name,
                        festival_date=fest_date,
                        year=year,
                        festival_type=rule.festival_type.value if rule and rule.festival_type else "LUNAR",
                        category=rule.category.value if rule and rule.category else "MAJOR",
                        regions=[r.value for r in rule.regions] if rule and rule.regions else ["all_india"],
                        description=rule.description if rule else "",
                        alternative_names=rule.alternative_names if rule else [],
                        duration_days=rule.duration_days if rule else 1,
                        observance_time=rule.observance_time if rule else "full_day",
                    ))
                    stored += 1
                await session.commit()
                dp_stored += stored
                print(f"   ✅ {year}: {stored} DP festivals imported")
        print(f"   Total: {dp_stored} DP entries imported")
    else:
        print(f"\n📥 Phase 1: No DP data for years {list(dp_years)}, skipping")
    
    # ─── Phase 2: Compute engine data for years WITHOUT DP coverage ───
    compute_years = [y for y in range(start_year, end_year + 1) if y not in dp_years]
    
    if compute_years:
        print(f"\n🔄 Phase 2: Computing engine data for {compute_years}")
        print(f"   (each year takes ~2-3 min, processing one at a time)")
        
        from kaal_engine.kaal import Kaal
        from kaal_engine.core.festivals import (
            FestivalEngine, FestivalCategory, Region as EngineRegion,
        )
        
        k = Kaal(ephemeris_path)
        fe = FestivalEngine(k)
        
        all_categories = [c for c in FestivalCategory]
        all_regions = [r for r in EngineRegion]
        engine_stored = 0
        
        for year in compute_years:
            print(f"\n   📆 Computing {year}...")
            
            festivals = fe.calculate_festival_dates(
                year=year,
                regions=all_regions,
                categories=all_categories,
            )
            print(f"   → {len(festivals)} dates computed")
            
            if not festivals:
                continue
            
            async with async_session() as session:
                await session.execute(delete(FestivalCalendar).where(FestivalCalendar.year == year))
                stored = 0
                for fd in festivals:
                    rule = fd.festival_rule
                    session.add(FestivalCalendar(
                        festival_name=rule.name,
                        english_name=rule.english_name,
                        festival_date=fd.date,
                        year=year,
                        festival_type=rule.festival_type.value if rule.festival_type else None,
                        category=rule.category.value if rule.category else None,
                        regions=[r.value for r in (rule.regions or [])],
                        description=rule.description,
                        alternative_names=rule.alternative_names or [],
                        duration_days=rule.duration_days or 1,
                        observance_time=rule.observance_time or "full_day",
                    ))
                    stored += 1
                await session.commit()
                engine_stored += stored
                print(f"   ✅ {year}: {stored} stored")
        
        print(f"\n   Total: {engine_stored} engine-computed entries stored")
    
    total_all = 0
    for year in range(start_year, end_year + 1):
        async with async_session() as session:
            from sqlalchemy import select, func
            result = await session.execute(select(func.count()).where(FestivalCalendar.year == year))
            count = result.scalar()
            if count:
                print(f"   Year {year}: {count} festivals in DB")
                total_all += count
    
    print(f"\n{'='*50}")
    print(f"✅ Done! {total_all} total festivals in DB ({start_year}-{end_year})")
    print(f"   Festivals endpoint will now return instantly from DB.")
    print(f"{'='*50}")
    
    await engine.dispose()
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Populate festival database (DP + engine)")
    parser.add_argument("--start-year", type=int, default=2025, help="Start year (default: 2025)")
    parser.add_argument("--end-year", type=int, default=2027, help="End year (default: 2027)")
    parser.add_argument("--db-url", type=str, help="Database URL (default: from env)")
    parser.add_argument("--ephemeris", type=str, default="de421.bsp", help="Ephemeris file path")
    args = parser.parse_args()
    exit(asyncio.run(populate_festivals(
        start_year=args.start_year,
        end_year=args.end_year,
        database_url=args.db_url,
        ephemeris_path=args.ephemeris,
    )))
