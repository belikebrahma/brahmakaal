from skyfield.almanac import find_discrete, sunrise_sunset
from skyfield.api import load, Topos
import math

ATM_REFRACTION = 34 / 60  # 34 arcminutes

def true_sunrise(jd: float, lat: float, lon: float, elev: float) -> float:
    """Calculate precise sunrise time with elevation corrections (Skyfield already includes refraction)"""
    base_jd = _apparent_sunrise(jd, lat, lon)
    return base_jd - _elevation_adjustment_magnitude(elev)  # Sunrise earlier at elevation

def true_sunset(jd: float, lat: float, lon: float, elev: float) -> float:
    """Calculate precise sunset time with elevation corrections (Skyfield already includes refraction)"""
    base_jd = _apparent_sunset(jd, lat, lon)
    return base_jd + _elevation_adjustment_magnitude(elev)  # Sunset later at elevation

def calculate_moonrise(jd: float, lat: float, lon: float) -> float:
    """Calculate moonrise time for given date and location"""
    try:
        ts = load.timescale()
        eph = load('de421.bsp')
        moon = eph['moon']
        observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
        
        # Search for moonrise in extended window (moon might not rise every day)
        t0 = ts.tdb_jd(jd - 1.0)  # Search 1 day before
        t1 = ts.tdb_jd(jd + 1.0)  # Search 1 day after
        
        # Look for actual rise: transition from below horizon to above horizon
        prev_alt = None
        rise_times = []
        
        # Check every 10 minutes for better precision
        for minute in range(int(48 * 6)):  # 48 hours * 6 (10-minute intervals)
            test_time = t0 + minute * (10.0 / (24 * 60)) 
            # Correct Skyfield API usage: earth observation from observer position
            earth = eph['earth']
            moon_alt = (earth + observer).at(test_time).observe(moon).apparent().altaz()[0].degrees
            
            # Detect rise: previous alt < 0 and current alt >= 0
            if prev_alt is not None and prev_alt < 0 and moon_alt >= 0:
                # Find the closest time to the target date
                time_diff = abs(test_time.tdb - jd)
                rise_times.append((test_time.tdb, time_diff))
            
            prev_alt = moon_alt
        
        # Return the moonrise closest to target date
        if rise_times:
            rise_times.sort(key=lambda x: x[1])  # Sort by time difference
            return rise_times[0][0]
        
        return None  # No moonrise found
    except Exception as e:
        print(f"⚠️ Moonrise calculation failed: {e}")
        return None

def calculate_moonset(jd: float, lat: float, lon: float) -> float:
    """Calculate moonset time for given date and location"""
    try:
        ts = load.timescale()
        eph = load('de421.bsp')
        moon = eph['moon']
        observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
        
        # Search for moonset in extended window
        t0 = ts.tdb_jd(jd - 1.0)  # Search 1 day before
        t1 = ts.tdb_jd(jd + 1.0)  # Search 1 day after
        
        # Look for actual set: transition from above horizon to below horizon
        prev_alt = None
        set_times = []
        
        # Check every 10 minutes for better precision
        for minute in range(int(48 * 6)):  # 48 hours * 6 (10-minute intervals)
            test_time = t0 + minute * (10.0 / (24 * 60))
            # Correct Skyfield API usage: earth observation from observer position
            earth = eph['earth']
            moon_alt = (earth + observer).at(test_time).observe(moon).apparent().altaz()[0].degrees
            
            # Detect set: previous alt > 0 and current alt <= 0
            if prev_alt is not None and prev_alt > 0 and moon_alt <= 0:
                # Find the closest time to the target date
                time_diff = abs(test_time.tdb - jd)
                set_times.append((test_time.tdb, time_diff))
            
            prev_alt = moon_alt
        
        # Return the moonset closest to target date
        if set_times:
            set_times.sort(key=lambda x: x[1])  # Sort by time difference
            return set_times[0][0]
        
        return None  # No moonset found
    except Exception as e:
        print(f"⚠️ Moonset calculation failed: {e}")
        return None

def _apparent_sunrise(jd: float, lat: float, lon: float) -> float:
    """Calculate apparent sunrise without corrections"""
    try:
        ts = load.timescale()
        eph = load('de421.bsp')
        # Use direct Topos creation - modern Skyfield approach
        observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
        
        # Calculate actual sunrise
        t0 = ts.tdb_jd(jd - 0.5)
        t1 = ts.tdb_jd(jd + 0.5)
        t, y = find_discrete(t0, t1, sunrise_sunset(eph, observer))
        sunrise_times = t[y == 1]
        print(f"🌅 Skyfield sunrise calculation succeeded")
        return sunrise_times[0].tdb if len(sunrise_times) > 0 else jd
    except Exception as e:
        # Fallback calculation using simplified formula
        print(f"⚠️ Skyfield sunrise failed, using fallback: {e}")
        return _calculate_solar_time(jd, lat, lon, True)

