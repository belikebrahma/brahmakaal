from datetime import datetime, timedelta
from .core import spice_loader, siddhanta, delta_t
from .core.ayanamsha import AyanamshaEngine
from .geo import micro_adjust
from astropy.time import Time
from skyfield.api import load
import math

class Kaal:
    def __init__(self, de441_path: str):
        self.eph = spice_loader.load_kernel(de441_path)
        self.earth = self.eph['earth']
        self.moon = self.eph['moon']
        self.sun = self.eph['sun']
        self.mars = self.eph['mars barycenter']
        self.mercury = self.eph['mercury barycenter']
        self.jupiter = self.eph['jupiter barycenter']
        self.venus = self.eph['venus barycenter']
        self.saturn = self.eph['saturn barycenter']
        
        # Load timescale for calculations
        self.ts = load.timescale()
        
        # Initialize ayanamsha engine
        self.ayanamsha_engine = AyanamshaEngine()
    
    def get_panchang(self, lat: float, lon: float, 
                    dt: datetime, elevation: float = 0.0, 
                    ayanamsha: str = "LAHIRI") -> dict:
        """
        Complete Panchang calculation with 50+ Vedic parameters
        """
        jd_utc = self._julian_day(dt)
        jd_tt = delta_t.utc_to_tt(jd_utc)
        
        # Get planetary positions
        planetary_data = self._get_planetary_positions(jd_tt, ayanamsha)
        sun_long = planetary_data['sun']['longitude']
        moon_long = planetary_data['moon']['longitude']
        
        # Calculate solar times
        solar_times = self._calculate_solar_times(jd_tt, lat, lon, elevation)
        
        # Calculate lunar times  
        lunar_times = self._calculate_lunar_times(jd_tt, lat, lon)
        
        # Calculate time periods
        time_periods = self._calculate_time_periods(solar_times, lat, lon, dt)
        
        return {
            # Basic Panchang Elements
            "tithi": self._compute_tithi(sun_long, moon_long),
            "tithi_name": self._get_tithi_name(self._compute_tithi(sun_long, moon_long)),
            "nakshatra": self._moon_nakshatra(moon_long),
            "nakshatra_lord": self._get_nakshatra_lord(moon_long),
            "yoga": self._compute_yoga(sun_long, moon_long),
            "yoga_name": self._get_yoga_name(self._compute_yoga(sun_long, moon_long)),
            "karana": self._compute_karana(sun_long, moon_long),
            "karana_name": self._get_karana_name(self._compute_karana(sun_long, moon_long)),
            
            # Solar Calculations
            "sunrise": solar_times['sunrise'],
            "sunset": solar_times['sunset'],
            "solar_noon": solar_times['solar_noon'],
            "day_length": solar_times['day_length'],
            
            # Lunar Calculations
            "moonrise": lunar_times['moonrise'],
            "moonset": lunar_times['moonset'],
            "moon_phase": self._compute_moon_phase(sun_long, moon_long),
            "moon_illumination": self._compute_moon_illumination(sun_long, moon_long),
            
            # Time Periods
            "rahu_kaal": time_periods['rahu_kaal'],
            "gulika_kaal": time_periods['gulika_kaal'],
            "yamaganda_kaal": time_periods['yamaganda_kaal'],
            "brahma_muhurta": time_periods['brahma_muhurta'],
            "abhijit_muhurta": time_periods['abhijit_muhurta'],
            
            # Planetary Positions (All 9 Grahas)
            "graha_positions": planetary_data,
            
            # Advanced Calculations
            "ayanamsha": self._compute_ayanamsha(jd_tt, ayanamsha),
            "local_mean_time": self._compute_local_mean_time(dt, lon),
            "sidereal_time": self._compute_sidereal_time(jd_tt, lon),
            
            # Additional Parameters
            "rashi_of_moon": self._get_rashi(moon_long),
            "rashi_of_sun": self._get_rashi(sun_long),
            "season": self._get_season(sun_long),
            "rtl_tithi_remaining": self._get_tithi_remaining_time(sun_long, moon_long, jd_tt)
        }
    
    def _get_planetary_positions(self, jd_tt: float, ayanamsha: str) -> dict:
        """Get positions of all 9 Grahas (Vedic planets)"""
        t = self.ts.tdb_jd(jd_tt)
        earth = self.eph['earth']
        
        positions = {}
        
        # Sun
        sun_pos = earth.at(t).observe(self.sun).apparent()
        sun_long = sun_pos.ecliptic_latlon()[0].degrees
        positions['sun'] = {
            'longitude': sun_long,
            'latitude': sun_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(sun_long),
            'nakshatra': self._get_nakshatra_from_longitude(sun_long)
        }
        
        # Moon
        moon_pos = earth.at(t).observe(self.moon).apparent()
        moon_long = moon_pos.ecliptic_latlon()[0].degrees
        positions['moon'] = {
            'longitude': moon_long,
            'latitude': moon_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(moon_long),
            'nakshatra': self._get_nakshatra_from_longitude(moon_long)
        }
        
        # Mars (Mangal)
        mars_pos = earth.at(t).observe(self.mars).apparent()
        mars_long = mars_pos.ecliptic_latlon()[0].degrees
        positions['mars'] = {
            'longitude': mars_long,
            'latitude': mars_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(mars_long),
            'nakshatra': self._get_nakshatra_from_longitude(mars_long)
        }
        
        # Mercury (Budh)
        mercury_pos = earth.at(t).observe(self.mercury).apparent()
        mercury_long = mercury_pos.ecliptic_latlon()[0].degrees
        positions['mercury'] = {
            'longitude': mercury_long,
            'latitude': mercury_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(mercury_long),
            'nakshatra': self._get_nakshatra_from_longitude(mercury_long)
        }
        
        # Jupiter (Guru)
        jupiter_pos = earth.at(t).observe(self.jupiter).apparent()
        jupiter_long = jupiter_pos.ecliptic_latlon()[0].degrees
        positions['jupiter'] = {
            'longitude': jupiter_long,
            'latitude': jupiter_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(jupiter_long),
            'nakshatra': self._get_nakshatra_from_longitude(jupiter_long)
        }
        
        # Venus (Shukra)
        venus_pos = earth.at(t).observe(self.venus).apparent()
        venus_long = venus_pos.ecliptic_latlon()[0].degrees
        positions['venus'] = {
            'longitude': venus_long,
            'latitude': venus_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(venus_long),
            'nakshatra': self._get_nakshatra_from_longitude(venus_long)
        }
        
        # Saturn (Shani)
        saturn_pos = earth.at(t).observe(self.saturn).apparent()
        saturn_long = saturn_pos.ecliptic_latlon()[0].degrees
        positions['saturn'] = {
            'longitude': saturn_long,
            'latitude': saturn_pos.ecliptic_latlon()[1].degrees,
            'rashi': self._get_rashi(saturn_long),
            'nakshatra': self._get_nakshatra_from_longitude(saturn_long)
        }
        
        # Rahu (North Node) - Mean node
        rahu_long = self._calculate_rahu_position(jd_tt)
        positions['rahu'] = {
            'longitude': rahu_long,
            'latitude': 0.0,  # Nodes are always on ecliptic
            'rashi': self._get_rashi(rahu_long),
            'nakshatra': self._get_nakshatra_from_longitude(rahu_long)
        }
        
        # Ketu (South Node) - Opposite of Rahu
        ketu_long = (rahu_long + 180) % 360
        positions['ketu'] = {
            'longitude': ketu_long,
            'latitude': 0.0,
            'rashi': self._get_rashi(ketu_long),
            'nakshatra': self._get_nakshatra_from_longitude(ketu_long)
        }
        
        return positions
    
    def _calculate_solar_times(self, jd_tt: float, lat: float, lon: float, elevation: float) -> dict:
        """Calculate sunrise, sunset, solar noon, and day length"""
        sunrise = micro_adjust.true_sunrise(jd_tt, lat, lon, elevation)
        sunset = micro_adjust.true_sunset(jd_tt, lat, lon, elevation)
        solar_noon = (sunrise + sunset) / 2
        day_length = (sunset - sunrise) * 24  # in hours
        
        return {
            'sunrise': sunrise,
            'sunset': sunset,
            'solar_noon': solar_noon,
            'day_length': day_length
        }
    
    def _calculate_lunar_times(self, jd_tt: float, lat: float, lon: float) -> dict:
        """Calculate moonrise and moonset times"""
        # This is a simplified calculation - in a full implementation,
        # we would use more sophisticated algorithms
        moonrise = micro_adjust.calculate_moonrise(jd_tt, lat, lon)
        moonset = micro_adjust.calculate_moonset(jd_tt, lat, lon)
        
        return {
            'moonrise': moonrise,
            'moonset': moonset
        }
    
    def _calculate_time_periods(self, solar_times: dict, lat: float, lon: float, dt: datetime) -> dict:
        """Calculate various time periods (Rahu Kaal, etc.)"""
        sunrise = solar_times['sunrise']
        sunset = solar_times['sunset']
        day_length = sunset - sunrise
        
        # Day of week (0 = Sunday, 1 = Monday, etc.)
        day_of_week = dt.weekday()
        if day_of_week == 6:  # Sunday
            day_of_week = 0
        else:
            day_of_week += 1
        
        # Rahu Kaal calculation (traditional formula)
        rahu_periods = [4.5, 7.5, 1.5, 6, 3, 5.5, 2.5]  # Hours from sunrise for each day
        rahu_start_hours = rahu_periods[day_of_week]
        
        rahu_start = sunrise + (rahu_start_hours / 24)
        rahu_end = rahu_start + (1.5 / 24)  # 1.5 hours duration
        
        # Gulika Kaal (similar calculation with different timing)
        gulika_periods = [6, 5, 4, 3, 2, 1, 7]
        gulika_start_hours = gulika_periods[day_of_week]
        gulika_start = sunrise + (gulika_start_hours / 24)
        gulika_end = gulika_start + (1.5 / 24)
        
        # Yamaganda Kaal
        yamaganda_periods = [2, 1, 7, 4.5, 6, 3, 5]
        yamaganda_start_hours = yamaganda_periods[day_of_week]
        yamaganda_start = sunrise + (yamaganda_start_hours / 24)
        yamaganda_end = yamaganda_start + (1.5 / 24)
        
        # Brahma Muhurta (96 minutes before sunrise)
        brahma_start = sunrise - (96 / (24 * 60))
        brahma_end = sunrise - (48 / (24 * 60))
        
        # Abhijit Muhurta (middle of the day)
        solar_noon = solar_times['solar_noon']
        abhijit_start = solar_noon - (24 / (24 * 60))  # 24 minutes before noon
        abhijit_end = solar_noon + (24 / (24 * 60))    # 24 minutes after noon
        
        return {
            'rahu_kaal': {'start': rahu_start, 'end': rahu_end},
            'gulika_kaal': {'start': gulika_start, 'end': gulika_end},
            'yamaganda_kaal': {'start': yamaganda_start, 'end': yamaganda_end},
            'brahma_muhurta': {'start': brahma_start, 'end': brahma_end},
            'abhijit_muhurta': {'start': abhijit_start, 'end': abhijit_end}
        }
    
    def _compute_tithi(self, sun_long: float, moon_long: float) -> float:
        """Calculate tithi (lunar day)"""
        return ((moon_long - sun_long) % 360) / 12.0
    
    def _get_tithi_name(self, tithi: float) -> str:
        """Get tithi name from tithi number"""
        tithi_names = [
            "Pratipad", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
        ]
        
        paksha = "Shukla" if tithi < 15 else "Krishna"
        tithi_index = int(tithi % 15)
        if tithi_index == 0:
            tithi_index = 15
        
        return f"{paksha} {tithi_names[tithi_index - 1]}"
    
    def _moon_nakshatra(self, moon_long: float) -> str:
        """Get nakshatra name from moon longitude"""
        return self._get_nakshatra_from_longitude(moon_long)
    
    def _get_nakshatra_from_longitude(self, longitude: float) -> str:
        """Get nakshatra from any longitude"""
        nakshatra_index = int(longitude // (13 + 20/60))
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
            "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
            "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra",
            "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
            "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
            "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ]
        return nakshatras[nakshatra_index % 27]
    
    def _get_nakshatra_lord(self, moon_long: float) -> str:
        """Get the ruling planet of moon's nakshatra"""
        nakshatra_index = int(moon_long // (13 + 20/60))
        lords = [
            "Ketu", "Venus", "Sun", "Moon", "Mars",
            "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
            "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
            "Sun", "Moon", "Mars", "Rahu", "Jupiter",
            "Saturn", "Mercury"
        ]
        return lords[nakshatra_index % 27]
    
    def _compute_yoga(self, sun_long: float, moon_long: float) -> float:
        """Calculate yoga (combination of sun and moon)"""
        return ((sun_long + moon_long) % 360) / 13.3333
    
    def _get_yoga_name(self, yoga: float) -> str:
        """Get yoga name from yoga number"""
        yoga_names = [
            "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
            "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
            "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
            "Siddhi", "Vyatipata", "Variyas", "Parigha", "Shiva",
            "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
            "Indra", "Vaidhriti"
        ]
        yoga_index = int(yoga) % 27
        return yoga_names[yoga_index]
    
    def _compute_karana(self, sun_long: float, moon_long: float) -> float:
        """Calculate karana (half tithi)"""
        tithi = self._compute_tithi(sun_long, moon_long)
        return (tithi * 2) % 60
    
    def _get_karana_name(self, karana: float) -> str:
        """Get karana name from karana number"""
        karana_names = [
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Shakuni", "Chatushpada", "Naga", "Kimstughna"
        ]
        karana_index = int(karana) % len(karana_names)
        return karana_names[karana_index]
    
    def _julian_day(self, dt: datetime) -> float:
        """Convert datetime to Julian Day"""
        t = Time(dt, scale='utc')
        return t.jd
    
    def _compute_moon_phase(self, sun_long: float, moon_long: float) -> str:
        """Calculate moon phase"""
        phase_angle = (moon_long - sun_long) % 360
        
        if phase_angle < 45:
            return "New Moon"
        elif phase_angle < 90:
            return "Waxing Crescent"
        elif phase_angle < 135:
            return "First Quarter"
        elif phase_angle < 180:
            return "Waxing Gibbous"
        elif phase_angle < 225:
            return "Full Moon"
        elif phase_angle < 270:
            return "Waning Gibbous"
        elif phase_angle < 315:
            return "Last Quarter"
        else:
            return "Waning Crescent"
    
    def _compute_moon_illumination(self, sun_long: float, moon_long: float) -> float:
        """Calculate moon illumination percentage"""
        phase_angle = abs((moon_long - sun_long) % 360)
        if phase_angle > 180:
            phase_angle = 360 - phase_angle
        
        # Simplified illumination calculation
        illumination = (1 + math.cos(math.radians(phase_angle))) / 2
        return round(illumination * 100, 1)
    
    def _calculate_rahu_position(self, jd_tt: float) -> float:
        """Calculate Rahu (Mean North Node) position"""
        # Mean lunar node calculation (simplified)
        # Full implementation would use proper orbital elements
        T = (jd_tt - 2451545.0) / 36525.0
        omega = 125.0445479 - 1934.1362891 * T + 0.0020754 * T * T
        return omega % 360
    
    def _get_rashi(self, longitude: float) -> str:
        """Get zodiac sign (rashi) from longitude"""
        rashi_index = int(longitude // 30)
        rashis = [
            "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
            "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena"
        ]
        return rashis[rashi_index % 12]
    
    def _compute_ayanamsha(self, jd_tt: float, ayanamsha_type: str) -> float:
        """Calculate ayanamsha correction using comprehensive engine"""
        return self.ayanamsha_engine.calculate_ayanamsha(jd_tt, ayanamsha_type)
    
    def _compute_local_mean_time(self, dt: datetime, lon: float) -> str:
        """Calculate Local Mean Time"""
        utc_offset = lon / 15.0  # 15 degrees per hour
        lmt = dt + timedelta(hours=utc_offset)
        return lmt.strftime("%H:%M:%S")
    
    def _compute_sidereal_time(self, jd_tt: float, lon: float) -> float:
        """Calculate Local Sidereal Time"""
        # Simplified calculation - full version would use GAST
        T = (jd_tt - 2451545.0) / 36525.0
        theta0 = 280.46061837 + 360.98564736629 * (jd_tt - 2451545.0)
        theta0 += 0.000387933 * T * T - T * T * T / 38710000.0
        
        # Convert to local sidereal time
        lst = (theta0 + lon) % 360
        return lst / 15.0  # Convert to hours
    
    def _get_season(self, sun_long: float) -> str:
        """Get season based on sun's position"""
        if 0 <= sun_long < 30:
            return "Spring"
        elif 30 <= sun_long < 60:
            return "Late Spring"
        elif 60 <= sun_long < 90:
            return "Summer"
        elif 90 <= sun_long < 120:
            return "Late Summer"
        elif 120 <= sun_long < 150:
            return "Monsoon"
        elif 150 <= sun_long < 180:
            return "Late Monsoon"
        elif 180 <= sun_long < 210:
            return "Autumn"
        elif 210 <= sun_long < 240:
            return "Late Autumn"
        elif 240 <= sun_long < 270:
            return "Winter"
        elif 270 <= sun_long < 300:
            return "Late Winter"
        elif 300 <= sun_long < 330:
            return "Pre-Spring"
        else:
            return "Late Winter"
    
    def _get_tithi_remaining_time(self, sun_long: float, moon_long: float, jd_tt: float) -> dict:
        """Calculate remaining time for current tithi"""
        current_tithi = self._compute_tithi(sun_long, moon_long)
        next_tithi = math.ceil(current_tithi)
        
        # Simplified calculation - in practice this would require
        # calculating the exact moment of tithi transition
        progress = current_tithi % 1
        remaining_fraction = 1 - progress
        
        # Assume average tithi duration of about 0.984 days
        remaining_hours = remaining_fraction * 23.6
        
        return {
            'hours': int(remaining_hours),
            'minutes': int((remaining_hours % 1) * 60),
            'percentage_complete': round(progress * 100, 1)
        }
    
    def get_ayanamsha_comparison(self, jd_tt: float) -> dict:
        """Compare all supported ayanamsha systems for given date"""
        return self.ayanamsha_engine.compare_systems(jd_tt)
    
    def tropical_to_sidereal(self, tropical_long: float, jd_tt: float, ayanamsha: str = "LAHIRI") -> float:
        """Convert tropical longitude to sidereal longitude"""
        return self.ayanamsha_engine.tropical_to_sidereal(tropical_long, jd_tt, ayanamsha)
    
    def sidereal_to_tropical(self, sidereal_long: float, jd_tt: float, ayanamsha: str = "LAHIRI") -> float:
        """Convert sidereal longitude to tropical longitude"""
        return self.ayanamsha_engine.sidereal_to_tropical(sidereal_long, jd_tt, ayanamsha)
    
    def get_supported_ayanamshas(self) -> dict:
        """Get list of all supported ayanamsha systems"""
        return self.ayanamsha_engine.SUPPORTED_SYSTEMS
    
    def calculate_planetary_aspects(self, planetary_data: dict) -> dict:
        """Calculate planetary aspects between all planets"""
        aspects = {}
        planets = list(planetary_data.keys())
        
        # Define aspect orbs (in degrees)
        aspect_orbs = {
            'conjunction': 8,
            'opposition': 8,
            'trine': 6,
            'square': 6,
            'sextile': 4
        }
        
        for i, planet1 in enumerate(planets):
            for planet2 in planets[i+1:]:
                if planet1 == planet2:
                    continue
                
                long1 = planetary_data[planet1]['longitude']
                long2 = planetary_data[planet2]['longitude']
                
                # Calculate angular separation
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects
                aspect_found = None
                if diff <= aspect_orbs['conjunction']:
                    aspect_found = 'conjunction'
                elif abs(diff - 180) <= aspect_orbs['opposition']:
                    aspect_found = 'opposition'
                elif abs(diff - 120) <= aspect_orbs['trine']:
                    aspect_found = 'trine'
                elif abs(diff - 90) <= aspect_orbs['square']:
                    aspect_found = 'square'
                elif abs(diff - 60) <= aspect_orbs['sextile']:
                    aspect_found = 'sextile'
                
                if aspect_found:
                    aspect_key = f"{planet1}-{planet2}"
                    aspects[aspect_key] = {
                        'aspect': aspect_found,
                        'orb': round(diff, 2),
                        'planets': [planet1, planet2]
                    }
        
        return aspects
    
    def calculate_house_positions(self, jd_tt: float, lat: float, lon: float, house_system: str = "PLACIDUS") -> dict:
        """Calculate house cusps for birth chart"""
        # This is a simplified house calculation
        # Full implementation would use proper algorithms for different house systems
        
        # Calculate Local Sidereal Time
        lst = self._compute_sidereal_time(jd_tt, lon)
        
        # Calculate Ascendant (simplified)
        # In reality, this requires complex spherical trigonometry
        ascendant = (lst * 15 + lon) % 360
        
        houses = {}
        for house_num in range(1, 13):
            if house_system == "EQUAL":
                # Equal house system - 30 degrees per house
                house_cusp = (ascendant + (house_num - 1) * 30) % 360
            else:
                # Simplified Placidus approximation
                house_cusp = (ascendant + (house_num - 1) * 30) % 360
                # In real implementation, would apply Placidus calculations
            
            houses[f"house_{house_num}"] = {
                'cusp_longitude': house_cusp,
                'rashi': self._get_rashi(house_cusp),
                'lord': self._get_house_lord(house_cusp)
            }
        
        return houses
    
    def _get_house_lord(self, longitude: float) -> str:
        """Get the ruling planet of a rashi"""
        rashi_index = int(longitude // 30)
        lords = [
            "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
            "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
        ]
        return lords[rashi_index % 12]
    
    def detect_yogas(self, planetary_data: dict, house_data: dict = None) -> list:
        """Detect common yogas in the chart"""
        yogas = []
        
        # Simple yoga detection examples
        # Raja Yoga - Jupiter and Venus conjunction/aspect
        jupiter_long = planetary_data.get('jupiter', {}).get('longitude', 0)
        venus_long = planetary_data.get('venus', {}).get('longitude', 0)
        
        diff = abs(jupiter_long - venus_long)
        if diff > 180:
            diff = 360 - diff
        
        if diff <= 10:  # Conjunction within 10 degrees
            yogas.append({
                'name': 'Guru-Shukra Yoga',
                'description': 'Jupiter-Venus conjunction brings wealth and knowledge',
                'strength': 'Strong' if diff <= 5 else 'Moderate'
            })
        
        # Gaja Kesari Yoga - Moon and Jupiter in Kendra
        moon_long = planetary_data.get('moon', {}).get('longitude', 0)
        moon_jupiter_diff = abs(moon_long - jupiter_long)
        if moon_jupiter_diff > 180:
            moon_jupiter_diff = 360 - moon_jupiter_diff
        
        if moon_jupiter_diff <= 10:
            yogas.append({
                'name': 'Gaja Kesari Yoga',
                'description': 'Moon-Jupiter combination brings fame and prosperity',
                'strength': 'Strong'
            })
        
        # More yogas would be added in full implementation
        
        return yogas
    
    def calculate_dasha_periods(self, moon_nakshatra: str, birth_jd: float) -> dict:
        """Calculate Vimshottari Dasha periods (simplified)"""
        # Dasha order and periods (in years)
        dasha_order = [
            ('Ketu', 7), ('Venus', 20), ('Sun', 6), ('Moon', 10),
            ('Mars', 7), ('Rahu', 18), ('Jupiter', 16), ('Saturn', 19), ('Mercury', 17)
        ]
        
        # Starting dasha based on nakshatra (simplified mapping)
        nakshatra_to_dasha = {
            'Ashwini': 0, 'Bharani': 1, 'Krittika': 2, 'Rohini': 3, 'Mrigashira': 4,
            'Ardra': 5, 'Punarvasu': 6, 'Pushya': 7, 'Ashlesha': 8, 'Magha': 0,
            'Purva Phalguni': 1, 'Uttara Phalguni': 2, 'Hasta': 3, 'Chitra': 4,
            'Swati': 5, 'Vishakha': 6, 'Anuradha': 7, 'Jyeshtha': 8, 'Mula': 0,
            'Purva Ashadha': 1, 'Uttara Ashadha': 2, 'Shravana': 3, 'Dhanishta': 4,
            'Shatabhisha': 5, 'Purva Bhadrapada': 6, 'Uttara Bhadrapada': 7, 'Revati': 8
        }
        
        start_index = nakshatra_to_dasha.get(moon_nakshatra, 0)
        
        dashas = []
        current_jd = birth_jd
        
        for i in range(9):
            dasha_index = (start_index + i) % 9
            planet, years = dasha_order[dasha_index]
            
            dashas.append({
                'planet': planet,
                'start_date': self._jd_to_date(current_jd),
                'end_date': self._jd_to_date(current_jd + years * 365.25),
                'duration_years': years
            })
            
            current_jd += years * 365.25
        
        return {'maha_dashas': dashas}
    
    def _jd_to_date(self, jd: float) -> str:
        """Convert Julian Day to date string"""
        from astropy.time import Time
        t = Time(jd, format='jd')
        return t.datetime.strftime("%Y-%m-%d")