#!/usr/bin/env python3
"""
Festival Scanner Test Runner

Tests the TithiScanner one festival at a time and saves results to a file.
Each test is independent so progress is saved even if timeout occurs.

Usage:
    python tests/run_festival_scanner_tests.py [festival_name]
    
    festival_name: Optional - run only one festival (or 'all' for all)
                   Default: all
                   Examples: Diwali, Dussehra, all
"""

import sys
import os
import time
import json
from datetime import date
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaal_engine.kaal import Kaal
from kaal_engine.core.festival_scanner import TithiScanner

RESULTS_FILE = Path(__file__).parent / "festival_scanner_results.json"

# All test cases
FESTIVAL_TESTS = [
    # (name, hindu_month, paksha, tithi_num, expected_approx)
    ("Diwali",                 "Kartik",      "krishna", 15, None),
    ("Holika Dahan",           "Phalguna",    "shukla",  15, None),  # night before Holi
    ("Rangwali Holi",          "Chaitra",     "krishna", 1,  None),
    ("Dussehra",               "Ashwin",      "shukla",  10, None),
    ("Sharad Navaratri start", "Ashwin",      "shukla",  1,  None),
    ("Chaitra Navaratri start","Chaitra",     "shukla",  1,  None),
    ("Ganesh Chaturthi",       "Bhadrapada",  "shukla",  4,  None),
    ("Maha Shivaratri",        "Magha",       "krishna", 14, None),
    ("Ram Navami",             "Chaitra",     "shukla",  9,  None),
    ("Guru Purnima",           "Ashadha",     "shukla",  15, None),
    ("Janmashtami",            "Bhadrapada",  "krishna", 8,  None),
    ("Karva Chauth",           "Kartik",      "krishna", 4,  None),
    ("Vasant Panchami",        "Magha",       "shukla",  5,  None),
    ("Dhanteras",              "Kartik",      "krishna", 13, None),
    ("Naraka Chaturdashi",     "Kartik",      "krishna", 14, None),
    ("Bhai Dooj",              "Kartik",      "shukla",  2,  None),
    ("Govardhan Puja",         "Kartik",      "shukla",  1,  None),
    ("Hanuman Jayanti",        "Chaitra",     "shukla",  15, None),
]

# Ekadashi test cases (all 24)
EKADASHI_MONTHS = [
    ("Chaitra", "krishna"), ("Chaitra", "shukla"),
    ("Vaishakha", "krishna"), ("Vaishakha", "shukla"),
    ("Jyeshtha", "krishna"), ("Jyeshtha", "shukla"),
    ("Ashadha", "krishna"), ("Ashadha", "shukla"),
    ("Shravana", "krishna"), ("Shravana", "shukla"),
    ("Bhadrapada", "krishna"), ("Bhadrapada", "shukla"),
    ("Ashwin", "krishna"), ("Ashwin", "shukla"),
    ("Kartik", "krishna"), ("Kartik", "shukla"),
    ("Margashirsha", "krishna"), ("Margashirsha", "shukla"),
    ("Pausha", "krishna"), ("Pausha", "shukla"),
    ("Magha", "krishna"), ("Magha", "shukla"),
    ("Phalguna", "krishna"), ("Phalguna", "shukla"),
]


def load_results():
    """Load previously saved results."""
    if RESULTS_FILE.exists():
        with open(RESULTS_FILE) as f:
            return json.load(f)
    return {"festivals": {}, "ekadashis": [], "metadata": {}}


def save_results(results):
    """Save results to file."""
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  💾 Results saved to {RESULTS_FILE}")


def test_festival(scanner, year, name, month, paksha, tithi_num):
    """Test one festival and return result."""
    print(f"\n{'='*60}")
    print(f"📅 Testing: {name}")
    print(f"   Rule: {month} {paksha.title()} {tithi_num}")
    print(f"   Year: {year}")
    print(f"{'='*60}")
    
    start = time.time()
    result = scanner.find_tithi_date(year, month, paksha, tithi_num, search_padding_days=20)
    elapsed = time.time() - start
    
    print(f"\n{'─'*60}")
    print(f"   Result: {result}")
    print(f"   Time:   {elapsed:.1f}s")
    print(f"{'─'*60}")
    
    return {
        "name": name,
        "month": month,
        "paksha": paksha,
        "tithi_num": tithi_num,
        "year": year,
        "result": str(result) if result else None,
        "elapsed_seconds": round(elapsed, 1),
        "status": "passed" if result else "failed"
    }


def test_ekadashi(scanner, year, month, paksha):
    """Test one Ekadashi."""
    name = f"{month} {paksha.title()} Ekadashi"
    print(f"\n  📅 {name}...", end=" ", flush=True)
    
    start = time.time()
    result = scanner.find_tithi_date(year, month, paksha, 11, search_padding_days=20)
    elapsed = time.time() - start
    
    status = "✅" if result else "❌"
    print(f"{status} {result} ({elapsed:.1f}s)")
    
    return {
        "name": name,
        "month": month,
        "paksha": paksha,
        "year": year,
        "result": str(result) if result else None,
        "elapsed_seconds": round(elapsed, 1),
        "status": "passed" if result else "failed"
    }


