#!/usr/bin/env python3
"""
Test Human-Readable Time Formatting Feature
"""

import requests
import json

def test_human_readable_times():
    print("🎨 Testing Human-Readable Time Formatting Feature")
    print("📅 Date: July 22, 2025, Delhi, India")
    print("=" * 80)
    
    url = "http://localhost:8000/v1/panchang"
    
    # Common parameters
    params = {
        "latitude": 28.6139,
        "longitude": 77.209,
        "date": "2025-07-22",
        "time": "12:00:00",
        "timezone_offset": 5.5
    }
    
    print("🔹 TEST 1: Default ISO Format (human_readable_times=false)")
    print("-" * 60)
    
    # Test with default formatting
    response1 = requests.get(url, params={**params, "human_readable_times": False})
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"   Sunrise:    {data1.get('sunrise', 'N/A')}")
        print(f"   Sunset:     {data1.get('sunset', 'N/A')}")
        print(f"   Solar Noon: {data1.get('solar_noon', 'N/A')}")
        print(f"   Moonrise:   {data1.get('moonrise', 'N/A')}")
        print(f"   Moonset:    {data1.get('moonset', 'N/A')}")
        
        # Show time periods
        rahu_kaal = data1.get('rahu_kaal', {})
        if rahu_kaal:
            print(f"   Rahu Kaal:  {rahu_kaal.get('start', 'N/A')} - {rahu_kaal.get('end', 'N/A')}")
    else:
        print(f"   ❌ Error: {response1.status_code}")
    
    print("\n🔹 TEST 2: Human-Readable Format (human_readable_times=true)")
    print("-" * 60)
    
    # Test with human-readable formatting
    response2 = requests.get(url, params={**params, "human_readable_times": True})
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"   Sunrise:    {data2.get('sunrise', 'N/A')}")
        print(f"   Sunset:     {data2.get('sunset', 'N/A')}")
        print(f"   Solar Noon: {data2.get('solar_noon', 'N/A')}")
        print(f"   Moonrise:   {data2.get('moonrise', 'N/A')}")
        print(f"   Moonset:    {data2.get('moonset', 'N/A')}")
        
        # Show time periods
        rahu_kaal = data2.get('rahu_kaal', {})
        if rahu_kaal:
            print(f"   Rahu Kaal:  {rahu_kaal.get('start', 'N/A')} - {rahu_kaal.get('end', 'N/A')}")
            
        brahma_muhurta = data2.get('brahma_muhurta', {})
        if brahma_muhurta:
            print(f"   Brahma Muhurta: {brahma_muhurta.get('start', 'N/A')} - {brahma_muhurta.get('end', 'N/A')}")
            
        abhijit_muhurta = data2.get('abhijit_muhurta', {})
        if abhijit_muhurta:
            print(f"   Abhijit Muhurta: {abhijit_muhurta.get('start', 'N/A')} - {abhijit_muhurta.get('end', 'N/A')}")
    else:
        print(f"   ❌ Error: {response2.status_code}")
    
    print("\n" + "=" * 80)
    print("✨ COMPARISON:")
    print("📊 ISO Format:      Full date-time with timezone (technical)")
    print("🎯 Human-Readable: Simple time format (user-friendly)")
    print("\n💡 Usage Examples:")
    print("   • Mobile apps: Use human_readable_times=true")
    print("   • APIs/Backend: Use human_readable_times=false (default)")
    print("   • User displays: Use human_readable_times=true")
    print("   • Data processing: Use human_readable_times=false")

if __name__ == "__main__":
    test_human_readable_times() 