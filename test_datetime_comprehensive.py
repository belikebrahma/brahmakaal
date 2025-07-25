#!/usr/bin/env python3
"""
Comprehensive DateTime Test for Brahmakaal API
Tests all endpoints and verifies logical consistency of time outputs
"""

import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Test configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJicmFobWFfYWRtaW5fMjAyNSIsImVtYWlsIjoiYnJhaG1hQGJyYWhtYWthYWwuY29tIiwicm9sZSI6ImFkbWluIiwiZXhwIjo0OTA1MDkyMTkwLCJpYXQiOjE3NTE0OTIxOTAsInR5cGUiOiJhY2Nlc3MiLCJuZXZlcl9leHBpcmVzIjp0cnVlfQ.dPWn_XyeR7D10CFUFjgpk5fRDROVPckFYkqmVsWdyZc"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Test locations
DELHI = {"lat": 28.6139, "lon": 77.209, "name": "Delhi, India", "tz": "Asia/Kolkata", "tz_offset": 5.5}
LONDON = {"lat": 51.5074, "lon": -0.1278, "name": "London, UK", "tz": "Europe/London", "tz_offset": 0.0}
NEW_YORK = {"lat": 40.7128, "lon": -74.0060, "name": "New York, USA", "tz": "America/New_York", "tz_offset": -5.0}

