#!/usr/bin/env python3
"""
Debug Solar Time Calculations
Test to see what exact Julian Day values are being returned
"""

import requests
import json
from datetime import datetime

# Test basic panchang for Delhi
BASE_URL = "http://localhost:8000"
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJicmFobWFfYWRtaW5fMjAyNSIsImVtYWlsIjoiYnJhaG1hQGJyYWhtYWthYWwuY29tIiwicm9sZSI6ImFkbWluIiwiZXhwIjo0OTA1MDkyMTkwLCJpYXQiOjE3NTE0OTIxOTAsInR5cGUiOiJhY2Nlc3MiLCJuZXZlcl9leHBpcmVzIjp0cnVlfQ.dPWn_XyeR7D10CFUFjgpk5fRDROVPckFYkqmVsWdyZc"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("🔍 Testing Delhi solar times for 2025-07-09...")

# Test Delhi
url = f"{BASE_URL}/v1/panchang"
params = {
    "latitude": 28.6139,
    "longitude": 77.209,
    "date": "2025-07-09",
    "time": "12:00:00",
    "timezone_offset": 5.5
}

response = requests.get(url, headers=headers, params=params)
if response.status_code == 200:
    data = response.json()
    
    print(f"✅ API Response received")
    print(f"📅 Request Date: 2025-07-09")
    print(f"🕐 Request Time: 12:00:00")
    print(f"🌍 Location: Delhi (28.6139°N, 77.209°E)")
    print(f"⏰ Timezone Offset: +5.5 hours")
    
    print(f"\n📊 Solar Time Results:")
    print(f"   🌅 Sunrise: {data.get('sunrise')}")
    print(f"   🌇 Sunset:  {data.get('sunset')}")
    print(f"   ☀️  Solar Noon: {data.get('solar_noon')}")
    print(f"   📏 Day Length: {data.get('day_length')} hours")
    
    # Expected values for Delhi on July 9, 2025
    print(f"\n✅ Expected Values (approximately):")
    print(f"   🌅 Sunrise: ~05:30 AM IST")
    print(f"   🌇 Sunset:  ~19:30 PM IST")
    print(f"   ☀️  Solar Noon: ~12:30 PM IST")
    print(f"   📏 Day Length: ~14 hours")
    
    # Parse the returned times
    try:
        sunrise = datetime.fromisoformat(data['sunrise'].replace('Z', '+00:00'))
        sunset = datetime.fromisoformat(data['sunset'].replace('Z', '+00:00'))
        solar_noon = datetime.fromisoformat(data['solar_noon'].replace('Z', '+00:00'))
        
        print(f"\n🔍 Analysis:")
        print(f"   📅 Sunrise Date: {sunrise.date()}")
        print(f"   🕐 Sunrise Time: {sunrise.time()}")
        print(f"   📅 Sunset Date: {sunset.date()}")
        print(f"   🕐 Sunset Time: {sunset.time()}")
        
        # Check if times are in correct range
        if sunrise.hour > 12:
            print(f"   ❌ ISSUE: Sunrise at {sunrise.hour}:00 is in PM, should be AM")
        elif 4 <= sunrise.hour <= 8:
            print(f"   ✅ Sunrise time looks reasonable")
        else:
            print(f"   ⚠️  Sunrise at {sunrise.hour}:00 seems unusual")
            
        if sunset.hour < 12:
            print(f"   ❌ ISSUE: Sunset at {sunset.hour}:00 is in AM, should be PM")
        elif 17 <= sunset.hour <= 21:
            print(f"   ✅ Sunset time looks reasonable")
        else:
            print(f"   ⚠️  Sunset at {sunset.hour}:00 seems unusual")
            
    except Exception as e:
        print(f"   ❌ ERROR parsing times: {e}")
        
else:
    print(f"❌ API Error: {response.status_code} - {response.text}")

print(f"\n💡 Additional Debug Info:")
print(f"   This test helps identify if the issue is in:")
print(f"   1. Julian Day calculation")
print(f"   2. Solar time calculation")
print(f"   3. Timezone conversion")
print(f"   4. DateTime formatting") 