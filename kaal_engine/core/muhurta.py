"""
Comprehensive Muhurta Engine for Brahmakaal
Electional Astrology System for Determining Auspicious Timings

This module implements traditional Vedic muhurta (auspicious timing) calculations
for various life events including marriage, business, travel, education, and property.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math

class MuhurtaType(Enum):
    """Types of muhurta calculations supported"""
    MARRIAGE = "marriage"
    BUSINESS = "business"
    TRAVEL = "travel"
    EDUCATION = "education"
    PROPERTY = "property"
    GENERAL = "general"
    CUSTOM = "custom"

class MuhurtaQuality(Enum):
    """Quality levels for muhurta timing"""
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    AVOID = "avoid"

@dataclass
class MuhurtaResult:
    """Result of muhurta analysis"""
    datetime: datetime
    quality: MuhurtaQuality
    score: float  # 0-100 score
    factors: Dict[str, Any]
    recommendations: List[str]
    warnings: List[str]
    duration_minutes: int
    description: str

@dataclass
class MuhurtaRequest:
    """Request for muhurta calculation"""
    muhurta_type: MuhurtaType
    start_date: datetime
    end_date: datetime
    latitude: float
    longitude: float
    duration_minutes: int = 60
    custom_rules: Optional[Dict[str, Any]] = None
    exclude_periods: Optional[List[Tuple[datetime, datetime]]] = None

class MuhurtaEngine:
    """
    Comprehensive Muhurta (Electional Astrology) Engine
    
    Implements traditional Vedic rules for determining auspicious timings
    for various life events and activities.
    """
    
    def __init__(self, kaal_engine):
        """
        Initialize muhurta engine with core astronomical engine
        
        Args:
            kaal_engine: Instance of Kaal class for astronomical calculations
        """
        self.kaal = kaal_engine
        self.cache = {}
        
        # Traditional muhurta factors and their weights
        self.muhurta_factors = {
            'tithi': 0.15,        # Lunar day
            'nakshatra': 0.15,    # Lunar mansion
            'yoga': 0.10,         # Sun-Moon combination
            'karana': 0.10,       # Half-tithi
            'vara': 0.10,         # Day of week
            'rahu_kaal': 0.15,    # Inauspicious periods
            'moon_phase': 0.10,   # Lunar phase quality
            'planetary_strength': 0.15  # Planetary positions
        }
        
        # Initialize muhurta rules for different types
        self._init_muhurta_rules()
    
    def _init_muhurta_rules(self):
        """Initialize traditional muhurta rules for different event types"""
        
        # Marriage Muhurta Rules
        self.marriage_rules = {
            'favorable_tithis': [2, 3, 5, 7, 10, 11, 12, 13],  # Dwitiya to Trayodashi (excluding 4,6,8,9)
            'avoid_tithis': [1, 4, 6, 8, 9, 14, 15, 30],       # Pratipad, Chaturthi, Shashthi, Ashtami, Navami, Chaturdashi, Amavasya, Purnima
            'favorable_nakshatras': ['Rohini', 'Mrigashira', 'Magha', 'Uttara_Phalguni', 'Hasta', 'Swati', 'Anuradha', 'Uttara_Ashadha', 'Uttara_Bhadrapada'],
            'avoid_nakshatras': ['Bharani', 'Ashlesha', 'Jyeshtha', 'Moola'],
            'favorable_varas': ['Sunday', 'Monday', 'Wednesday', 'Thursday', 'Friday'],
            'avoid_varas': ['Tuesday', 'Saturday'],
            'favorable_months': [1, 2, 3, 4, 5, 10, 11, 12],   # Avoid monsoon months
            'special_considerations': {
                'guru_chandal': -20,      # Jupiter-Rahu conjunction penalty
                'mangal_dosha': -15,      # Mars in certain houses
                'ganda_moola': -25,       # Ganda Moola nakshatras
                'bhadra_periods': -30     # Bhadra times (inauspicious)
            }
        }
        
        # Business Muhurta Rules
        self.business_rules = {
            'favorable_tithis': [2, 3, 5, 7, 10, 11, 13],
            'avoid_tithis': [1, 4, 6, 8, 9, 14, 15, 30],
            'favorable_nakshatras': ['Ashwini', 'Rohini', 'Pushya', 'Magha', 'Uttara_Phalguni', 'Hasta', 'Chitra', 'Swati', 'Anuradha', 'Uttara_Ashadha', 'Shravana', 'Dhanishtha', 'Shatabhisha'],
            'avoid_nakshatras': ['Bharani', 'Ashlesha', 'Jyeshtha', 'Moola'],
            'favorable_varas': ['Sunday', 'Monday', 'Wednesday', 'Thursday'],
            'avoid_varas': ['Tuesday', 'Saturday'],
            'special_considerations': {
                'mercury_strength': 10,   # Strong Mercury for business
                'jupiter_position': 15,   # Jupiter in good houses
                'venus_aspects': 10,      # Venus aspects for prosperity
                'lunar_strength': 10      # Strong Moon for public acceptance
            }
        }
        
        # Travel Muhurta Rules
        self.travel_rules = {
            'favorable_tithis': [2, 3, 5, 6, 7, 10, 11, 12, 13],
            'avoid_tithis': [1, 4, 8, 9, 14, 15, 30],
            'favorable_nakshatras': ['Ashwini', 'Rohini', 'Mrigashira', 'Punarvasu', 'Pushya', 'Hasta', 'Chitra', 'Swati', 'Anuradha', 'Shravana', 'Dhanishtha', 'Shatabhisha'],
            'avoid_nakshatras': ['Bharani', 'Ashlesha', 'Jyeshtha', 'Moola'],
            'favorable_varas': ['Monday', 'Wednesday', 'Thursday', 'Friday'],
            'avoid_varas': ['Tuesday', 'Saturday'],
            'direction_considerations': {
                'east': ['Sunday', 'Monday'],      # Favorable days for eastward travel
                'south': ['Tuesday', 'Wednesday'], # Favorable days for southward travel
                'west': ['Thursday', 'Friday'],    # Favorable days for westward travel
                'north': ['Saturday', 'Sunday']    # Favorable days for northward travel
            }
        }
        
        # Education Muhurta Rules (Vidyarambha)
        self.education_rules = {
            'favorable_tithis': [2, 3, 5, 7, 10, 11, 12, 13],
            'avoid_tithis': [1, 4, 6, 8, 9, 14, 15, 30],
            'favorable_nakshatras': ['Ashwini', 'Rohini', 'Punarvasu', 'Pushya', 'Hasta', 'Chitra', 'Swati', 'Anuradha', 'Uttara_Ashadha', 'Shravana', 'Dhanishtha', 'Revati'],
            'avoid_nakshatras': ['Bharani', 'Ashlesha', 'Jyeshtha', 'Moola'],
            'favorable_varas': ['Monday', 'Wednesday', 'Thursday', 'Friday'],
            'avoid_varas': ['Tuesday', 'Saturday'],
            'special_considerations': {
                'mercury_strength': 20,   # Mercury is key for education
                'jupiter_aspects': 15,    # Jupiter aspects for wisdom
                'saraswati_yoga': 25,     # Special yoga for learning
                'fifth_house': 15         # Fifth house strength
            }
        }
        
        # Property Muhurta Rules (Griha Pravesh)
        self.property_rules = {
            'favorable_tithis': [2, 3, 5, 7, 10, 11, 12, 13],
            'avoid_tithis': [1, 4, 6, 8, 9, 14, 15, 30],
            'favorable_nakshatras': ['Rohini', 'Mrigashira', 'Pushya', 'Magha', 'Uttara_Phalguni', 'Hasta', 'Chitra', 'Swati', 'Anuradha', 'Uttara_Ashadha', 'Shravana', 'Uttara_Bhadrapada'],
            'avoid_nakshatras': ['Bharani', 'Ashlesha', 'Jyeshtha', 'Moola'],
            'favorable_varas': ['Sunday', 'Monday', 'Wednesday', 'Thursday', 'Friday'],
            'avoid_varas': ['Tuesday', 'Saturday'],
            'special_considerations': {
                'mars_position': 15,      # Mars for property strength
                'venus_aspects': 10,      # Venus for comfort
                'moon_strength': 10,      # Moon for peace
                'fourth_house': 20        # Fourth house (home) strength
            }
        }
    
    def find_muhurta(self, request: MuhurtaRequest) -> List[MuhurtaResult]:
        """
        Find auspicious muhurta timings for the given request
        
        Args:
            request: MuhurtaRequest with timing requirements
            
        Returns:
            List of MuhurtaResult objects sorted by quality/score
        """
        results = []
        current_time = request.start_date
        
        # Scan through the time range in hourly intervals
        while current_time <= request.end_date:
            # Skip if this time falls in excluded periods
            if self._is_excluded_period(current_time, request.exclude_periods):
                current_time += timedelta(hours=1)
                continue
            
            # Calculate muhurta for this time
            muhurta_result = self._calculate_muhurta(
                current_time, 
                request.muhurta_type,
                request.latitude,
                request.longitude,
                request.duration_minutes,
                request.custom_rules
            )
            
            # Only include results that are at least "average" quality
            if muhurta_result.quality not in [MuhurtaQuality.POOR, MuhurtaQuality.AVOID]:
                results.append(muhurta_result)
            
            current_time += timedelta(hours=1)
        
        # Sort results by score (highest first)
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Return top 20 results
        return results[:20]
    
    def _calculate_muhurta(self, dt: datetime, muhurta_type: MuhurtaType, 
                          lat: float, lon: float, duration_minutes: int,
                          custom_rules: Optional[Dict] = None) -> MuhurtaResult:
        """
        Calculate muhurta quality for a specific date/time
        
        Args:
            dt: DateTime to analyze
            muhurta_type: Type of muhurta calculation
            lat: Latitude
            lon: Longitude
            duration_minutes: Duration of the event
            custom_rules: Custom rules to apply
            
        Returns:
            MuhurtaResult with quality assessment
        """
        # Get comprehensive panchang for this time
        panchang = self.kaal.get_panchang(lat, lon, dt)
        
        # Initialize scoring
        total_score = 0.0
        factors = {}
        recommendations = []
        warnings = []
        
        # Get rules for this muhurta type
        rules = self._get_rules_for_type(muhurta_type)
        
        # Factor 1: Tithi Analysis
        tithi_score, tithi_factors = self._analyze_tithi(panchang, rules)
        total_score += tithi_score * self.muhurta_factors['tithi']
        factors['tithi'] = tithi_factors
        
        # Factor 2: Nakshatra Analysis
        nakshatra_score, nakshatra_factors = self._analyze_nakshatra(panchang, rules)
        total_score += nakshatra_score * self.muhurta_factors['nakshatra']
        factors['nakshatra'] = nakshatra_factors
        
        # Factor 3: Yoga Analysis
        yoga_score, yoga_factors = self._analyze_yoga(panchang, rules)
        total_score += yoga_score * self.muhurta_factors['yoga']
        factors['yoga'] = yoga_factors
        
        # Factor 4: Karana Analysis
        karana_score, karana_factors = self._analyze_karana(panchang, rules)
        total_score += karana_score * self.muhurta_factors['karana']
        factors['karana'] = karana_factors
        
        # Factor 5: Vara (Day of Week) Analysis
        vara_score, vara_factors = self._analyze_vara(panchang, rules)
        total_score += vara_score * self.muhurta_factors['vara']
        factors['vara'] = vara_factors
        
        # Factor 6: Rahu Kaal and Inauspicious Periods
        kaal_score, kaal_factors = self._analyze_inauspicious_periods(panchang, dt)
        total_score += kaal_score * self.muhurta_factors['rahu_kaal']
        factors['inauspicious_periods'] = kaal_factors
        
        # Factor 7: Moon Phase Analysis
        moon_score, moon_factors = self._analyze_moon_phase(panchang, muhurta_type)
        total_score += moon_score * self.muhurta_factors['moon_phase']
        factors['moon_phase'] = moon_factors
        
        # Factor 8: Planetary Strength Analysis
        planetary_score, planetary_factors = self._analyze_planetary_strength(panchang, rules)
        total_score += planetary_score * self.muhurta_factors['planetary_strength']
        factors['planetary_strength'] = planetary_factors
        
        # Apply custom rules if provided
        if custom_rules:
            custom_score, custom_factors = self._apply_custom_rules(panchang, custom_rules)
            total_score += custom_score * 0.1  # 10% weight for custom rules
            factors['custom'] = custom_factors
        
        # Determine quality based on total score
        quality = self._determine_quality(total_score)
        
        # Generate recommendations and warnings
        recommendations, warnings = self._generate_recommendations_warnings(
            factors, quality, muhurta_type
        )
        
        # Create description
        description = self._generate_description(dt, quality, muhurta_type, factors)
        
        return MuhurtaResult(
            datetime=dt,
            quality=quality,
            score=total_score,
            factors=factors,
            recommendations=recommendations,
            warnings=warnings,
            duration_minutes=duration_minutes,
            description=description
        )
    
    def _get_rules_for_type(self, muhurta_type: MuhurtaType) -> Dict:
        """Get rules for specific muhurta type"""
        rules_map = {
            MuhurtaType.MARRIAGE: self.marriage_rules,
            MuhurtaType.BUSINESS: self.business_rules,
            MuhurtaType.TRAVEL: self.travel_rules,
            MuhurtaType.EDUCATION: self.education_rules,
            MuhurtaType.PROPERTY: self.property_rules,
            MuhurtaType.GENERAL: self.business_rules,  # Use business rules as general default
            MuhurtaType.CUSTOM: {}  # No default rules for custom
        }
        return rules_map.get(muhurta_type, {})
    
    def _analyze_tithi(self, panchang: Dict, rules: Dict) -> Tuple[float, Dict]:
        """Analyze tithi favorability"""
        tithi = int(panchang.get('tithi', 0))
        tithi_name = panchang.get('tithi_name', '')
        
        score = 50.0  # Neutral score
        factors = {
            'tithi_number': tithi,
            'tithi_name': tithi_name,
            'favorable': False,
            'avoid': False
        }
        
        if 'favorable_tithis' in rules and tithi in rules['favorable_tithis']:
            score = 80.0
            factors['favorable'] = True
        elif 'avoid_tithis' in rules and tithi in rules['avoid_tithis']:
            score = 20.0
            factors['avoid'] = True
        
        # Special tithi considerations
        if tithi == 15 or tithi == 30:  # Purnima or Amavasya
            score -= 10  # Generally less favorable
        
        return score, factors
    
    def _analyze_nakshatra(self, panchang: Dict, rules: Dict) -> Tuple[float, Dict]:
        """Analyze nakshatra favorability"""
        nakshatra = panchang.get('nakshatra', '')
        nakshatra_lord = panchang.get('nakshatra_lord', '')
        
        score = 50.0  # Neutral score
        factors = {
            'nakshatra': nakshatra,
            'nakshatra_lord': nakshatra_lord,
            'favorable': False,
            'avoid': False
        }
        
        if 'favorable_nakshatras' in rules and nakshatra in rules['favorable_nakshatras']:
            score = 85.0
            factors['favorable'] = True
        elif 'avoid_nakshatras' in rules and nakshatra in rules['avoid_nakshatras']:
            score = 15.0
            factors['avoid'] = True
        
        # Check for Ganda Moola nakshatras (junction points)
        ganda_moola = ['Ashlesha', 'Magha', 'Moola', 'Jyeshtha', 'Revati', 'Ashwini']
        if nakshatra in ganda_moola:
            score -= 15
            factors['ganda_moola'] = True
        
        return score, factors
    
    def _analyze_yoga(self, panchang: Dict, rules: Dict) -> Tuple[float, Dict]:
        """Analyze yoga favorability"""
        yoga = panchang.get('yoga', 0)
        yoga_name = panchang.get('yoga_name', '')
        
        score = 50.0  # Neutral score
        factors = {
            'yoga_number': yoga,
            'yoga_name': yoga_name,
            'favorable': False
        }
        
        # Favorable yogas
        if yoga_name in ['Siddha', 'Sadhya', 'Shubha', 'Shukla', 'Brahma', 'Indra']:
            score = 90.0
            factors['favorable'] = True
            factors['excellent_yoga'] = True
        elif yoga_name in ['Vyaghata', 'Parigha', 'Vaidhriti']:
            score = 25.0
            factors['avoid'] = True
        
        return score, factors
    
    def _analyze_karana(self, panchang: Dict, rules: Dict) -> Tuple[float, Dict]:
        """Analyze karana favorability"""
        karana = panchang.get('karana', 0)
        karana_name = panchang.get('karana_name', '')
        
        score = 50.0  # Neutral score
        factors = {
            'karana_number': karana,
            'karana_name': karana_name,
            'favorable': False
        }
        
        # Favorable karanas
        favorable_karanas = ['Bava', 'Balava', 'Kaulava', 'Taitila', 'Gara', 'Vanija', 'Vishti']
        avoid_karanas = ['Shakuni', 'Chatushpada', 'Naga', 'Kimstughna']
        
        if karana_name in favorable_karanas:
            score = 75.0
            factors['favorable'] = True
        elif karana_name in avoid_karanas:
            score = 30.0
            factors['avoid'] = True
        
        return score, factors
    
    def _analyze_vara(self, panchang: Dict, rules: Dict) -> Tuple[float, Dict]:
        """Analyze day of week favorability"""
        vara_name = panchang.get('vara_name', '')
        
        score = 50.0  # Neutral score
        factors = {
            'vara': vara_name,
            'favorable': False,
            'avoid': False
        }
        
        if 'favorable_varas' in rules and vara_name in rules['favorable_varas']:
            score = 80.0
            factors['favorable'] = True
        elif 'avoid_varas' in rules and vara_name in rules['avoid_varas']:
            score = 30.0
            factors['avoid'] = True
        
        return score, factors
    
    def _analyze_inauspicious_periods(self, panchang: Dict, dt: datetime) -> Tuple[float, Dict]:
        """Analyze if time falls in inauspicious periods"""
        score = 100.0  # Start with perfect score
        factors = {
            'rahu_kaal': False,
            'gulika_kaal': False,
            'yamaganda_kaal': False,
            'clean_period': True
        }
        
        # For now, simplified check - in full implementation would compare actual times
        # Check if any inauspicious periods are present (simplified)
        if panchang.get('rahu_kaal'):
            # Would need proper time comparison logic here
            pass
            
        return score, factors
    
    def _analyze_moon_phase(self, panchang: Dict, muhurta_type: MuhurtaType) -> Tuple[float, Dict]:
        """Analyze moon phase favorability"""
        moon_phase = panchang.get('moon_phase', '')
        moon_illumination = panchang.get('moon_illumination', 0)
        
        score = 50.0
        factors = {
            'moon_phase': moon_phase,
            'illumination_percent': moon_illumination,
            'favorable': False
        }
        
        # Different muhurta types favor different moon phases
        if muhurta_type in [MuhurtaType.MARRIAGE, MuhurtaType.BUSINESS]:
            # Favor waxing moon for growth-oriented activities
            if 'Waxing' in moon_phase and moon_illumination > 25:
                score = 80.0
                factors['favorable'] = True
            elif 'Full' in moon_phase:
                score = 90.0
                factors['favorable'] = True
                factors['full_moon_power'] = True
        elif muhurta_type == MuhurtaType.TRAVEL:
            # Moderate illumination preferred for travel
            if 25 <= moon_illumination <= 75:
                score = 75.0
                factors['favorable'] = True
        
        return score, factors
    
    def _analyze_planetary_strength(self, panchang: Dict, rules: Dict) -> Tuple[float, Dict]:
        """Analyze planetary positions and strengths"""
        score = 50.0
        factors = {
            'planetary_analysis': {},
            'special_yogas': [],
            'planetary_strength': 'average'
        }
        
        graha_positions = panchang.get('graha_positions', {})
        
        # Analyze key planets based on muhurta type
        if 'special_considerations' in rules:
            for consideration, weight in rules['special_considerations'].items():
                if consideration == 'mercury_strength':
                    # Analyze Mercury position and strength
                    mercury = graha_positions.get('mercury', {})
                    if mercury:
                        mercury_long = mercury.get('longitude', 0)
                        mercury_strength = self._calculate_planetary_strength('mercury', mercury_long)
                        score += mercury_strength * weight / 100
                        factors['planetary_analysis']['mercury'] = {
                            'strength': mercury_strength,
                            'longitude': mercury_long,
                            'impact': weight
                        }
        
        return min(score, 100), factors
    
    def _calculate_planetary_strength(self, planet: str, longitude: float) -> float:
        """Calculate basic planetary strength based on sign placement"""
        # Simplified strength calculation
        strength = 50.0  # Base strength
        
        # Own sign and exaltation degrees (simplified)
        if planet == 'mercury':
            # Mercury exalted in Virgo (150-180°), own signs Gemini (60-90°) and Virgo
            if 150 <= longitude <= 165:  # Exaltation degree
                strength = 95.0
            elif (60 <= longitude <= 90) or (150 <= longitude <= 180):  # Own signs
                strength = 80.0
            elif 330 <= longitude <= 345:  # Debilitation in Pisces
                strength = 20.0
        
        return strength
    
    def _apply_custom_rules(self, panchang: Dict, custom_rules: Dict) -> Tuple[float, Dict]:
        """Apply custom user-defined rules"""
        score = 0.0
        factors = {'custom_rules_applied': custom_rules}
        return score, factors
    
    def _determine_quality(self, score: float) -> MuhurtaQuality:
        """Determine muhurta quality based on total score"""
        if score >= 85:
            return MuhurtaQuality.EXCELLENT
        elif score >= 75:
            return MuhurtaQuality.VERY_GOOD
        elif score >= 65:
            return MuhurtaQuality.GOOD
        elif score >= 50:
            return MuhurtaQuality.AVERAGE
        elif score >= 35:
            return MuhurtaQuality.POOR
        else:
            return MuhurtaQuality.AVOID
    
    def _generate_recommendations_warnings(self, factors: Dict, quality: MuhurtaQuality, 
                                         muhurta_type: MuhurtaType) -> Tuple[List[str], List[str]]:
        """Generate recommendations and warnings based on analysis"""
        recommendations = []
        warnings = []
        
        # Quality-based recommendations
        if quality == MuhurtaQuality.EXCELLENT:
            recommendations.append("Excellent time for this activity - all factors are highly favorable")
        elif quality == MuhurtaQuality.VERY_GOOD:
            recommendations.append("Very auspicious timing with strong favorable factors")
        elif quality == MuhurtaQuality.GOOD:
            recommendations.append("Good timing for this activity with mostly favorable conditions")
        elif quality == MuhurtaQuality.AVERAGE:
            recommendations.append("Acceptable timing but consider waiting for better muhurta if possible")
        else:
            warnings.append("This timing has significant challenges - strongly recommend finding alternative")
        
        return recommendations, warnings
    
    def _generate_description(self, dt: datetime, quality: MuhurtaQuality, 
                            muhurta_type: MuhurtaType, factors: Dict) -> str:
        """Generate descriptive text for the muhurta"""
        tithi_name = factors.get('tithi', {}).get('tithi_name', 'Unknown')
        nakshatra = factors.get('nakshatra', {}).get('nakshatra', 'Unknown')
        vara = factors.get('vara', {}).get('vara', 'Unknown')
        
        description = f"{quality.value.replace('_', ' ').title()} {muhurta_type.value} muhurta on {vara}, "
        description += f"{tithi_name} tithi in {nakshatra} nakshatra. "
        
        if quality in [MuhurtaQuality.EXCELLENT, MuhurtaQuality.VERY_GOOD]:
            description += "Highly recommended timing with strong traditional support."
        elif quality == MuhurtaQuality.GOOD:
            description += "Good timing with favorable astrological conditions."
        elif quality == MuhurtaQuality.AVERAGE:
            description += "Acceptable timing with mixed astrological factors."
        else:
            description += "Consider alternative timing due to challenging factors."
        
        return description
    
    def _is_excluded_period(self, dt: datetime, exclude_periods: Optional[List[Tuple[datetime, datetime]]]) -> bool:
        """Check if datetime falls in any excluded period"""
        if not exclude_periods:
            return False
        
        for start, end in exclude_periods:
            if start <= dt <= end:
                return True
        
        return False
    
    def get_best_muhurta(self, request: MuhurtaRequest) -> Optional[MuhurtaResult]:
        """Get the single best muhurta from the given time range"""
        results = self.find_muhurta(request)
        return results[0] if results else None
    
    def get_muhurta_calendar(self, start_date: datetime, end_date: datetime,
                           muhurta_type: MuhurtaType, lat: float, lon: float) -> Dict[str, List[MuhurtaResult]]:
        """
        Generate a calendar of good muhurta timings for a date range
        
        Returns:
            Dictionary with dates as keys and list of good muhurtas as values
        """
        calendar = {}
        current_date = start_date.date()
        end_date_obj = end_date.date()
        
        while current_date <= end_date_obj:
            day_start = datetime.combine(current_date, datetime.min.time()).replace(tzinfo=timezone.utc)
            day_end = day_start + timedelta(days=1)
            
            request = MuhurtaRequest(
                muhurta_type=muhurta_type,
                start_date=day_start,
                end_date=day_end,
                latitude=lat,
                longitude=lon
            )
            
            day_muhurtas = self.find_muhurta(request)
            # Only include good quality muhurtas
            good_muhurtas = [m for m in day_muhurtas if m.quality in [
                MuhurtaQuality.EXCELLENT, MuhurtaQuality.VERY_GOOD, MuhurtaQuality.GOOD
            ]]
            
            if good_muhurtas:
                calendar[current_date.isoformat()] = good_muhurtas
            
            current_date += timedelta(days=1)
        
        return calendar

# Convenience functions for common muhurta types
def find_marriage_muhurta(kaal_engine, start_date: datetime, end_date: datetime,
                         lat: float, lon: float, duration_hours: int = 2) -> List[MuhurtaResult]:
    """Find marriage muhurta timings"""
    engine = MuhurtaEngine(kaal_engine)
    request = MuhurtaRequest(
        muhurta_type=MuhurtaType.MARRIAGE,
        start_date=start_date,
        end_date=end_date,
        latitude=lat,
        longitude=lon,
        duration_minutes=duration_hours * 60
    )
    return engine.find_muhurta(request)

def find_business_muhurta(kaal_engine, start_date: datetime, end_date: datetime,
                         lat: float, lon: float) -> List[MuhurtaResult]:
    """Find business muhurta timings"""
    engine = MuhurtaEngine(kaal_engine)
    request = MuhurtaRequest(
        muhurta_type=MuhurtaType.BUSINESS,
        start_date=start_date,
        end_date=end_date,
        latitude=lat,
        longitude=lon
    )
    return engine.find_muhurta(request)

def find_travel_muhurta(kaal_engine, start_date: datetime, end_date: datetime,
                       lat: float, lon: float) -> List[MuhurtaResult]:
    """Find travel muhurta timings"""
    engine = MuhurtaEngine(kaal_engine)
    request = MuhurtaRequest(
        muhurta_type=MuhurtaType.TRAVEL,
        start_date=start_date,
        end_date=end_date,
        latitude=lat,
        longitude=lon
    )
    return engine.find_muhurta(request) 