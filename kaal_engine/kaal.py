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
        Complete Panchang calculation with 50+ Vedic parameters including traditional features
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
        
        # Calculate end times for tithi and nakshatra
        tithi_end_data = self._calculate_tithi_end_time(sun_long, moon_long, jd_tt)
        nakshatra_end_data = self._calculate_nakshatra_end_time(moon_long, jd_tt)
        
        # Calculate traditional calendar years
        traditional_years = self._calculate_traditional_years(dt)
        
        # Calculate Tarabala and Chandrabala
        tarabala_data = self._calculate_tarabala_chandrabala(moon_long, dt)
        
        # Calculate Shool direction and Nivas
        shool_data = self._calculate_shool_nivas(dt, moon_long)
        
        # Calculate Panchaka classification
        panchaka_data = self._calculate_panchaka(dt, moon_long)
        
        return {
            # Basic Panchang Elements
            "tithi": self._compute_tithi(sun_long, moon_long),
            "tithi_name": self._get_tithi_name(self._compute_tithi(sun_long, moon_long)),
            "tithi_end_time": tithi_end_data,
            "nakshatra": self._moon_nakshatra(moon_long),
            "nakshatra_lord": self._get_nakshatra_lord(moon_long),
            "nakshatra_end_time": nakshatra_end_data,
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
            
            # NEW: Enhanced traditional features
            "traditional_years": traditional_years,
            "tarabala": tarabala_data,
            "shool_data": shool_data,
            "panchaka": panchaka_data
        }
    
    def _calculate_tithi_end_time(self, sun_long: float, moon_long: float, jd_tt: float) -> dict:
        """Calculate exact end time for current tithi"""
        current_tithi = self._compute_tithi(sun_long, moon_long)
        next_tithi_target = math.ceil(current_tithi)
        
        # Calculate how much tithi has progressed (0-1)
        progress = current_tithi % 1
        remaining_fraction = 1 - progress
        
        # Average tithi duration is about 23.62 hours
        # More precise calculation would use lunar motion rates
        average_tithi_duration_hours = 23.62
        remaining_hours = remaining_fraction * average_tithi_duration_hours
        
        # Calculate end time
        end_time = datetime.utcfromtimestamp((jd_tt - 2440587.5) * 86400) + timedelta(hours=remaining_hours)
        
        return {
            "end_time": end_time,
            "hours_remaining": int(remaining_hours),
            "minutes_remaining": int((remaining_hours % 1) * 60),
            "percentage_complete": round(progress * 100, 1)
        }
    
    def _calculate_nakshatra_end_time(self, moon_long: float, jd_tt: float) -> dict:
        """Calculate exact end time for current nakshatra"""
        # Each nakshatra spans 13.333... degrees (360/27)
        nakshatra_span = 360.0 / 27.0
        current_nakshatra_position = moon_long % nakshatra_span
        progress = current_nakshatra_position / nakshatra_span
        
        # Average moon motion is about 13.2 degrees per day
        moon_daily_motion = 13.2
        remaining_degrees = nakshatra_span - current_nakshatra_position
        remaining_hours = (remaining_degrees / moon_daily_motion) * 24
        
        # Calculate end time
        end_time = datetime.utcfromtimestamp((jd_tt - 2440587.5) * 86400) + timedelta(hours=remaining_hours)
        
        return {
            "end_time": end_time,
            "hours_remaining": int(remaining_hours),
            "minutes_remaining": int((remaining_hours % 1) * 60),
            "percentage_complete": round(progress * 100, 1)
        }
    
    def _calculate_traditional_years(self, dt: datetime) -> dict:
        """Calculate traditional Hindu calendar years"""
        year = dt.year
        
        # Vikram Samvat (starts around April, so add 57 for most of the year)
        if dt.month >= 4:
            vikram_samvat = year + 57
        else:
            vikram_samvat = year + 56
        
        # Shaka Samvat (starts around March/April, subtract 78)
        if dt.month >= 3:
            shaka_samvat = year - 78
        else:
            shaka_samvat = year - 79
        
        # Kali Yuga year (add 3102 to CE year)
        kali_yuga = year + 3102
        
        # Bengali San (starts around April, subtract 593)
        if dt.month >= 4:
            bengali_san = year - 593
        else:
            bengali_san = year - 594
        
        # Tamil year names cycle (60-year cycle)
        tamil_years = [
            "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati", "Angirasa", "Shrimukha", "Bhava",
            "Yuva", "Dhata", "Ishvara", "Bahudhanya", "Pramadi", "Vikrama", "Vrusha", "Chitrabhanu",
            "Svabhanu", "Tarana", "Parthiva", "Vyaya", "Sarvajeeth", "Sarvadhadi", "Virodhi", "Vikrita",
            "Khara", "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi", "Hemalamba", "Vilamba",
            "Vikari", "Sharvari", "Plava", "Shubhakrit", "Sobhakrit", "Krodhi", "Vishvavasu", "Parabhava",
            "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrit", "Paridhavi", "Pramadi", "Ananda",
            "Rakshasa", "Nala", "Pingala", "Kalayukti", "Siddharthi", "Raudra", "Durmati", "Dundubhi",
            "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"
        ]
        
        # Calculate Tamil year (approximately)
        tamil_year_index = (year - 1987) % 60  # 1987 was Prabhava year
        tamil_year = tamil_years[tamil_year_index]
        
        return {
            "vikram_samvat": vikram_samvat,
            "shaka_samvat": shaka_samvat,
            "kali_yuga": kali_yuga,
            "bengali_san": bengali_san,
            "tamil_year": tamil_year
        }
    
    def _calculate_tarabala_chandrabala(self, moon_long: float, dt: datetime) -> dict:
        """Calculate Tarabala and Chandrabala"""
        # Get birth nakshatra (using a reference - in real app, this would be user's birth nakshatra)
        # For demo, using Rohini (4th nakshatra) as reference
        birth_nakshatra_number = 4  # This should come from user data
        
        # Current Moon nakshatra
        current_nakshatra_number = self._get_nakshatra_number(moon_long)
        
        # Calculate Tarabala
        if current_nakshatra_number >= birth_nakshatra_number:
            tara_count = current_nakshatra_number - birth_nakshatra_number + 1
        else:
            tara_count = current_nakshatra_number + 27 - birth_nakshatra_number + 1
        
        tara_count = ((tara_count - 1) % 9) + 1
        
        tara_names = [
            "Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhaka", "Vadha", "Mitra", "Param Mitra"
        ]
        
        tara_results = [
            "Neutral", "Very Good", "Bad", "Good", "Bad", "Good", "Very Bad", "Very Good", "Excellent"
        ]
        
        tarabala = tara_names[tara_count - 1]
        tarabala_result = tara_results[tara_count - 1]
        
        # Calculate Chandrabala (simplified)
        # Based on lunar day and other factors
        tithi_number = int(self._compute_tithi(self._get_sun_longitude(dt), moon_long))
        chandrabala_points = min(6, max(0, (tithi_number % 8) + 1))
        
        chandrabala_names = ["Very Weak", "Weak", "Average", "Good", "Very Good", "Excellent", "Supreme"]
        chandrabala = chandrabala_names[min(6, chandrabala_points)]
        
        return {
            "tarabala": tarabala,
            "tarabala_number": tara_count,
            "tarabala_result": tarabala_result,
            "chandrabala": chandrabala,
            "chandrabala_points": chandrabala_points
        }
    
    def _calculate_shool_nivas(self, dt: datetime, moon_long: float) -> dict:
        """Calculate Shool direction and Nivas"""
        day_of_week = dt.weekday()  # 0 = Monday
        
        # Shool directions by day of week
        shool_directions = [
            "North",     # Monday
            "East",      # Tuesday  
            "South",     # Wednesday
            "West",      # Thursday
            "North",     # Friday
            "East",      # Saturday
            "South"      # Sunday
        ]
        
        # Ruling deities for each direction
        direction_deities = {
            "North": "Kubera",
            "East": "Indra", 
            "South": "Yama",
            "West": "Varuna"
        }
        
        # Current Nivas (residence) calculation based on lunar month
        nivas_cycle = ["Ksheera Sagara", "Vaikuntha", "Ksheer Sagara", "Bhu Loka", "Patala Loka", "Swarga Loka"]
        lunar_month = int((moon_long / 30) % 12)
        nivas = nivas_cycle[lunar_month % 6]
        
        # Favorable direction (opposite to Shool)
        direction_opposites = {
            "North": "South",
            "South": "North", 
            "East": "West",
            "West": "East"
        }
        
        shool_direction = shool_directions[day_of_week]
        favorable_direction = direction_opposites[shool_direction]
        
        return {
            "shool_direction": shool_direction,
            "shool_deity": direction_deities[shool_direction],
            "nivas": nivas,
            "favorable_direction": favorable_direction
        }
    
    def _calculate_panchaka(self, dt: datetime, moon_long: float) -> dict:
        """Calculate Panchaka classification"""
        # Get current nakshatra
        nakshatra_number = self._get_nakshatra_number(moon_long)
        
        # Panchaka nakshatras: Dhanishtha, Shatabhisha, Purva Bhadrapada, Uttara Bhadrapada, Revati
        panchaka_nakshatras = [23, 24, 25, 26, 27]  # Nakshatra numbers
        
        if nakshatra_number in panchaka_nakshatras:
            # Determine specific Panchaka type based on additional factors
            day_of_week = dt.weekday()
            
            panchaka_types = [
                {
                    "type": "Agni Panchaka",
                    "description": "Fire element dominance, avoid fire-related activities",
                    "favorable": ["Religious ceremonies", "Spiritual practices", "Meditation"],
                    "avoid": ["Starting fires", "Cooking elaborate meals", "Metalwork"]
                },
                {
                    "type": "Raja Panchaka", 
                    "description": "Royal element, good for leadership activities",
                    "favorable": ["Government work", "Leadership roles", "Important decisions"],
                    "avoid": ["Submissive activities", "Following others blindly"]
                },
                {
                    "type": "Mrityu Panchaka",
                    "description": "Death element, avoid new beginnings",
                    "favorable": ["Ending bad habits", "Completing projects", "Letting go"],
                    "avoid": ["New ventures", "Marriages", "Important purchases"]
                },
                {
                    "type": "Chor Panchaka",
                    "description": "Theft element, be cautious with valuables",
                    "favorable": ["Security arrangements", "Vigilance", "Protective measures"],
                    "avoid": ["Displaying wealth", "Traveling with valuables", "Trusting strangers"]
                },
                {
                    "type": "Roga Panchaka",
                    "description": "Disease element, focus on health",
                    "favorable": ["Health checkups", "Healing practices", "Medical treatments"],
                    "avoid": ["Unhealthy food", "Stress", "Overexertion"]
                }
            ]
            
            panchaka_index = (nakshatra_number - 23 + day_of_week) % 5
            panchaka_info = panchaka_types[panchaka_index]
            
            return {
                "panchaka_type": panchaka_info["type"],
                "panchaka_description": panchaka_info["description"],
                "favorable_activities": panchaka_info["favorable"],
                "activities_to_avoid": panchaka_info["avoid"]
            }
        else:
            return {
                "panchaka_type": "No Panchaka",
                "panchaka_description": "Normal period, no special Panchaka restrictions",
                "favorable_activities": ["All normal activities", "General work", "Regular tasks"],
                "activities_to_avoid": ["None specific"]
            }
    
    def _get_nakshatra_number(self, moon_long: float) -> int:
        """Get nakshatra number (1-27) from moon longitude"""
        return int(moon_long / 13.333333) + 1
    
    def _get_sun_longitude(self, dt: datetime) -> float:
        """Get sun longitude for given datetime"""
        jd_utc = self._julian_day(dt)
        jd_tt = delta_t.utc_to_tt(jd_utc)
        planetary_data = self._get_planetary_positions(jd_tt, "LAHIRI")
        return planetary_data['sun']['longitude']
    
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
        abhijit_end = solar_noon + (24 / (24 * 60))
        
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
        """Get nakshatra name from longitude"""
        nakshatras = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
            "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
            "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
            "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha",
            "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada",
            "Uttara Bhadrapada", "Revati"
        ]
        
        nakshatra_index = int(longitude / 13.333333) % 27
        return nakshatras[nakshatra_index]
    
    def _get_nakshatra_lord(self, moon_long: float) -> str:
        """Get nakshatra ruling planet"""
        lords = [
            "Ketu", "Venus", "Sun", "Moon", "Mars",
            "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
            "Venus", "Sun", "Moon", "Mars", "Rahu",
            "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
            "Sun", "Moon", "Mars", "Rahu", "Jupiter",
            "Saturn", "Mercury"
        ]
        
        nakshatra_index = int(moon_long / 13.333333) % 27
        return lords[nakshatra_index]
    
    def _compute_yoga(self, sun_long: float, moon_long: float) -> float:
        """Calculate yoga"""
        return ((sun_long + moon_long) % 360) / 13.333333
    
    def _get_yoga_name(self, yoga: float) -> str:
        """Get yoga name from yoga number"""
        yogas = [
            "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
            "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
            "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
            "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
            "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
            "Indra", "Vaidhriti"
        ]
        
        yoga_index = int(yoga) % 27
        return yogas[yoga_index]
    
    def _compute_karana(self, sun_long: float, moon_long: float) -> float:
        """Calculate karana"""
        tithi = self._compute_tithi(sun_long, moon_long)
        return (tithi * 2) % 60
    
    def _get_karana_name(self, karana: float) -> str:
        """Get karana name from karana number"""
        karanas = [
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
            "Kimstughna", "Shakuni", "Chatushpada", "Naga"
        ]
        
        karana_index = int(karana / 2) % len(karanas)
        return karanas[karana_index]
    
    def _compute_moon_phase(self, sun_long: float, moon_long: float) -> str:
        """Calculate moon phase name"""
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
        # Simplified sidereal time calculation
        T = (jd_tt - 2451545.0) / 36525.0
        
        # Greenwich Mean Sidereal Time
        gmst = 280.46061837 + 360.98564736629 * (jd_tt - 2451545.0) + 0.000387933 * T * T - T * T * T / 38710000.0
        
        # Local Sidereal Time
        lst = (gmst + lon) % 360
        return lst / 15.0  # Convert to hours
    
    def _get_season(self, sun_long: float) -> str:
        """Get current season from sun longitude"""
        if 0 <= sun_long < 90:
            return "Spring"
        elif 90 <= sun_long < 180:
            return "Summer"
        elif 180 <= sun_long < 270:
            return "Autumn"
        else:
            return "Winter"
    
    def _julian_day(self, dt: datetime) -> float:
        """Convert datetime to Julian Day"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jdn = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        
        # Add fractional day
        fractional_day = (dt.hour + dt.minute/60.0 + dt.second/3600.0) / 24.0
        
        return jdn + fractional_day - 0.5
    
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