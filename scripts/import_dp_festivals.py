#!/usr/bin/env python3
"""
Import existing DP festival data into PostgreSQL.
No engine computation needed — uses already-validated DP dates for 2025-2027.
"""
import asyncio
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from kaal_engine.config import settings
from kaal_engine.db.models import FestivalCalendar
from kaal_engine.db.database import Base, process_database_url_for_asyncpg


def _import_years():
    """Yield (name, date_str, year) tuples from all DP calendar files."""
    for year in [2025, 2026, 2027]:
        path = f"data/reference/dp_calendar_{year}.json"
        if not os.path.exists(path):
            print(f"  ⚠️  {path} not found, skipping")
            continue
        with open(path) as f:
            entries = json.load(f)
        for entry in entries:
            yield entry["name"], entry["date"], entry["year"]


async def import_dp_festivals(database_url: str = None, verbose: bool = True):
    """Import DP reference data into festival_calendars table."""
    
    db_url = database_url or settings.database_url
    if not db_url or "postgresql" not in db_url:
        print("❌ No PostgreSQL DATABASE_URL set.")
        return 1
    
    if verbose:
        print(f"🗄️  Database: {db_url.split('@')[-1][:40]}...")
    
    # Use the same engine creation as the main app (handles sslmode)
    processed_url, connect_args = process_database_url_for_asyncpg(db_url)
    engine = create_async_engine(processed_url, echo=False, connect_args=connect_args)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Load all DP entries
    entries = list(_import_years())
    print(f"📅 Loaded {len(entries)} DP calendar entries (2025-2027)")
    
    # Group by name
    from collections import defaultdict
    name_map = defaultdict(dict)
    for name, date_str, year in entries:
        name_map[name][year] = date_str
    
    print(f"📋 {len(name_map)} unique festival names")
    
    # Load engine rules for category/regions mapping
    rules = []
    try:
        from kaal_engine.kaal import Kaal
        from kaal_engine.core.festivals import FestivalEngine
        k = Kaal("de421.bsp")
        fe = FestivalEngine(k)
        rules = fe.festival_rules
        
        rule_by_name = {}
        for r in rules:
            rule_by_name[r.name] = r
            if r.english_name:
                rule_by_name[r.english_name] = r
            for alt in (r.alternative_names or []):
                rule_by_name[alt] = r
        
        matched_count = sum(1 for n in name_map if n in rule_by_name)
        print(f"🎯 Matched {matched_count}/{len(name_map)} names to engine rules")
        unmatched = [n for n in name_map if n not in rule_by_name]
        if unmatched and verbose:
            print(f"  Unmatched ({len(unmatched)}): {', '.join(unmatched[:15])}")
            
    except Exception as e:
        print(f"  ⚠️  Engine rules unavailable: {e}")
        rule_by_name = {}
    
    # Store in DB
    total_stored = 0
    for year in [2025, 2026, 2027]:
        year_entries = [(n, d) for n, d, y in entries if y == year]
        if not year_entries:
            continue
        
        async with async_session() as session:
            # Clear existing for this year
            await session.execute(delete(FestivalCalendar).where(FestivalCalendar.year == year))
            
            stored = 0
            for name, date_str in year_entries:
                try:
                    fest_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue
                
                rule = rule_by_name.get(name)
                
                record = FestivalCalendar(
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
                    lunar_month=rule.month if rule and hasattr(rule, 'month') else None,
                    paksha=rule.paksha if rule and hasattr(rule, 'paksha') else None,
                    tithi=rule.tithi if rule and hasattr(rule, 'tithi') else None,
                )
                session.add(record)
                stored += 1
            
            await session.commit()
            total_stored += stored
            if verbose:
                print(f"  ✅ {year}: {stored} festivals stored")
    
    print(f"\n{'='*50}")
    print(f"✅ Done! {total_stored} DP festival entries imported ({2025}-{2027})")
    print(f"   Try: curl https://kaal.brah.ma/v1/festivals?year=2026")
    print(f"{'='*50}")
    
    await engine.dispose()
    return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import DP festival data into DB")
    parser.add_argument("--db-url", type=str, help="Database URL (default: from env)")
    args = parser.parse_args()
    exit(asyncio.run(import_dp_festivals(database_url=args.db_url)))