def main():
    # Parse args
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    
    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║   TithiScanner Validation — {year}              ║")
    print(f"╚══════════════════════════════════════════════════╝")
    
    # Initialize engine
    print(f"\n🔄 Initializing Kaal engine...")
    start = time.time()
    k = Kaal("de421.bsp")
    s = TithiScanner(k, lat=28.6139, lon=77.2090, timezone_offset=5.5)
    print(f"✅ Kaal engine ready ({time.time()-start:.1f}s)")
    
    # Load existing results
    results = load_results()
    if "festivals" not in results:
        results["festivals"] = {}
    if "ekadashis" not in results:
        results["ekadashis"] = []
    
    results["metadata"]["last_run"] = str(date.today())
    results["metadata"]["year"] = year
    
    if target.lower() == "all" or target.lower() == "festivals":
        # Run festival tests
        print(f"\n{'#'*60}")
        print(f"#   MAJOR FESTIVALS")
        print(f"{'#'*60}")
        
        year_key = str(year)
        if year_key not in results["festivals"]:
            results["festivals"][year_key] = {}
        
        for name, month, paksha, tithi_num, _ in FESTIVAL_TESTS:
            # Skip if already tested in this run
            if name in results["festivals"][year_key]:
                existing = results["festivals"][year_key][name]
                if existing.get("status") == "passed":
                    print(f"  ⏭ Skipping {name} (already passed: {existing['result']})")
                    continue
            
            result = test_festival(s, year, name, month, paksha, tithi_num)
            results["festivals"][year_key][name] = result
            save_results(results)
    
    if target.lower() == "all" or target.lower() == "ekadashis":
        # Run Ekadashi tests
        print(f"\n{'#'*60}")
        print(f"#   ALL EKADASHIS")
        print(f"{'#'*60}")
        
        for month, paksha in EKADASHI_MONTHS:
            name = f"{month} {paksha.title()} Ekadashi"
            
            # Skip if already tested
            existing = [e for e in results["ekadashis"] 
                       if e["name"] == name and e["year"] == year and e.get("status") == "passed"]
            if existing:
                print(f"  ⏭ Skipping {name} (already passed: {existing[0]['result']})")
                continue
            
            result = test_ekadashi(s, year, month, paksha)
            results["ekadashis"].append(result)
            save_results(results)
    
    elif target.lower() == "all" or target.lower() == "amavasya":
        print(f"\n{'#'*60}")
        print(f"#   ALL AMAVASYAS")
        print(f"{'#'*60}")
        
        amavasyas = []
        for month_name in TithiScanner.HINDU_MONTH_MAP:
            print(f"\n  📅 {month_name} Amavasya...", end=" ", flush=True)
            start = time.time()
            d = s.find_tithi_date(year, month_name, "krishna", 15, search_padding_days=20)
            elapsed = time.time() - start
            status = "✅" if d else "❌"
            print(f"{status} {d} ({elapsed:.1f}s)")
            if d:
                amavasyas.append({"month": month_name, "date": str(d)})
        
        results["amavasyas"] = amavasyas
        save_results(results)
    
    elif target.lower() == "all" or target.lower() == "purnima":
        print(f"\n{'#'*60}")
        print(f"#   ALL PURNIMAS")
        print(f"{'#'*60}")
        
        purnimas = []
        for month_name in TithiScanner.HINDU_MONTH_MAP:
            print(f"\n  📅 {month_name} Purnima...", end=" ", flush=True)
            start = time.time()
            d = s.find_tithi_date(year, month_name, "shukla", 15, search_padding_days=20)
            elapsed = time.time() - start
            status = "✅" if d else "❌"
            print(f"{status} {d} ({elapsed:.1f}s)")
            if d:
                purnimas.append({"month": month_name, "date": str(d)})
        
        results["purnimas"] = purnimas
        save_results(results)
    
    # Run single festival by name
    if target.lower() not in ("all", "festivals", "ekadashis", "amavasya", "purnima"):
        # Find the festival
        festival = None
        for f in FESTIVAL_TESTS:
            if f[0].lower() == target.lower():
                festival = f
                break
        
        if festival:
            name, month, paksha, tithi_num, _ = festival
            result = test_festival(s, year, name, month, paksha, tithi_num)
            
            year_key = str(year)
            if year_key not in results["festivals"]:
                results["festivals"][year_key] = {}
            results["festivals"][year_key][name] = result
            save_results(results)
        else:
            print(f"\n❌ Unknown festival: {target}")
            print(f"   Available: {', '.join(f[0] for f in FESTIVAL_TESTS)}")
            sys.exit(1)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    total_time = 0
    
    for year_key, festivals in results.get("festivals", {}).items():
        for name, result in festivals.items():
            status = result.get("status", "unknown")
            if status == "passed":
                passed += 1
            else:
                failed += 1
            total_time += result.get("elapsed_seconds", 0)
    
    for result in results.get("ekadashis", []):
        if result.get("status") == "passed":
            passed += 1
        else:
            failed += 1
        total_time += result.get("elapsed_seconds", 0)
    
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   ⏱  Total: {total_time:.0f}s ({total_time/60:.1f}m)")
    print(f"   📁 Saved: {RESULTS_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