def _apparent_sunset(jd: float, lat: float, lon: float) -> float:
    """Calculate apparent sunset without corrections"""
    try:
        ts = load.timescale()
        eph = load('de421.bsp')
        # Use direct Topos creation - modern Skyfield approach
        observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
        
        # Calculate actual sunset
        t0 = ts.tdb_jd(jd - 0.5)
        t1 = ts.tdb_jd(jd + 0.5)
        t, y = find_discrete(t0, t1, sunrise_sunset(eph, observer))
        sunset_times = t[y == 0]
        print(f"🌇 Skyfield sunset calculation succeeded")
        return sunset_times[-1].tdb if len(sunset_times) > 0 else jd + 0.5
    except Exception as e:
        # Fallback calculation
        print(f"⚠️ Skyfield sunset failed, using fallback: {e}")
        return _calculate_solar_time(jd, lat, lon, False)

def _calculate_solar_time(jd: float, lat: float, lon: float, is_sunrise: bool) -> float:
    """Simplified solar time calculation for fallback"""
    # This is a simplified calculation based on solar position
    # In a full implementation, this would use more precise algorithms
    
    # Calculate solar noon
    solar_noon = jd + 0.5 - lon / 360.0
    
    # Approximate equation of time (simplified)
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    
    # Solar declination
    declination = math.asin(math.sin(math.radians(23.45)) * math.sin(lambda_sun))
    
    # Hour angle for sunrise/sunset
    lat_rad = math.radians(lat)
    cos_hour_angle = -math.tan(lat_rad) * math.tan(declination)
    
    # Check for polar day/night
    if cos_hour_angle > 1:  # Polar night
        return jd if is_sunrise else jd + 1
    elif cos_hour_angle < -1:  # Polar day
        return jd - 1 if is_sunrise else jd + 1
    
    hour_angle = math.acos(cos_hour_angle)
    hour_angle_hours = math.degrees(hour_angle) / 15.0
    
    if is_sunrise:
        return solar_noon - hour_angle_hours / 24.0
    else:
        return solar_noon + hour_angle_hours / 24.0

def _elevation_adjustment_magnitude(elev: float) -> float:
    """Calculate magnitude of time adjustment for observer elevation"""
    if elev <= 0:
        return 0.0
    # Dip of horizon formula: dip = 1.76 * sqrt(height_in_meters) in arcminutes
    dip_arcminutes = 1.76 * math.sqrt(elev)
    # Convert to time: 1 degree = 4 minutes of time, so 1 arcminute = 4/60 minutes of time
    adjustment_minutes = dip_arcminutes * (4.0 / 60.0)
    # Return positive magnitude (direction handled in sunrise/sunset functions)
    return adjustment_minutes / (24 * 60)  # Convert to days

def _refraction_adjustment() -> float:
    """Standard atmospheric refraction adjustment"""
    # Standard refraction is about 34 arcminutes at horizon
    # This corresponds to about 2.3 minutes of time
    return 2.3 / (24 * 60)  # Convert to days

def geometric_sunrise(jd: float, lat: float, lon: float) -> float:
    """Calculate geometric sunrise (center of sun at horizon)"""
    return _calculate_solar_time(jd, lat, lon, True)

def geometric_sunset(jd: float, lat: float, lon: float) -> float:
    """Calculate geometric sunset (center of sun at horizon)"""
    return _calculate_solar_time(jd, lat, lon, False)

def civil_twilight_begin(jd: float, lat: float, lon: float) -> float:
    """Calculate civil twilight beginning (sun 6° below horizon)"""
    return _calculate_twilight_time(jd, lat, lon, -6, True)

def civil_twilight_end(jd: float, lat: float, lon: float) -> float:
    """Calculate civil twilight end (sun 6° below horizon)"""
    return _calculate_twilight_time(jd, lat, lon, -6, False)

def _calculate_twilight_time(jd: float, lat: float, lon: float, angle: float, is_morning: bool) -> float:
    """Calculate twilight times for given solar angle"""
    # Solar noon
    solar_noon = jd + 0.5 - lon / 360.0
    
    # Calculate solar declination (simplified)
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    declination = math.asin(math.sin(math.radians(23.45)) * math.sin(lambda_sun))
    
    # Hour angle calculation for given altitude
    lat_rad = math.radians(lat)
    angle_rad = math.radians(angle)
    
    cos_hour_angle = (math.sin(angle_rad) - math.sin(lat_rad) * math.sin(declination)) / \
                     (math.cos(lat_rad) * math.cos(declination))
    
    if cos_hour_angle > 1 or cos_hour_angle < -1:
        return jd  # No twilight at this location/date
    
    hour_angle = math.acos(cos_hour_angle)
    hour_angle_hours = math.degrees(hour_angle) / 15.0
    
    if is_morning:
        return solar_noon - hour_angle_hours / 24.0
    else:
        return solar_noon + hour_angle_hours / 24.0
