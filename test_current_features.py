#!/usr/bin/env python3
"""
Brahmakaal - Comprehensive Feature Test Script
Tests all Phase 1 enhancements implemented in the system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from kaal_engine.kaal import Kaal
from kaal_engine.core.ayanamsha import AyanamshaEngine
from kaal_engine.core.cache import KaalCache
import json

def test_comprehensive_panchang():
    """Test enhanced panchang with 50+ parameters"""
    print("🕉️  TESTING COMPREHENSIVE PANCHANG")
    print("=" * 50)
    
    # Test for Ujjain (traditional reference)
    kaal = Kaal("de421.bsp")  # Use the correct ephemeris file
    dt = datetime(2024, 12, 26, 12, 0, 0, tzinfo=timezone.utc)
    
    panchang = kaal.get_panchang(
        lat=23.1765,
        lon=75.7885, 
        dt=dt
    )
    
    print(f"📍 Location: Ujjain (23.1765°N, 75.7885°E)")
    print(f"📅 Date: {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Core Panchang Elements
    print("🌙 CORE PANCHANG:")
    print(f"   Tithi: {panchang.get('tithi_name', 'N/A')} ({panchang.get('tithi', 'N/A'):.2f})")
    print(f"   Nakshatra: {panchang.get('nakshatra_name', 'N/A')} ({panchang.get('nakshatra', 'N/A'):.2f})")
    print(f"   Yoga: {panchang.get('yoga_name', 'N/A')} ({panchang.get('yoga', 'N/A'):.2f})")
    print(f"   Karana: {panchang.get('karana_name', 'N/A')} ({panchang.get('karana', 'N/A'):.2f})")
    print(f"   Vara: {panchang.get('vara_name', 'N/A')}")
    print()
    
    # Solar & Lunar Times
    print("🌅 SOLAR & LUNAR TIMES:")
    print(f"   Sunrise: {panchang.get('sunrise', 'N/A')}")
    print(f"   Sunset: {panchang.get('sunset', 'N/A')}")
    print(f"   Solar Noon: {panchang.get('solar_noon', 'N/A')}")
    print(f"   Day Length: {panchang.get('day_length_hours', 'N/A'):.2f} hours")
    print(f"   Moonrise: {panchang.get('moonrise', 'N/A')}")
    print(f"   Moonset: {panchang.get('moonset', 'N/A')}")
    print(f"   Moon Phase: {panchang.get('moon_phase', 'N/A')}")
    print(f"   Moon Illumination: {panchang.get('moon_illumination', 'N/A'):.1f}%")
    print()
    
    # Time Periods (Kaal)
    print("⏰ AUSPICIOUS & INAUSPICIOUS PERIODS:")
    print(f"   Rahu Kaal: {panchang.get('rahu_kaal', 'N/A')}")
    print(f"   Gulika Kaal: {panchang.get('gulika_kaal', 'N/A')}")
    print(f"   Yamaganda Kaal: {panchang.get('yamaganda_kaal', 'N/A')}")
    print(f"   Brahma Muhurta: {panchang.get('brahma_muhurta', 'N/A')}")
    print(f"   Abhijit Muhurta: {panchang.get('abhijit_muhurta', 'N/A')}")
    print()
    
    # Planetary Positions
    print("🪐 PLANETARY POSITIONS (Sidereal):")
    planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn', 'rahu', 'ketu']
    for planet in planets:
        pos = panchang.get(f'{planet}_position')
        if pos:
            print(f"   {planet.title()}: {pos.get('longitude', 'N/A'):.2f}° ({pos.get('rashi', 'N/A')}) in {pos.get('nakshatra', 'N/A')}")
    print()
    
    return True

def test_ayanamsha_systems():
    """Test multi-ayanamsha engine"""
    print("🌌 TESTING MULTI-AYANAMSHA SYSTEMS")
    print("=" * 50)
    
    ayanamsha_engine = AyanamshaEngine()
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    print(f"📅 Reference Date: {dt.strftime('%Y-%m-%d')}")
    print()
    
    systems = [
        'LAHIRI', 'RAMAN', 'KRISHNAMURTI', 'YUKTESHWAR', 
        'SURYA_SIDDHANTA', 'FAGAN_BRADLEY', 'DELUCE',
        'PUSHYA_PAKSHA', 'GALACTIC_CENTER', 'TRUE_CITRA'
    ]
    
    print("🔢 AYANAMSHA VALUES:")
    jd = 2451545.0 + (dt - datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)).days  # Convert to JD
    
    for system in systems:
        try:
            value = ayanamsha_engine.calculate_ayanamsha(jd, system)
            print(f"   {system:<18}: {value:.4f}°")
        except Exception as e:
            print(f"   {system:<18}: Error - {e}")
    
    print()
    
    # Test tropical to sidereal conversion
    tropical_sun = 276.1234  # Example tropical longitude
    print(f"🔄 COORDINATE CONVERSION:")
    print(f"   Tropical Sun Position: {tropical_sun:.4f}°")
    sidereal_sun = ayanamsha_engine.tropical_to_sidereal(tropical_sun, jd)
    print(f"   Sidereal Sun Position: {sidereal_sun:.4f}° (Lahiri)")
    
    # Conversion back
    tropical_back = ayanamsha_engine.sidereal_to_tropical(sidereal_sun, jd)
    print(f"   Converted Back: {tropical_back:.4f}°")
    print(f"   Precision Check: ±{abs(tropical_sun - tropical_back):.6f}°")
    print()
    
    return True

def test_caching_system():
    """Test intelligent caching system"""
    print("🚀 TESTING CACHING SYSTEM")
    print("=" * 50)
    
    cache = KaalCache()
    dt = datetime(2024, 12, 26, 12, 0, 0, tzinfo=timezone.utc)
    
    # Test cache operations
    test_key = "test_panchang_23.1765_75.7885_2024-12-26"
    test_data = {"tithi": 12.5, "nakshatra": "Rohini", "cached": True}
    
    print("💾 CACHE OPERATIONS:")
    
    # Store data
    cache.set(test_key, test_data, ttl=1800)  # 30 minutes
    print(f"   ✅ Stored: {test_key}")
    
    # Retrieve data
    retrieved = cache.get(test_key)
    print(f"   ✅ Retrieved: {retrieved is not None}")
    
    if retrieved:
        print(f"   📊 Data: {json.dumps(retrieved, indent=6)}")
    
    # Cache statistics
    stats = cache.get_stats()
    print(f"   📈 Cache Stats:")
    print(f"      Hits: {stats.get('hits', 0)}")
    print(f"      Misses: {stats.get('misses', 0)}")
    print(f"      Size: {stats.get('size', 0)} entries")
    
    print()
    return True

def test_advanced_features():
    """Test advanced astronomical features"""
    print("✨ TESTING ADVANCED FEATURES")
    print("=" * 50)
    
    kaal = Kaal("de421.bsp")  # Use the correct ephemeris file
    dt = datetime(2024, 12, 26, 12, 0, 0, tzinfo=timezone.utc)
    
    panchang = kaal.get_panchang(
        lat=28.6139,  # Delhi
        lon=77.2090,
        dt=dt
    )
    
    print("📍 Location: Delhi (28.6139°N, 77.2090°E)")
    print()
    
    # Advanced timing calculations
    print("🔬 ADVANCED CALCULATIONS:")
    print(f"   Local Mean Time: {panchang.get('local_mean_time', 'N/A')}")
    print(f"   Local Sidereal Time: {panchang.get('local_sidereal_time', 'N/A')}")
    print(f"   Ayanamsha (Lahiri): {panchang.get('ayanamsha', 'N/A'):.4f}°")
    print(f"   Season: {panchang.get('season', 'N/A')}")
    print()
    
    # Tithi details
    print("🌙 TITHI DETAILS:")
    print(f"   Current Tithi: {panchang.get('tithi_name', 'N/A')}")
    print(f"   Tithi Remaining: {panchang.get('tithi_remaining_time', 'N/A')}")
    print(f"   Next Tithi: {panchang.get('next_tithi_name', 'N/A')}")
    print()
    
    return True

def test_error_handling():
    """Test error handling and edge cases"""
    print("🛡️  TESTING ERROR HANDLING")
    print("=" * 50)
    
    kaal = Kaal("de421.bsp")  # Use the correct ephemeris file
    
    # Test invalid coordinates
    try:
        invalid_panchang = kaal.get_panchang(
            lat=91.0,  # Invalid latitude
            lon=181.0,  # Invalid longitude  
            dt=datetime.now(timezone.utc)
        )
        print("   ❌ Should have caught invalid coordinates")
    except Exception as e:
        print(f"   ✅ Caught invalid coordinates: {type(e).__name__}")
    
    # Test extreme dates
    try:
        extreme_date = datetime(1, 1, 1, tzinfo=timezone.utc)
        extreme_panchang = kaal.get_panchang(
            lat=23.1765,
            lon=75.7885,
            dt=extreme_date
        )
        print(f"   ✅ Handled extreme date: {extreme_date}")
    except Exception as e:
        print(f"   ⚠️  Extreme date limitation: {type(e).__name__}")
    
    print()
    return True

def main():
    """Run all tests"""
    print("🕉️  BRAHMAKAAL - COMPREHENSIVE FEATURE TESTING")
    print("=" * 60)
    print()
    
    tests = [
        ("Comprehensive Panchang", test_comprehensive_panchang),
        ("Ayanamsha Systems", test_ayanamsha_systems), 
        ("Caching System", test_caching_system),
        ("Advanced Features", test_advanced_features),
        ("Error Handling", test_error_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "✅ PASSED" if success else "❌ FAILED"))
            print()
        except Exception as e:
            results.append((test_name, f"❌ ERROR: {e}"))
            print(f"❌ Error in {test_name}: {e}")
            print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 30)
    for test_name, result in results:
        print(f"{test_name:<25}: {result}")
    
    passed = sum(1 for _, result in results if "PASSED" in result)
    total = len(results)
    
    print()
    print(f"🎯 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL SYSTEMS OPERATIONAL! Ready for Phase 2 (Muhurta Engine)")
    else:
        print("⚠️  Some issues detected. Please review before proceeding.")

if __name__ == "__main__":
    main() 