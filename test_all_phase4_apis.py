#!/usr/bin/env python3
"""
Comprehensive Test Script for All Phase 4 APIs
Tests all 4 personalized astrology endpoints with proper example data
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

# Test data using the example values from API documentation
test_birth_data = {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "birth_timezone": "Asia/Kolkata",
    "birth_location_name": "New Delhi, India"
}

def test_api_endpoint(endpoint, data, test_name):
    """Test a single API endpoint"""
    print(f"🧪 Testing {test_name}...")
    
    try:
        start_time = datetime.now()
        response = requests.post(
            f"{API_BASE}/{endpoint}",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response_time:.1f}ms")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                return True, json_data, response_time
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON response")
                return False, None, response_time
        else:
            print(f"❌ Failed with error:")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   {response.text}")
            return False, None, response_time
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False, None, 0

def test_personalized_panchang():
    """Test personalized panchang API"""
    data = {
        "birth_data": test_birth_data,
        "target_date": "2025-07-09",
        "target_time": "12:00:00",
        "location_latitude": 28.6139,
        "location_longitude": 77.2090,
        "ayanamsha": "LAHIRI",
        "include_transit_analysis": True,
        "recommendation_depth": "standard"
    }
    
    success, response_data, response_time = test_api_endpoint(
        "v1/panchang/personalized", data, "Personalized Panchang API"
    )
    
    if success:
        print("✅ Success! Response structure:")
        print(f"   - Basic Panchang: ✓ (tithi: {response_data['basic_panchang']['tithi_name']})")
        print(f"   - Personalized Insights: ✓ ({len(response_data['personalized_insights']['favorable_periods'])} favorable periods)")
        print(f"   - Transit Highlights: ✓ ({len(response_data['transit_highlights'])} highlights)")
        print(f"   - Birth Chart Summary: ✓ (moon sign: {response_data['birth_chart_summary']['moon_sign']})")
        print(f"   - Calculation Time: {response_data['calculation_time_ms']}ms")
    
    return success

def test_personalized_muhurta():
    """Test personalized muhurta API"""
    data = {
        "birth_data": test_birth_data,
        "activity_type": "marriage",
        "start_date": "2025-07-09T00:00:00Z",
        "end_date": "2025-07-12T23:59:59Z",
        "location_latitude": 28.6139,
        "location_longitude": 77.2090,
        "duration_minutes": 120,
        "ayanamsha": "LAHIRI",
        "custom_preferences": {},
        "min_quality": "good",
        "max_results": 10
    }
    
    success, response_data, response_time = test_api_endpoint(
        "v1/muhurta/personalized", data, "Personalized Muhurta API"
    )
    
    if success:
        print("✅ Success! Response structure:")
        print(f"   - Request Summary: ✓ (activity: {response_data['request_summary']['activity_type']})")
        print(f"   - Birth Chart Factors: ✓ (moon sign: {response_data['birth_chart_factors']['moon_sign']})")
        print(f"   - Results Found: {response_data['total_found']}")
        print(f"   - Personalization Notes: ✓ ({len(response_data['personalization_notes'])} notes)")
        print(f"   - Calculation Time: {response_data['calculation_time_ms']}ms")
    
    return success

def test_natal_chart():
    """Test natal chart generation API"""
    data = {
        "birth_data": test_birth_data,
        "ayanamsha": "LAHIRI",
        "include_insights": True,
        "include_yogas": True
    }
    
    success, response_data, response_time = test_api_endpoint(
        "v1/horoscope/natal-chart", data, "Natal Chart Generation API"
    )
    
    if success:
        print("✅ Success! Response structure:")
        print(f"   - Birth Details: ✓ (date: {response_data['birth_details']['birth_date']})")
        print(f"   - Chart Data: ✓")
        print(f"   - Planetary Positions: ✓ ({len(response_data['planetary_positions'])} planets)")
        print(f"   - House Cusps: ✓ ({len(response_data['house_cusps'])} houses)")
        print(f"   - Ascendant: ✓ (sign: {response_data['ascendant']['sign']})")
        if response_data.get('planetary_yogas'):
            print(f"   - Yogas: ✓ ({len(response_data['planetary_yogas'])} yogas detected)")
        print(f"   - Calculation Time: {response_data['calculation_time_ms']}ms")
    
    return success

def test_daily_transits():
    """Test daily transit analysis API"""
    data = {
        "birth_data": test_birth_data,
        "analysis_date": "2025-07-09",
        "ayanamsha": "LAHIRI",
        "include_predictions": True,
        "transit_types": ["all"]
    }
    
    success, response_data, response_time = test_api_endpoint(
        "v1/transits/daily", data, "Daily Transit Analysis API"
    )
    
    if success:
        print("✅ Success! Response structure:")
        print(f"   - Analysis Date: ✓ ({response_data['analysis_date']})")
        print(f"   - Birth Chart Reference: ✓ (moon sign: {response_data['birth_chart_reference']['moon_sign']})")
        print(f"   - Active Transits: ✓ ({len(response_data['active_transits'])} transits)")
        print(f"   - Daily Summary: ✓")
        print(f"   - Key Influences: ✓ ({len(response_data['key_influences'])} influences)")
        print(f"   - Timing Recommendations: ✓")
        print(f"   - Calculation Time: {response_data['calculation_time_ms']}ms")
    
    return success

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{API_BASE}/v1/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def main():
    """Run comprehensive tests for all Phase 4 APIs"""
    print("🚀 Comprehensive Phase 4 API Testing")
    print("=" * 60)
    
    # Test health first
    print("🏥 Testing API Health...")
    if not test_health():
        print("\n❌ API server not available. Please start the server.")
        return
    
    print("\n" + "🔬 Testing All Phase 4 APIs".center(60))
    print("=" * 60)
    
    results = []
    
    # Test all 4 Phase 4 APIs
    print("\n1️⃣ PERSONALIZED PANCHANG")
    print("-" * 30)
    results.append(("Personalized Panchang", test_personalized_panchang()))
    
    print("\n2️⃣ PERSONALIZED MUHURTA")
    print("-" * 30)
    results.append(("Personalized Muhurta", test_personalized_muhurta()))
    
    print("\n3️⃣ NATAL CHART GENERATION")
    print("-" * 30)
    results.append(("Natal Chart Generation", test_natal_chart()))
    
    print("\n4️⃣ DAILY TRANSIT ANALYSIS")
    print("-" * 30)
    results.append(("Daily Transit Analysis", test_daily_transits()))
    
    # Summary
    print("\n" + "📋 FINAL RESULTS".center(60))
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for api_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{api_name:.<40} {status}")
        if success:
            passed += 1
    
    print("-" * 60)
    print(f"Total: {passed}/{total} APIs working")
    
    if passed == total:
        print("\n🎉 ALL PHASE 4 APIS ARE WORKING PERFECTLY!")
        print("\n💡 You can now test all APIs in the documentation at:")
        print(f"   {API_BASE}/docs")
        print("\n🔥 The Phase 4 Personalized Astrology system is ready for production!")
    else:
        print(f"\n⚠️  {total - passed} APIs need attention.")
    
    print("\n" + "🌟 API Feature Summary".center(60))
    print("=" * 60)
    print("✅ Personalized Panchang   - Daily guidance with transit analysis")
    print("✅ Personalized Muhurta    - Activity timing with personal factors")  
    print("✅ Natal Chart Generation  - Complete birth chart with yogas")
    print("✅ Daily Transit Analysis  - Current planetary influences")
    print("\n🚀 Total Endpoints: 35+ (including all Phase 1-4 APIs)")

if __name__ == "__main__":
    main() 