class DateTimeTestResults:
    def __init__(self):
        self.issues: List[Dict[str, Any]] = []
        self.passed_tests: List[str] = []
        
    def add_issue(self, test_name: str, issue_type: str, details: str, data: Any = None):
        self.issues.append({
            "test": test_name,
            "issue_type": issue_type,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_pass(self, test_name: str):
        self.passed_tests.append(test_name)
        
    def print_summary(self):
        print("\n" + "="*80)
        print("COMPREHENSIVE DATETIME TEST RESULTS")
        print("="*80)
        
        print(f"\n✅ PASSED TESTS: {len(self.passed_tests)}")
        for test in self.passed_tests:
            print(f"   ✓ {test}")
            
        print(f"\n❌ FAILED TESTS: {len(self.issues)}")
        for issue in self.issues:
            print(f"\n   ❌ {issue['test']}")
            print(f"      Issue: {issue['issue_type']}")
            print(f"      Details: {issue['details']}")
            if issue['data']:
                print(f"      Data: {json.dumps(issue['data'], indent=8, default=str)}")

def test_basic_panchang(location: Dict, test_date: str = "2025-07-09") -> Dict[str, Any]:
    """Test basic panchang endpoint"""
    url = f"{BASE_URL}/v1/panchang"
    params = {
        "latitude": location["lat"],
        "longitude": location["lon"], 
        "date": test_date,
        "time": "12:00:00",
        "timezone_offset": location["tz_offset"]
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def test_personalized_panchang(location: Dict, test_date: str = "2025-07-09") -> Dict[str, Any]:
    """Test personalized panchang endpoint"""
    url = f"{BASE_URL}/v1/panchang/personalized"
    data = {
        "birth_data": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "birth_latitude": location["lat"],
            "birth_longitude": location["lon"],
            "birth_timezone": location["tz"],
            "birth_location_name": location["name"]
        },
        "target_date": test_date,
        "target_time": "12:00:00",
        "location_latitude": location["lat"],
        "location_longitude": location["lon"],
        "ayanamsha": "LAHIRI"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def test_natal_chart(location: Dict) -> Dict[str, Any]:
    """Test natal chart endpoint"""
    url = f"{BASE_URL}/v1/horoscope/natal-chart"
    data = {
        "birth_data": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "birth_latitude": location["lat"],
            "birth_longitude": location["lon"],
            "birth_timezone": location["tz"],
            "birth_location_name": location["name"]
        },
        "ayanamsha": "LAHIRI"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def test_daily_transits(location: Dict, test_date: str = "2025-07-09") -> Dict[str, Any]:
    """Test daily transits endpoint"""
    url = f"{BASE_URL}/v1/transits/daily"
    data = {
        "birth_data": {
            "birth_date": "1990-05-15",
            "birth_time": "14:30:00",
            "birth_latitude": location["lat"],
            "birth_longitude": location["lon"],
            "birth_timezone": location["tz"]
        },
        "analysis_date": test_date,
        "ayanamsha": "LAHIRI"
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

def validate_solar_times(data: Dict[str, Any], location: Dict, test_name: str, results: DateTimeTestResults):
    """Validate sunrise/sunset times make logical sense"""
    
    sunrise_str = data.get('sunrise')
    sunset_str = data.get('sunset')
    solar_noon_str = data.get('solar_noon')
    
    if not sunrise_str or not sunset_str:
        results.add_issue(test_name, "MISSING_DATA", "Missing sunrise or sunset data")
        return
        
    try:
        # Parse datetime strings
        sunrise = datetime.fromisoformat(sunrise_str.replace('Z', '+00:00'))
        sunset = datetime.fromisoformat(sunset_str.replace('Z', '+00:00'))
        
        # Extract time components (hour)
        sunrise_hour = sunrise.hour
        sunset_hour = sunset.hour
        
        # Basic logical checks
        issues = []
        
        # Check if sunrise is in morning (typically 4-8 AM)
        if sunrise_hour > 12:
            issues.append(f"Sunrise at {sunrise_hour}:00 (PM) - should be in AM")
            
        # Check if sunset is in evening (typically 5-8 PM)  
        if sunset_hour < 12:
            issues.append(f"Sunset at {sunset_hour}:00 (AM) - should be in PM")
            
        # Check if sunset is after sunrise
        if sunset <= sunrise:
            issues.append(f"Sunset ({sunset_hour}:00) before sunrise ({sunrise_hour}:00)")
            
        # Check day length (should be positive and reasonable)
        day_length = data.get('day_length', 0)
        if day_length <= 0 or day_length > 24:
            issues.append(f"Invalid day length: {day_length} hours")
            
        if issues:
            results.add_issue(
                test_name, 
                "INVALID_SOLAR_TIMES", 
                "; ".join(issues),
                {
                    "sunrise": sunrise_str,
                    "sunset": sunset_str,
                    "sunrise_hour": sunrise_hour,
                    "sunset_hour": sunset_hour,
                    "day_length": day_length,
                    "location": location["name"]
                }
            )
        else:
            results.add_pass(f"{test_name} - Solar times validation")
            
    except Exception as e:
        results.add_issue(test_name, "DATETIME_PARSE_ERROR", f"Failed to parse times: {e}")

def validate_time_periods(data: Dict[str, Any], test_name: str, results: DateTimeTestResults):
    """Validate time periods like Rahu Kaal, Gulika Kaal"""
    
    time_periods = [
        ('rahu_kaal', 'Rahu Kaal'),
        ('gulika_kaal', 'Gulika Kaal'), 
        ('brahma_muhurta', 'Brahma Muhurta')
    ]
    
    for field_name, display_name in time_periods:
        period = data.get(field_name)
        if not period:
            continue
            
        try:
            start_str = period.get('start')
            end_str = period.get('end')
            
            if start_str and end_str:
                start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                
                if end <= start:
                    results.add_issue(
                        test_name,
                        "INVALID_TIME_PERIOD",
                        f"{display_name}: End time before start time",
                        {"start": start_str, "end": end_str}
                    )
                else:
                    results.add_pass(f"{test_name} - {display_name} validation")
                    
        except Exception as e:
            results.add_issue(test_name, "TIME_PERIOD_PARSE_ERROR", f"{display_name}: {e}")

def run_comprehensive_test():
    """Run comprehensive datetime tests across all endpoints and locations"""
    
    results = DateTimeTestResults()
    
    print("🔍 Starting Comprehensive DateTime Test...")
    print(f"Testing against: {BASE_URL}")
    print(f"Test Date: 2025-07-09")
    
    # Test locations
    locations = [DELHI, LONDON, NEW_YORK]
    
    for location in locations:
        print(f"\n📍 Testing location: {location['name']}")
        
        try:
            # Test 1: Basic Panchang
            print("  Testing basic panchang...")
            panchang_data = test_basic_panchang(location)
            validate_solar_times(panchang_data, location, f"Basic Panchang - {location['name']}", results)
            validate_time_periods(panchang_data, f"Basic Panchang - {location['name']}", results)
            
            # Test 2: Personalized Panchang  
            print("  Testing personalized panchang...")
            pers_panchang = test_personalized_panchang(location)
            basic_panchang = pers_panchang.get('basic_panchang', {})
            validate_solar_times(basic_panchang, location, f"Personalized Panchang - {location['name']}", results)
            validate_time_periods(basic_panchang, f"Personalized Panchang - {location['name']}", results)
            
            # Test 3: Natal Chart (birth times)
            print("  Testing natal chart...")
            natal_data = test_natal_chart(location)
            # Natal charts don't have solar times, just check for successful response
            if natal_data:
                results.add_pass(f"Natal Chart - {location['name']}")
            
            # Test 4: Daily Transits
            print("  Testing daily transits...")
            transit_data = test_daily_transits(location)
            if transit_data:
                results.add_pass(f"Daily Transits - {location['name']}")
                
        except Exception as e:
            results.add_issue(f"All APIs - {location['name']}", "API_ERROR", str(e))
    
    # Print comprehensive results
    results.print_summary()
    
    # Generate detailed report
    print("\n" + "="*80)
    print("DETAILED ANALYSIS")
    print("="*80)
    
    # Check for patterns in issues
    solar_time_issues = [i for i in results.issues if i['issue_type'] == 'INVALID_SOLAR_TIMES']
    if solar_time_issues:
        print("\n🔴 CRITICAL: Solar Time Issues Detected")
        print("   - Sunrise times appearing in PM")
        print("   - Sunset times appearing in AM") 
        print("   - This indicates datetime conversion problems in Julian Day handling")
        print("\n   LIKELY ROOT CAUSE:")
        print("   - _jd_to_datetime_with_timezone function is incorrectly combining")
        print("     time from JD calculation with target date")
        print("   - Should use the actual date derived from Julian Day")
        
    parse_errors = [i for i in results.issues if 'PARSE_ERROR' in i['issue_type']]
    if parse_errors:
        print("\n🟡 DateTime Parsing Issues:")
        for error in parse_errors:
            print(f"   - {error['details']}")
    
    print(f"\n📊 Test Summary:")
    print(f"   Total Tests: {len(results.passed_tests) + len(results.issues)}")
    print(f"   Passed: {len(results.passed_tests)}")
    print(f"   Failed: {len(results.issues)}")
    
    if results.issues:
        print("\n🚨 RECOMMENDATION: Fix the datetime conversion logic immediately")
        print("   The system is returning incorrect times which affects all calculations")
    else:
        print("\n✅ All datetime tests passed!")

if __name__ == "__main__":
    run_comprehensive_test() 