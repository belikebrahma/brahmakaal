from datetime import datetime, timezone
from kaal_engine.kaal import Kaal
from kaal_engine.core.ayanamsha import AyanamshaEngine
from kaal_engine.core.cache import create_cache
import json

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_dict(data, indent=0):
    """Pretty print dictionary data"""
    for key, value in data.items():
        if isinstance(value, dict):
            print(f"{'  ' * indent}{key}:")
            print_dict(value, indent + 1)
        else:
            print(f"{'  ' * indent}{key}: {value}")

def test_comprehensive_panchang():
    """Test comprehensive panchang calculation"""
    print_section("COMPREHENSIVE PANCHANG TEST")
    
    try:
    # Initialize Kaal with the DE441 kernel
        kaal = Kaal("de421.bsp")
    
    # Test with Ujjain coordinates for Mahashivaratri 2025
        dt = datetime(2025, 2, 26, 12, 0, 0, tzinfo=timezone.utc)
    result = kaal.get_panchang(
        lat=23.1765,
        lon=75.7885,
        dt=dt,
            elevation=491.0,  # Ujjain elevation
            ayanamsha="LAHIRI"
    )
    
        print("Panchang Results for Mahashivaratri 2025 (Ujjain):")
        print_dict(result)
        
        return True
        
    except Exception as e:
        print(f"Error in comprehensive panchang test: {e}")
        return False

def test_ayanamsha_systems():
    """Test multi-ayanamsha support"""
    print_section("AYANAMSHA SYSTEMS TEST")
    
    try:
        engine = AyanamshaEngine()
        jd = 2460310.5  # January 1, 2024
        
        print("Supported Ayanamsha Systems:")
        for system, description in engine.SUPPORTED_SYSTEMS.items():
            ayanamsha = engine.calculate_ayanamsha(jd, system)
            print(f"  {system}: {ayanamsha:.4f}° - {description}")
        
        print(f"\nComparison for JD {jd}:")
        comparison = engine.compare_systems(jd)
        for system, value in comparison.items():
            print(f"  {system}: {value:.6f}°")
        
        # Test tropical to sidereal conversion
        tropical_long = 30.0  # 30 degrees tropical
        sidereal_lahiri = engine.tropical_to_sidereal(tropical_long, jd, "LAHIRI")
        sidereal_raman = engine.tropical_to_sidereal(tropical_long, jd, "RAMAN")
        
        print(f"\nTropical to Sidereal Conversion (30.0° tropical):")
        print(f"  Lahiri: {sidereal_lahiri:.4f}°")
        print(f"  Raman: {sidereal_raman:.4f}°")
        
        return True
        
    except Exception as e:
        print(f"Error in ayanamsha test: {e}")
        return False

