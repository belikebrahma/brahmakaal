#!/usr/bin/env python3
"""
Phase 4 Personalized Astrology API Tests
Testing the new natal chart, transit analysis, and personalized endpoints
"""

import asyncio
import json
import time
from datetime import datetime, date
from typing import Dict, Any

import httpx

# Test configuration
BASE_URL = "http://localhost:8000/v1"
TEST_TIMEOUT = 30.0

# Sample birth data for testing
SAMPLE_BIRTH_DATA = {
    "birth_date": "1990-06-15",
    "birth_time": "14:30:00",
    "birth_latitude": 28.6139,  # New Delhi
    "birth_longitude": 77.2090,
    "birth_timezone": "Asia/Kolkata",
    "birth_location_name": "New Delhi, India"
}

# Test API endpoints
TEST_ENDPOINTS = {
    "natal_chart": "/horoscope/natal-chart",
    "daily_transits": "/transits/daily", 
    "personalized_panchang": "/panchang/personalized",
    "personalized_muhurta": "/muhurta/personalized"
}

async def test_natal_chart_api():
    """Test natal chart generation API"""
    print("\n🌟 Testing Natal Chart API...")
    
    request_data = {
        "birth_data": SAMPLE_BIRTH_DATA,
        "ayanamsha": "LAHIRI",
        "include_insights": True,
        "include_yogas": True
    }
    
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{BASE_URL}{TEST_ENDPOINTS['natal_chart']}", 
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Natal Chart API: Success ({response.status_code})")
                print(f"   📊 Calculation time: {data.get('calculation_time_ms', 0)}ms")
                print(f"   🏠 Ascendant: {data.get('ascendant', {}).get('sign', 'Unknown')}")
                print(f"   🪐 Planets found: {len(data.get('planetary_positions', {}))}")
                
                # Check for key insights
                if data.get('key_insights'):
                    personality_traits = data['key_insights'].get('personality_traits', [])
                    print(f"   🧠 Personality traits: {', '.join(personality_traits[:3])}")
                
                # Check for yogas
                if data.get('planetary_yogas'):
                    yogas = [yoga['name'] for yoga in data['planetary_yogas']]
                    print(f"   🎯 Yogas detected: {', '.join(yogas[:2])}")
                
                return True
            else:
                print(f"❌ Natal Chart API failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Natal Chart API error: {str(e)}")
            return False

async def test_daily_transits_api():
    """Test daily transit analysis API"""
    print("\n🌌 Testing Daily Transits API...")
    
    request_data = {
        "birth_data": SAMPLE_BIRTH_DATA,
        "analysis_date": date.today().isoformat(),
        "ayanamsha": "LAHIRI",
        "include_predictions": True,
        "transit_types": ["all"]
    }
    
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{BASE_URL}{TEST_ENDPOINTS['daily_transits']}", 
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Daily Transits API: Success ({response.status_code})")
                print(f"   📊 Calculation time: {data.get('calculation_time_ms', 0)}ms")
                print(f"   🌙 Birth Moon sign: {data.get('birth_chart_reference', {}).get('moon_sign', 'Unknown')}")
                
                active_transits = data.get('active_transits', [])
                print(f"   🔄 Active transits: {len(active_transits)}")
                
                if active_transits:
                    # Show first few transits
                    for i, transit in enumerate(active_transits[:3]):
                        print(f"   🪐 {transit.get('transiting_planet', '').title()} {transit.get('aspect_type', '')} natal {transit.get('natal_planet', '').title()}")
                
                # Show daily summary
                summary = data.get('daily_summary', '')
                if summary:
                    print(f"   📋 Summary: {summary[:100]}...")
                
                return True
            else:
                print(f"❌ Daily Transits API failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Daily Transits API error: {str(e)}")
            return False

