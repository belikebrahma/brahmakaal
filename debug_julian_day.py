#!/usr/bin/env python3
"""
Debug Julian Day to DateTime Conversion
Test to understand the conversion process step by step
"""

from datetime import datetime, timezone, timedelta
from skyfield.api import load, Topos
from skyfield.almanac import find_discrete, sunrise_sunset

def test_julian_day_conversion():
    """Test Julian Day conversion process step by step"""
    
    print("🔍 Testing Julian Day to DateTime Conversion for Delhi")
    print("="*60)
    
    # Delhi coordinates
    lat, lon = 28.6139, 77.209
    
    # Create test date
    test_date = datetime(2025, 7, 9, 12, 0, 0)
    print(f"📅 Test Date: {test_date}")
    print(f"🌍 Location: Delhi ({lat}°N, {lon}°E)")
    
    # Calculate Julian Day for the test date
    unix_epoch_jd = 2440587.5
    seconds_since_epoch = test_date.timestamp()
    jd_test = unix_epoch_jd + (seconds_since_epoch / 86400.0)
    
    print(f"🔢 Calculated JD for test date: {jd_test}")
    
    # Test Skyfield sunrise calculation
    try:
        ts = load.timescale()
        eph = load('de421.bsp')
        earth = eph['earth']
        location = Topos(latitude_degrees=lat, longitude_degrees=lon)
        observer = earth + location
        
        # Search for sunrise/sunset around the test date
        t0 = ts.tdb_jd(jd_test - 0.5)
        t1 = ts.tdb_jd(jd_test + 0.5)
        t, y = find_discrete(t0, t1, sunrise_sunset(eph, observer))
        
        sunrise_times = t[y == 1]
        sunset_times = t[y == 0]
        
        if len(sunrise_times) > 0 and len(sunset_times) > 0:
            sunrise_jd = sunrise_times[0].tdb
            sunset_jd = sunset_times[0].tdb
            
            print(f"\n☀️ Skyfield Results:")
            print(f"   Sunrise JD: {sunrise_jd}")
            print(f"   Sunset JD:  {sunset_jd}")
            
            # Convert using different methods
            print(f"\n🔄 Conversion Tests:")
            
            # Method 1: Direct conversion from JD to UTC
            sunrise_utc = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=(sunrise_jd - unix_epoch_jd) * 86400)
            sunset_utc = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=(sunset_jd - unix_epoch_jd) * 86400)
            
            print(f"   Method 1 (UTC):")
            print(f"     Sunrise UTC: {sunrise_utc}")
            print(f"     Sunset UTC:  {sunset_utc}")
            
            # Method 2: Convert to IST (+5.5 hours)
            ist_tz = timezone(timedelta(hours=5.5))
            sunrise_ist = sunrise_utc.astimezone(ist_tz)
            sunset_ist = sunset_utc.astimezone(ist_tz)
            
            print(f"   Method 2 (IST +5.5):")
            print(f"     Sunrise IST: {sunrise_ist}")
            print(f"     Sunset IST:  {sunset_ist}")
            
            # Method 3: Skyfield's built-in conversion
            sunrise_skyfield = sunrise_times[0].utc_datetime()
            sunset_skyfield = sunset_times[0].utc_datetime()
            
            print(f"   Method 3 (Skyfield UTC):")
            print(f"     Sunrise Skyfield: {sunrise_skyfield}")
            print(f"     Sunset Skyfield:  {sunset_skyfield}")
            
            # Convert Skyfield UTC to IST
            sunrise_skyfield_ist = sunrise_skyfield.replace(tzinfo=timezone.utc).astimezone(ist_tz)
            sunset_skyfield_ist = sunset_skyfield.replace(tzinfo=timezone.utc).astimezone(ist_tz)
            
            print(f"   Method 3 → IST:")
            print(f"     Sunrise IST: {sunrise_skyfield_ist}")
            print(f"     Sunset IST:  {sunset_skyfield_ist}")
            
            # Expected times for Delhi on July 9, 2025
            print(f"\n✅ Expected for Delhi July 9, 2025:")
            print(f"   Sunrise: ~05:30 AM IST")
            print(f"   Sunset:  ~19:30 PM IST")
            
            # Analysis
            print(f"\n🔍 Analysis:")
            sunrise_hour = sunrise_skyfield_ist.hour
            sunset_hour = sunset_skyfield_ist.hour
            
            if 4 <= sunrise_hour <= 8:
                print(f"   ✅ Sunrise at {sunrise_hour}:00 looks correct")
            else:
                print(f"   ❌ Sunrise at {sunrise_hour}:00 seems wrong")
                
            if 17 <= sunset_hour <= 21:
                print(f"   ✅ Sunset at {sunset_hour}:00 looks correct")
            else:
                print(f"   ❌ Sunset at {sunset_hour}:00 seems wrong")
                
        else:
            print("❌ No sunrise/sunset found in the search period")
            
    except Exception as e:
        print(f"❌ Error in Skyfield calculation: {e}")

if __name__ == "__main__":
    test_julian_day_conversion() 