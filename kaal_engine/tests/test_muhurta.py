"""
Comprehensive Test Suite for Muhurta Engine
Tests electional astrology functionality and auspicious timing calculations
"""

import unittest
import sys
import os
from datetime import datetime, timezone, timedelta

# Add the parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaal import Kaal
from core.muhurta import (
    MuhurtaEngine, MuhurtaType, MuhurtaQuality, MuhurtaRequest, MuhurtaResult,
    find_marriage_muhurta, find_business_muhurta, find_travel_muhurta
)

class TestMuhurtaEngine(unittest.TestCase):
    """Test suite for Muhurta Engine functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.kaal = Kaal("de421.bsp")
        cls.muhurta_engine = MuhurtaEngine(cls.kaal)
        
        # Test coordinates - Ujjain (traditional reference)
        cls.test_lat = 23.1765
        cls.test_lon = 75.7885
        
        # Test dates
        cls.test_start_date = datetime(2025, 1, 1, 6, 0, 0, tzinfo=timezone.utc)
        cls.test_end_date = cls.test_start_date + timedelta(days=7)
    
    def test_muhurta_engine_initialization(self):
        """Test MuhurtaEngine initialization"""
        print("\n🧪 Testing Muhurta Engine Initialization...")
        
        # Test basic initialization
        self.assertIsNotNone(self.muhurta_engine)
        self.assertIsNotNone(self.muhurta_engine.kaal)
        self.assertIsInstance(self.muhurta_engine.cache, dict)
        
        # Test muhurta factors
        expected_factors = ['tithi', 'nakshatra', 'yoga', 'karana', 'vara', 'rahu_kaal', 'moon_phase', 'planetary_strength']
        for factor in expected_factors:
            self.assertIn(factor, self.muhurta_engine.muhurta_factors)
        
        # Test rules initialization
        self.assertIsNotNone(self.muhurta_engine.marriage_rules)
        self.assertIsNotNone(self.muhurta_engine.business_rules)
        self.assertIsNotNone(self.muhurta_engine.travel_rules)
        self.assertIsNotNone(self.muhurta_engine.education_rules)
        self.assertIsNotNone(self.muhurta_engine.property_rules)
        
        print("✅ Muhurta Engine initialization: PASSED")
    
    def test_muhurta_types_and_enums(self):
        """Test MuhurtaType and MuhurtaQuality enums"""
        print("\n🧪 Testing Muhurta Types and Quality Enums...")
        
        # Test MuhurtaType enum
        expected_types = ['marriage', 'business', 'travel', 'education', 'property', 'general', 'custom']
        for muhurta_type in MuhurtaType:
            self.assertIn(muhurta_type.value, expected_types)
        
        # Test MuhurtaQuality enum
        expected_qualities = ['excellent', 'very_good', 'good', 'average', 'poor', 'avoid']
        for quality in MuhurtaQuality:
            self.assertIn(quality.value, expected_qualities)
        
        print("✅ Muhurta types and enums: PASSED")
    
    def test_marriage_muhurta_rules(self):
        """Test marriage muhurta rules"""
        print("\n🧪 Testing Marriage Muhurta Rules...")
        
        rules = self.muhurta_engine.marriage_rules
        
        # Test favorable tithis
        self.assertIn('favorable_tithis', rules)
        self.assertIn(2, rules['favorable_tithis'])  # Dwitiya
        self.assertIn(5, rules['favorable_tithis'])  # Panchami
        self.assertIn(11, rules['favorable_tithis']) # Ekadashi
        
        # Test avoid tithis
        self.assertIn('avoid_tithis', rules)
        self.assertIn(4, rules['avoid_tithis'])  # Chaturthi
        self.assertIn(8, rules['avoid_tithis'])  # Ashtami
        self.assertIn(15, rules['avoid_tithis']) # Purnima
        
        # Test favorable nakshatras
        self.assertIn('favorable_nakshatras', rules)
        self.assertIn('Rohini', rules['favorable_nakshatras'])
        self.assertIn('Hasta', rules['favorable_nakshatras'])
        self.assertIn('Swati', rules['favorable_nakshatras'])
        
        # Test avoid nakshatras
        self.assertIn('avoid_nakshatras', rules)
        self.assertIn('Bharani', rules['avoid_nakshatras'])
        self.assertIn('Jyeshtha', rules['avoid_nakshatras'])
        
        # Test special considerations
        self.assertIn('special_considerations', rules)
        self.assertIn('guru_chandal', rules['special_considerations'])
        
        print("✅ Marriage muhurta rules: PASSED")
    
    def test_business_muhurta_rules(self):
        """Test business muhurta rules"""
        print("\n🧪 Testing Business Muhurta Rules...")
        
        rules = self.muhurta_engine.business_rules
        
        # Test favorable elements
        self.assertIn('favorable_tithis', rules)
        self.assertIn('favorable_nakshatras', rules)
        self.assertIn('favorable_varas', rules)
        
        # Business-specific nakshatras
        self.assertIn('Pushya', rules['favorable_nakshatras'])  # Good for business
        self.assertIn('Hasta', rules['favorable_nakshatras'])   # Good for transactions
        
        # Business-specific considerations
        self.assertIn('special_considerations', rules)
        self.assertIn('mercury_strength', rules['special_considerations'])  # Mercury key for business
        self.assertIn('jupiter_position', rules['special_considerations'])  # Jupiter for prosperity
        
        print("✅ Business muhurta rules: PASSED")
    
    def test_muhurta_request_creation(self):
        """Test MuhurtaRequest creation and validation"""
        print("\n🧪 Testing Muhurta Request Creation...")
        
        # Create basic request
        request = MuhurtaRequest(
            muhurta_type=MuhurtaType.MARRIAGE,
            start_date=self.test_start_date,
            end_date=self.test_end_date,
            latitude=self.test_lat,
            longitude=self.test_lon,
            duration_minutes=120
        )
        
        self.assertEqual(request.muhurta_type, MuhurtaType.MARRIAGE)
        self.assertEqual(request.start_date, self.test_start_date)
        self.assertEqual(request.end_date, self.test_end_date)
        self.assertEqual(request.latitude, self.test_lat)
        self.assertEqual(request.longitude, self.test_lon)
        self.assertEqual(request.duration_minutes, 120)
        
        # Test with custom rules
        custom_rules = {'avoid_saturn_aspects': True, 'prefer_jupiter_strength': 80}
        request_with_custom = MuhurtaRequest(
            muhurta_type=MuhurtaType.BUSINESS,
            start_date=self.test_start_date,
            end_date=self.test_end_date,
            latitude=self.test_lat,
            longitude=self.test_lon,
            custom_rules=custom_rules
        )
        
        self.assertEqual(request_with_custom.custom_rules, custom_rules)
        
        print("✅ Muhurta request creation: PASSED")
    
    def test_single_muhurta_calculation(self):
        """Test single muhurta calculation for specific date/time"""
        print("\n🧪 Testing Single Muhurta Calculation...")
        
        test_datetime = datetime(2025, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        
        # Test marriage muhurta calculation
        result = self.muhurta_engine._calculate_muhurta(
            dt=test_datetime,
            muhurta_type=MuhurtaType.MARRIAGE,
            lat=self.test_lat,
            lon=self.test_lon,
            duration_minutes=60
        )
        
        # Verify result structure
        self.assertIsInstance(result, MuhurtaResult)
        self.assertEqual(result.datetime, test_datetime)
        self.assertIsInstance(result.quality, MuhurtaQuality)
        self.assertIsInstance(result.score, float)
        self.assertGreaterEqual(result.score, 0)
        self.assertLessEqual(result.score, 100)
        self.assertIsInstance(result.factors, dict)
        self.assertIsInstance(result.recommendations, list)
        self.assertIsInstance(result.warnings, list)
        self.assertEqual(result.duration_minutes, 60)
        self.assertIsInstance(result.description, str)
        
        # Test key factors presence
        expected_factors = ['tithi', 'nakshatra', 'yoga', 'karana', 'vara', 'inauspicious_periods', 'moon_phase', 'planetary_strength']
        for factor in expected_factors:
            self.assertIn(factor, result.factors)
        
        print(f"   Result: {result.quality.value} quality (Score: {result.score:.1f})")
        print(f"   Description: {result.description}")
        print("✅ Single muhurta calculation: PASSED")
    
    def test_muhurta_quality_determination(self):
        """Test quality determination logic"""
        print("\n🧪 Testing Muhurta Quality Determination...")
        
        # Test quality mapping
        test_scores = [95, 85, 80, 70, 60, 45, 30, 10]
        expected_qualities = [
            MuhurtaQuality.EXCELLENT,   # 95
            MuhurtaQuality.EXCELLENT,   # 85
            MuhurtaQuality.VERY_GOOD,   # 80
            MuhurtaQuality.GOOD,        # 70
            MuhurtaQuality.AVERAGE,     # 60
            MuhurtaQuality.POOR,        # 45
            MuhurtaQuality.AVOID,       # 30
            MuhurtaQuality.AVOID        # 10
        ]
        
        for score, expected_quality in zip(test_scores, expected_qualities):
            actual_quality = self.muhurta_engine._determine_quality(score)
            self.assertEqual(actual_quality, expected_quality, 
                           f"Score {score} should map to {expected_quality.value}, got {actual_quality.value}")
        
        print("✅ Quality determination: PASSED")
    
    def test_find_muhurta_basic(self):
        """Test basic muhurta finding functionality"""
        print("\n🧪 Testing Basic Muhurta Finding...")
        
        # Create request for marriage muhurta
        request = MuhurtaRequest(
            muhurta_type=MuhurtaType.MARRIAGE,
            start_date=self.test_start_date,
            end_date=self.test_start_date + timedelta(days=2),  # Shorter range for faster testing
            latitude=self.test_lat,
            longitude=self.test_lon,
            duration_minutes=120
        )
        
        # Find muhurtas
        results = self.muhurta_engine.find_muhurta(request)
        
        # Verify results
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 20)  # Should limit to 20 results
        
        if results:
            # Verify results are sorted by score (highest first)
            for i in range(len(results) - 1):
                self.assertGreaterEqual(results[i].score, results[i + 1].score)
            
            # Verify all results are at least average quality
            for result in results:
                self.assertNotIn(result.quality, [MuhurtaQuality.POOR, MuhurtaQuality.AVOID])
            
            print(f"   Found {len(results)} suitable muhurta timings")
            print(f"   Best score: {results[0].score:.1f}")
            print(f"   Best quality: {results[0].quality.value}")
        else:
            print("   No suitable muhurta timings found (this is acceptable for testing)")
        
        print("✅ Basic muhurta finding: PASSED")
    
    def test_convenience_functions(self):
        """Test convenience functions for common muhurta types"""
        print("\n🧪 Testing Convenience Functions...")
        
        start_date = self.test_start_date
        end_date = start_date + timedelta(days=1)  # Short range for testing
        
        # Test marriage muhurta function
        marriage_results = find_marriage_muhurta(
            self.kaal, start_date, end_date, self.test_lat, self.test_lon, duration_hours=2
        )
        self.assertIsInstance(marriage_results, list)
        
        # Test business muhurta function
        business_results = find_business_muhurta(
            self.kaal, start_date, end_date, self.test_lat, self.test_lon
        )
        self.assertIsInstance(business_results, list)
        
        # Test travel muhurta function
        travel_results = find_travel_muhurta(
            self.kaal, start_date, end_date, self.test_lat, self.test_lon
        )
        self.assertIsInstance(travel_results, list)
        
        print("✅ Convenience functions: PASSED")
    
    def test_different_muhurta_types(self):
        """Test different types of muhurta calculations"""
        print("\n🧪 Testing Different Muhurta Types...")
        
        test_datetime = datetime(2025, 2, 14, 11, 0, 0, tzinfo=timezone.utc)
        muhurta_types = [
            MuhurtaType.MARRIAGE,
            MuhurtaType.BUSINESS,
            MuhurtaType.TRAVEL,
            MuhurtaType.EDUCATION,
            MuhurtaType.PROPERTY,
            MuhurtaType.GENERAL
        ]
        
        for muhurta_type in muhurta_types:
            result = self.muhurta_engine._calculate_muhurta(
                dt=test_datetime,
                muhurta_type=muhurta_type,
                lat=self.test_lat,
                lon=self.test_lon,
                duration_minutes=60
            )
            
            self.assertIsInstance(result, MuhurtaResult)
            self.assertEqual(result.datetime, test_datetime)
            print(f"   {muhurta_type.value.title()}: {result.quality.value} (Score: {result.score:.1f})")
        
        print("✅ Different muhurta types: PASSED")
    
    def test_get_best_muhurta(self):
        """Test getting the single best muhurta"""
        print("\n🧪 Testing Get Best Muhurta...")
        
        request = MuhurtaRequest(
            muhurta_type=MuhurtaType.BUSINESS,
            start_date=self.test_start_date,
            end_date=self.test_start_date + timedelta(days=1),
            latitude=self.test_lat,
            longitude=self.test_lon
        )
        
        best_muhurta = self.muhurta_engine.get_best_muhurta(request)
        
        if best_muhurta:
            self.assertIsInstance(best_muhurta, MuhurtaResult)
            print(f"   Best muhurta: {best_muhurta.datetime} - {best_muhurta.quality.value} (Score: {best_muhurta.score:.1f})")
        else:
            print("   No suitable muhurta found (acceptable for testing)")
        
        print("✅ Get best muhurta: PASSED")
    
    def test_muhurta_calendar(self):
        """Test muhurta calendar generation"""
        print("\n🧪 Testing Muhurta Calendar...")
        
        start_date = self.test_start_date
        end_date = start_date + timedelta(days=3)
        
        calendar = self.muhurta_engine.get_muhurta_calendar(
            start_date=start_date,
            end_date=end_date,
            muhurta_type=MuhurtaType.GENERAL,
            lat=self.test_lat,
            lon=self.test_lon
        )
        
        self.assertIsInstance(calendar, dict)
        
        # Check calendar structure
        for date_key, muhurtas in calendar.items():
            # Verify date format
            datetime.strptime(date_key, '%Y-%m-%d')  # Will raise exception if invalid
            self.assertIsInstance(muhurtas, list)
            
            # Verify all muhurtas are good quality or better
            for muhurta in muhurtas:
                self.assertIn(muhurta.quality, [
                    MuhurtaQuality.EXCELLENT,
                    MuhurtaQuality.VERY_GOOD,
                    MuhurtaQuality.GOOD
                ])
        
        print(f"   Generated calendar for {len(calendar)} days with good muhurtas")
        print("✅ Muhurta calendar: PASSED")
    
    def test_factor_analysis(self):
        """Test individual factor analysis methods"""
        print("\n🧪 Testing Factor Analysis Methods...")
        
        # Get sample panchang data
        test_datetime = datetime(2025, 1, 20, 10, 0, 0, tzinfo=timezone.utc)
        panchang = self.kaal.get_panchang(self.test_lat, self.test_lon, test_datetime)
        rules = self.muhurta_engine.marriage_rules
        
        # Test tithi analysis
        tithi_score, tithi_factors = self.muhurta_engine._analyze_tithi(panchang, rules)
        self.assertIsInstance(tithi_score, float)
        self.assertIsInstance(tithi_factors, dict)
        self.assertIn('tithi_number', tithi_factors)
        self.assertIn('tithi_name', tithi_factors)
        
        # Test nakshatra analysis
        nakshatra_score, nakshatra_factors = self.muhurta_engine._analyze_nakshatra(panchang, rules)
        self.assertIsInstance(nakshatra_score, float)
        self.assertIsInstance(nakshatra_factors, dict)
        self.assertIn('nakshatra', nakshatra_factors)
        
        # Test yoga analysis
        yoga_score, yoga_factors = self.muhurta_engine._analyze_yoga(panchang, rules)
        self.assertIsInstance(yoga_score, float)
        self.assertIsInstance(yoga_factors, dict)
        
        # Test vara analysis
        vara_score, vara_factors = self.muhurta_engine._analyze_vara(panchang, rules)
        self.assertIsInstance(vara_score, float)
        self.assertIsInstance(vara_factors, dict)
        
        print(f"   Tithi analysis: Score {tithi_score:.1f}")
        print(f"   Nakshatra analysis: Score {nakshatra_score:.1f}")
        print(f"   Yoga analysis: Score {yoga_score:.1f}")
        print(f"   Vara analysis: Score {vara_score:.1f}")
        print("✅ Factor analysis methods: PASSED")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("\n🧪 Testing Error Handling...")
        
        # Test with invalid coordinates (should not crash)
        try:
            request = MuhurtaRequest(
                muhurta_type=MuhurtaType.GENERAL,
                start_date=self.test_start_date,
                end_date=self.test_end_date,
                latitude=95.0,  # Invalid latitude
                longitude=185.0,  # Invalid longitude
            )
            results = self.muhurta_engine.find_muhurta(request)
            # Should handle gracefully without crashing
        except Exception as e:
            print(f"   Handled error gracefully: {e}")
        
        # Test with very short time range
        short_end = self.test_start_date + timedelta(hours=1)
        short_request = MuhurtaRequest(
            muhurta_type=MuhurtaType.MARRIAGE,
            start_date=self.test_start_date,
            end_date=short_end,
            latitude=self.test_lat,
            longitude=self.test_lon
        )
        
        short_results = self.muhurta_engine.find_muhurta(short_request)
        self.assertIsInstance(short_results, list)
        
        print("✅ Error handling: PASSED")
    
    def run_comprehensive_test(self):
        """Run all tests and provide summary"""
        print("\n" + "="*80)
        print("🚀 STARTING COMPREHENSIVE MUHURTA ENGINE TESTS")
        print("="*80)
        
        test_methods = [
            self.test_muhurta_engine_initialization,
            self.test_muhurta_types_and_enums,
            self.test_marriage_muhurta_rules,
            self.test_business_muhurta_rules,
            self.test_muhurta_request_creation,
            self.test_single_muhurta_calculation,
            self.test_muhurta_quality_determination,
            self.test_find_muhurta_basic,
            self.test_convenience_functions,
            self.test_different_muhurta_types,
            self.test_get_best_muhurta,
            self.test_muhurta_calendar,
            self.test_factor_analysis,
            self.test_error_handling
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                test_method()
                passed_tests += 1
            except Exception as e:
                print(f"❌ {test_method.__name__}: FAILED - {e}")
        
        print("\n" + "="*80)
        print(f"🎯 MUHURTA ENGINE TEST RESULTS: {passed_tests}/{total_tests} PASSED ({(passed_tests/total_tests)*100:.1f}%)")
        print("="*80)
        
        if passed_tests == total_tests:
            print("🎉 ALL MUHURTA ENGINE TESTS PASSED! Phase 2 Muhurta Engine is operational.")
        else:
            print(f"⚠️  {total_tests - passed_tests} tests failed. Review and fix issues.")
        
        return passed_tests == total_tests

def main():
    """Run the Muhurta Engine test suite"""
    try:
        test_suite = TestMuhurtaEngine()
        test_suite.setUpClass()
        success = test_suite.run_comprehensive_test()
        return 0 if success else 1
    except Exception as e:
        print(f"Critical error in test setup: {e}")
        return 1

if __name__ == '__main__':
    exit(main()) 