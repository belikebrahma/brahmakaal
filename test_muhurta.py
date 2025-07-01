"""
Comprehensive Test Suite for Muhurta Engine
Tests electional astrology functionality and auspicious timing calculations
"""

import unittest
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from kaal_engine.kaal import Kaal
from kaal_engine.core.muhurta import (
    MuhurtaEngine, MuhurtaType, MuhurtaQuality, MuhurtaRequest, MuhurtaResult,
    find_marriage_muhurta, find_business_muhurta, find_travel_muhurta
)

def test_muhurta_engine():
    """Test Muhurta Engine functionality"""
    print("\n" + "="*80)
    print("🚀 TESTING MUHURTA ENGINE - Phase 2 Implementation")
    print("="*80)
    
    try:
        # Initialize
        kaal = Kaal("de421.bsp")
        muhurta_engine = MuhurtaEngine(kaal)
        
        # Test coordinates - Ujjain (traditional reference)
        test_lat = 23.1765
        test_lon = 75.7885
        
        # Test dates
        test_start_date = datetime(2025, 1, 1, 6, 0, 0, tzinfo=timezone.utc)
        test_end_date = test_start_date + timedelta(days=2)  # Short range for testing
        
        print("🧪 Test 1: Engine Initialization")
        assert muhurta_engine is not None
        assert muhurta_engine.kaal is not None
        assert isinstance(muhurta_engine.cache, dict)
        print("✅ Engine initialization: PASSED")
        
        print("\n🧪 Test 2: Muhurta Rules")
        # Check marriage rules
        marriage_rules = muhurta_engine.marriage_rules
        assert 'favorable_tithis' in marriage_rules
        assert 'favorable_nakshatras' in marriage_rules
        assert 'avoid_nakshatras' in marriage_rules
        assert 'Rohini' in marriage_rules['favorable_nakshatras']
        assert 'Bharani' in marriage_rules['avoid_nakshatras']
        print("✅ Muhurta rules: PASSED")
        
        print("\n🧪 Test 3: Single Muhurta Calculation")
        test_datetime = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        result = muhurta_engine._calculate_muhurta(
            dt=test_datetime,
            muhurta_type=MuhurtaType.MARRIAGE,
            lat=test_lat,
            lon=test_lon,
            duration_minutes=60
        )
        
        assert isinstance(result, MuhurtaResult)
        assert result.datetime == test_datetime
        assert isinstance(result.quality, MuhurtaQuality)
        assert isinstance(result.score, float)
        assert 0 <= result.score <= 100
        assert isinstance(result.factors, dict)
        print(f"   Result: {result.quality.value} quality (Score: {result.score:.1f})")
        print("✅ Single muhurta calculation: PASSED")
        
        print("\n🧪 Test 4: Muhurta Finding")
        request = MuhurtaRequest(
            muhurta_type=MuhurtaType.MARRIAGE,
            start_date=test_start_date,
            end_date=test_end_date,
            latitude=test_lat,
            longitude=test_lon,
            duration_minutes=120
        )
        
        results = muhurta_engine.find_muhurta(request)
        assert isinstance(results, list)
        assert len(results) <= 20  # Should limit to 20 results
        
        if results:
            # Verify results are sorted by score
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score
            print(f"   Found {len(results)} suitable muhurta timings")
            print(f"   Best score: {results[0].score:.1f}")
        else:
            print("   No suitable muhurta timings found (acceptable for testing)")
        print("✅ Muhurta finding: PASSED")
        
        print("\n🧪 Test 5: Different Muhurta Types")
        muhurta_types = [MuhurtaType.MARRIAGE, MuhurtaType.BUSINESS, MuhurtaType.TRAVEL, MuhurtaType.EDUCATION]
        
        for muhurta_type in muhurta_types:
            result = muhurta_engine._calculate_muhurta(
                dt=test_datetime,
                muhurta_type=muhurta_type,
                lat=test_lat,
                lon=test_lon,
                duration_minutes=60
            )
            assert isinstance(result, MuhurtaResult)
            print(f"   {muhurta_type.value.title()}: {result.quality.value} (Score: {result.score:.1f})")
        print("✅ Different muhurta types: PASSED")
        
        print("\n🧪 Test 6: Convenience Functions")
        start_date = test_start_date
        end_date = start_date + timedelta(days=1)
        
        marriage_results = find_marriage_muhurta(kaal, start_date, end_date, test_lat, test_lon)
        business_results = find_business_muhurta(kaal, start_date, end_date, test_lat, test_lon)
        travel_results = find_travel_muhurta(kaal, start_date, end_date, test_lat, test_lon)
        
        assert isinstance(marriage_results, list)
        assert isinstance(business_results, list)
        assert isinstance(travel_results, list)
        print("✅ Convenience functions: PASSED")
        
        print("\n🧪 Test 7: Quality Determination")
        test_scores = [95, 85, 80, 70, 60, 45, 30, 10]
        expected_qualities = [
            MuhurtaQuality.EXCELLENT,   # 95
            MuhurtaQuality.EXCELLENT,   # 85
            MuhurtaQuality.VERY_GOOD,   # 80
            MuhurtaQuality.GOOD,        # 70
            MuhurtaQuality.AVERAGE,     # 60
            MuhurtaQuality.POOR,        # 45
            MuhurtaQuality.AVOID,       # 30
            MuhurtaQuality.AVOID        # 10
        ]
        
        for score, expected_quality in zip(test_scores, expected_qualities):
            actual_quality = muhurta_engine._determine_quality(score)
            assert actual_quality == expected_quality
        print("✅ Quality determination: PASSED")
        
        print("\n" + "="*80)
        print("🎉 ALL MUHURTA ENGINE TESTS PASSED! Phase 2 Muhurta Engine is operational.")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"❌ MUHURTA ENGINE TEST FAILED: {e}")
        print("="*80)
        return False

def main():
    """Run the Muhurta Engine test suite"""
    try:
        success = test_muhurta_engine()
        return 0 if success else 1
    except Exception as e:
        print(f"Critical error in muhurta test setup: {e}")
        return 1

if __name__ == '__main__':
    exit(main()) 