#!/usr/bin/env python3
"""
Test Delhi panchang for July 22, 2025 with human-readable time format
"""

import requests
from datetime import datetime
import json

def format_time_readable(iso_time_str):
    """Convert ISO time string to readable format like '6:20 AM'"""
    try:
        # Parse the ISO datetime string
        dt = datetime.fromisoformat(iso_time_str.replace('Z', '+00:00'))
        
        # Format to readable time
        return dt.strftime('%I:%M %p').lstrip('0')  # Remove leading zero from hour
    except Exception as e:
        return f"Error parsing {iso_time_str}: {e}"

def test_delhi_july22():
    print("🔍 Testing Delhi Panchang for July 22, 2025")
    print("📍 Location: Delhi, India (28.6139°N, 77.209°E)")
    print("🕐 Timezone: Asia/Kolkata (IST, UTC+5:30)")
    print("📅 Date: July 22, 2025")
    print("=" * 60)
    
    # Test basic panchang API
    url = "http://localhost:8000/v1/panchang"
    params = {
        "latitude": 28.6139,
        "longitude": 77.209,
        "date": "2025-07-22",
        "time": "12:00:00",
        "timezone_offset": 5.5  # IST is UTC+5:30
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            print("🌅 SOLAR TIMES:")
            print(f"   Sunrise:    {format_time_readable(data['sunrise'])}")
            print(f"   Sunset:     {format_time_readable(data['sunset'])}")
            print(f"   Solar Noon: {format_time_readable(data['solar_noon'])}")
            print(f"   Day Length: {data['day_length']:.2f} hours")
            
            print("\n🌙 LUNAR TIMES:")
            if data.get('moonrise'):
                print(f"   Moonrise:   {format_time_readable(data['moonrise'])}")
            else:
                print("   Moonrise:   No moonrise today")
                
            if data.get('moonset'):
                print(f"   Moonset:    {format_time_readable(data['moonset'])}")
            else:
                print("   Moonset:    No moonset today")
                
            print(f"   Moon Phase: {data['moon_phase']}")
            print(f"   Moon Illumination: {data['moon_illumination']:.1f}%")
            
            print("\n🕰️  AUSPICIOUS TIMES:")
            rahu_kaal = data.get('rahu_kaal', {})
            if rahu_kaal:
                print(f"   Rahu Kaal:  {format_time_readable(rahu_kaal['start'])} - {format_time_readable(rahu_kaal['end'])}")
            
            gulika_kaal = data.get('gulika_kaal', {})
            if gulika_kaal:
                print(f"   Gulika Kaal: {format_time_readable(gulika_kaal['start'])} - {format_time_readable(gulika_kaal['end'])}")
                
            yamaganda_kaal = data.get('yamaganda_kaal', {})
            if yamaganda_kaal:
                print(f"   Yamaganda:  {format_time_readable(yamaganda_kaal['start'])} - {format_time_readable(yamaganda_kaal['end'])}")
                
            brahma_muhurta = data.get('brahma_muhurta', {})
            if brahma_muhurta:
                print(f"   Brahma Muhurta: {format_time_readable(brahma_muhurta['start'])} - {format_time_readable(brahma_muhurta['end'])}")
                
            abhijit_muhurta = data.get('abhijit_muhurta', {})
            if abhijit_muhurta:
                print(f"   Abhijit Muhurta: {format_time_readable(abhijit_muhurta['start'])} - {format_time_readable(abhijit_muhurta['end'])}")
            
            print("\n📚 PANCHANG ELEMENTS:")
            print(f"   Tithi:      {data['tithi_name']} ({data['tithi']:.1f})")
            
            tithi_end = data.get('tithi_end_time', {})
            if tithi_end and tithi_end.get('end_time'):
                print(f"   Tithi Ends: {format_time_readable(tithi_end['end_time'])} ({tithi_end.get('percentage_complete', 0):.1f}% complete)")
            
            print(f"   Nakshatra:  {data['nakshatra']} (Lord: {data['nakshatra_lord']})")
            
            nakshatra_end = data.get('nakshatra_end_time', {})
            if nakshatra_end and nakshatra_end.get('end_time'):
                print(f"   Nakshatra Ends: {format_time_readable(nakshatra_end['end_time'])} ({nakshatra_end.get('percentage_complete', 0):.1f}% complete)")
            
            print(f"   Yoga:       {data['yoga_name']}")
            print(f"   Karana:     {data['karana_name']}")
            
            print("\n" + "=" * 60)
            print("✅ Test completed successfully!")
            print("\n💡 You can verify these times against:")
            print("   - Drik Panchang (drikpanchang.com)")
            print("   - Prokerala Panchang")
            print("   - Any reliable Vedic calendar")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_delhi_july22() 