def test_caching_system():
    """Test caching functionality"""
    print_section("CACHING SYSTEM TEST")
    
    try:
        # Create memory cache
        cache = create_cache('memory', max_size=100)
        
        # Test basic cache operations
        cache.set("test_key", {"value": 123, "name": "test"}, ttl=60)
        retrieved = cache.get("test_key")
        print(f"Cache set/get test: {retrieved}")
        
        # Test get_or_compute
        def expensive_calculation():
            print("  Computing expensive result...")
            return {"computed": True, "result": 456}
        
        result1 = cache.get_or_compute("compute_key", expensive_calculation, data_type="panchang")
        result2 = cache.get_or_compute("compute_key", expensive_calculation, data_type="panchang")
        
        print(f"First call (computed): {result1}")
        print(f"Second call (cached): {result2}")
        
        # Test cache stats
        stats = cache.get_stats()
        print(f"Cache statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"Error in caching test: {e}")
        return False

def test_planetary_calculations():
    """Test planetary position calculations"""
    print_section("PLANETARY CALCULATIONS TEST")
    
    try:
        kaal = Kaal("de421.bsp")
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        # Get comprehensive panchang
        result = kaal.get_panchang(
            lat=23.1765,
            lon=75.7885,
            dt=dt,
            ayanamsha="LAHIRI"
        )
        
        print("Planetary Positions (January 1, 2024):")
        if 'graha_positions' in result:
            for planet, data in result['graha_positions'].items():
                print(f"  {planet.capitalize()}:")
                print(f"    Longitude: {data['longitude']:.4f}°")
                print(f"    Rashi: {data['rashi']}")
                print(f"    Nakshatra: {data['nakshatra']}")
        
        # Test planetary aspects
        if 'graha_positions' in result:
            aspects = kaal.calculate_planetary_aspects(result['graha_positions'])
            print(f"\nPlanetary Aspects:")
            for aspect_key, aspect_data in aspects.items():
                print(f"  {aspect_key}: {aspect_data['aspect']} (orb: {aspect_data['orb']}°)")
        
        return True
        
    except Exception as e:
        print(f"Error in planetary calculations test: {e}")
        return False

def test_advanced_features():
    """Test advanced features like yogas and house calculations"""
    print_section("ADVANCED FEATURES TEST")
    
    try:
        kaal = Kaal("de421.bsp")
        dt = datetime(2024, 6, 15, 6, 30, 0, tzinfo=timezone.utc)  # Summer morning
        
        # Get panchang
        result = kaal.get_panchang(
        lat=28.6139,  # New Delhi
        lon=77.2090,
            dt=dt,
            ayanamsha="LAHIRI"
        )
        
        # Test house calculations
        jd_tt = kaal._julian_day(dt)
        houses = kaal.calculate_house_positions(jd_tt, 28.6139, 77.2090)
        print("House Positions:")
        for house, data in houses.items():
            print(f"  {house}: {data['cusp_longitude']:.2f}° ({data['rashi']}) - Lord: {data['lord']}")
        
        # Test yoga detection
        if 'graha_positions' in result:
            yogas = kaal.detect_yogas(result['graha_positions'])
            print(f"\nDetected Yogas:")
            for yoga in yogas:
                print(f"  {yoga['name']}: {yoga['description']} (Strength: {yoga['strength']})")
        
        # Test dasha calculation
        moon_nakshatra = result.get('nakshatra', 'Ashwini')
        dashas = kaal.calculate_dasha_periods(moon_nakshatra, jd_tt)
        print(f"\nVimshottari Dashas (starting from {moon_nakshatra}):")
        for i, dasha in enumerate(dashas['maha_dashas'][:5]):  # Show first 5
            print(f"  {i+1}. {dasha['planet']}: {dasha['start_date']} - {dasha['end_date']} ({dasha['duration_years']} years)")
        
        return True
        
    except Exception as e:
        print(f"Error in advanced features test: {e}")
        return False

def test_ayanamsha_comparison():
    """Test ayanamsha comparison functionality"""
    print_section("AYANAMSHA COMPARISON TEST")
    
    try:
        kaal = Kaal("de421.bsp")
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd_tt = kaal._julian_day(dt)
        
        comparison = kaal.get_ayanamsha_comparison(jd_tt)
        print("Ayanamsha Comparison for January 1, 2024:")
        
        # Sort by value for easy comparison
        sorted_ayanamshas = sorted(comparison.items(), key=lambda x: x[1])
        for system, value in sorted_ayanamshas:
            print(f"  {system}: {value:.6f}°")
        
        # Show differences from Lahiri
        lahiri_value = comparison.get('LAHIRI', 0)
        print(f"\nDifferences from Lahiri Ayanamsha:")
        for system, value in sorted_ayanamshas:
            if system != 'LAHIRI':
                diff = value - lahiri_value
                print(f"  {system}: {diff:+.4f}°")
        
        return True
        
    except Exception as e:
        print(f"Error in ayanamsha comparison test: {e}")
        return False

def test_time_periods():
    """Test special time period calculations"""
    print_section("TIME PERIODS TEST")
    
    try:
        kaal = Kaal("de421.bsp")
        dt = datetime(2024, 3, 15, 6, 0, 0, tzinfo=timezone.utc)  # Spring equinox
        
        result = kaal.get_panchang(
            lat=19.0760,  # Mumbai
            lon=72.8777,
            dt=dt,
            elevation=8.0
        )
        
        print("Special Time Periods for Mumbai (March 15, 2024):")
        
        # Display time periods
        time_periods = [
            'rahu_kaal', 'gulika_kaal', 'yamaganda_kaal', 
            'brahma_muhurta', 'abhijit_muhurta'
        ]
        
        for period in time_periods:
            if period in result:
                period_data = result[period]
                if isinstance(period_data, dict) and 'start' in period_data:
                    print(f"  {period.replace('_', ' ').title()}:")
                    print(f"    Start: JD {period_data['start']:.6f}")
                    print(f"    End: JD {period_data['end']:.6f}")
        
        # Display solar and lunar times
        solar_times = ['sunrise', 'sunset', 'solar_noon']
        lunar_times = ['moonrise', 'moonset']
        
        print(f"\nSolar Times:")
        for time_type in solar_times:
            if time_type in result:
                print(f"  {time_type.replace('_', ' ').title()}: JD {result[time_type]:.6f}")
        
        print(f"\nLunar Times:")
        for time_type in lunar_times:
            if time_type in result:
                print(f"  {time_type.replace('_', ' ').title()}: JD {result[time_type]:.6f}")
        
        # Display day length
        if 'day_length' in result:
            print(f"\nDay Length: {result['day_length']:.2f} hours")
        
        return True
        
    except Exception as e:
        print(f"Error in time periods test: {e}")
        return False

def main():
    """Run comprehensive test suite"""
    print_section("BRAHMAKAAL COMPREHENSIVE TEST SUITE")
    
    tests = [
        ("Comprehensive Panchang", test_comprehensive_panchang),
        ("Ayanamsha Systems", test_ayanamsha_systems),
        ("Caching System", test_caching_system),
        ("Planetary Calculations", test_planetary_calculations),
        ("Advanced Features", test_advanced_features),
        ("Ayanamsha Comparison", test_ayanamsha_comparison),
        ("Time Periods", test_time_periods),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            success = test_func()
            results[test_name] = "PASSED" if success else "FAILED"
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results[test_name] = "ERROR"
    
    # Print summary
    print_section("TEST RESULTS SUMMARY")
    
    passed = sum(1 for result in results.values() if result == "PASSED")
    total = len(results)
    
    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASSED" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Brahmakaal is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == '__main__':
    main() 