async def test_personalized_panchang_api():
    """Test personalized panchang API"""
    print("\n📅 Testing Personalized Panchang API...")
    
    request_data = {
        "birth_data": SAMPLE_BIRTH_DATA,
        "target_date": date.today().isoformat(),
        "target_time": "12:00:00",
        "location_latitude": 28.6139,  # Delhi
        "location_longitude": 77.2090,
        "ayanamsha": "LAHIRI",
        "include_transit_analysis": True,
        "recommendation_depth": "standard"
    }
    
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{BASE_URL}{TEST_ENDPOINTS['personalized_panchang']}", 
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Personalized Panchang API: Success ({response.status_code})")
                print(f"   📊 Calculation time: {data.get('calculation_time_ms', 0)}ms")
                
                # Check basic panchang
                basic_panchang = data.get('basic_panchang', {})
                if basic_panchang:
                    print(f"   🌙 Tithi: {basic_panchang.get('tithi_name', 'Unknown')}")
                    print(f"   ⭐ Nakshatra: {basic_panchang.get('nakshatra', 'Unknown')}")
                
                # Check personalized insights
                insights = data.get('personalized_insights', {})
                if insights:
                    favorable_periods = insights.get('favorable_periods', [])
                    print(f"   ✨ Favorable periods: {len(favorable_periods)}")
                    
                    if favorable_periods:
                        first_period = favorable_periods[0]
                        print(f"   🕐 Best time: {first_period.get('start_time', '')} - {first_period.get('end_time', '')} for {first_period.get('activity_type', '')}")
                
                # Check transit highlights
                transits = data.get('transit_highlights', [])
                print(f"   🔄 Transit highlights: {len(transits)}")
                
                return True
            else:
                print(f"❌ Personalized Panchang API failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Personalized Panchang API error: {str(e)}")
            return False

async def test_personalized_muhurta_api():
    """Test personalized muhurta API"""
    print("\n⏰ Testing Personalized Muhurta API...")
    
    from datetime import timedelta
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    request_data = {
        "birth_data": SAMPLE_BIRTH_DATA,
        "activity_type": "business",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "location_latitude": 28.6139,
        "location_longitude": 77.2090,
        "duration_minutes": 120,
        "ayanamsha": "LAHIRI",
        "min_quality": "good",
        "max_results": 5
    }
    
    async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{BASE_URL}{TEST_ENDPOINTS['personalized_muhurta']}", 
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Personalized Muhurta API: Success ({response.status_code})")
                print(f"   📊 Calculation time: {data.get('calculation_time_ms', 0)}ms")
                
                results = data.get('results', [])
                print(f"   🎯 Muhurta results found: {len(results)}")
                
                if results:
                    # Show best result
                    best = results[0]
                    print(f"   🥇 Best timing: {best.get('datetime', '')}")
                    print(f"   ⭐ Personal score: {best.get('personal_score', 0)}")
                    print(f"   📈 Standard score: {best.get('standard_score', 0)}")
                    
                    transit_support = best.get('transit_support', [])
                    if transit_support:
                        print(f"   🪐 Transit support: {', '.join(transit_support[:2])}")
                
                # Show birth chart factors
                birth_factors = data.get('birth_chart_factors', {})
                if birth_factors:
                    print(f"   🌙 Your Moon sign: {birth_factors.get('moon_sign', 'Unknown')}")
                
                return True
            else:
                print(f"❌ Personalized Muhurta API failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Personalized Muhurta API error: {str(e)}")
            return False

async def test_api_health():
    """Test if the API server is running"""
    print("🏥 Checking API health...")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API is healthy: {data.get('status', 'unknown')}")
                print(f"   🕰️ Uptime: {data.get('uptime_seconds', 0)} seconds")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to API: {str(e)}")
            print(f"   🔧 Make sure the API server is running on {BASE_URL}")
            return False

async def run_all_tests():
    """Run all Phase 4 API tests"""
    print("🚀 Starting Phase 4 Personalized Astrology API Tests")
    print("=" * 60)
    
    start_time = time.time()
    results = []
    
    # Test API health first
    health_ok = await test_api_health()
    if not health_ok:
        print("\n❌ API server is not available. Please start the server first.")
        return
    
    # Run all API tests
    test_functions = [
        test_natal_chart_api,
        test_daily_transits_api,
        test_personalized_panchang_api,
        test_personalized_muhurta_api
    ]
    
    for test_func in test_functions:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed with error: {str(e)}")
            results.append(False)
    
    # Test summary
    total_time = time.time() - start_time
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests passed: {passed}/{total}")
    print(f"⏱️ Total time: {total_time:.2f} seconds")
    
    if passed == total:
        print("🎉 All Phase 4 APIs are working correctly!")
        print("\n🔗 Available endpoints:")
        for name, endpoint in TEST_ENDPOINTS.items():
            print(f"   📡 {name}: POST {BASE_URL}{endpoint}")
        
        print("\n📚 Next steps:")
        print("   1. Check API documentation: http://localhost:8000/docs")
        print("   2. Test with your own birth data")
        print("   3. Integrate with your application")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
        print("🔧 Make sure all dependencies are installed and configured.")

if __name__ == "__main__":
    print("🕉️ Brahmakaal Phase 4 API Test Suite")
    print("Testing personalized astrology endpoints...\n")
    
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
    
    print("\n🙏 Testing complete.") 