"""
Comprehensive tests for the Hindu Festival Calendar System
Tests all festival types, regional variations, and calendar generation
"""

import unittest
from datetime import datetime, date, timezone
import json
from kaal_engine.kaal import Kaal
from kaal_engine.core.festivals import (
    FestivalEngine, FestivalRule, FestivalDate, HinduCalendar,
    FestivalType, FestivalCategory, Region,
    get_major_festivals, get_regional_festivals, get_spiritual_observances
)

class TestFestivalCalendar(unittest.TestCase):
    """Test suite for Festival Calendar System"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.kaal = Kaal('de421.bsp')  # Use the available ephemeris file
        cls.festival_engine = FestivalEngine(cls.kaal)
    
    def test_hindu_calendar_constants(self):
        """Test Hindu calendar constants and utilities"""
        calendar = HinduCalendar()
        
        # Test month lists
        self.assertEqual(len(calendar.HINDU_MONTHS), 12)
        self.assertEqual(len(calendar.SOLAR_MONTHS), 12)
        self.assertEqual(len(calendar.NAKSHATRAS), 27)
        
        # Test specific months
        self.assertIn("Chaitra", calendar.HINDU_MONTHS)
        self.assertIn("Kartik", calendar.HINDU_MONTHS)
        self.assertIn("Mesha", calendar.SOLAR_MONTHS)
        self.assertIn("Makara", calendar.SOLAR_MONTHS)
        
        # Test nakshatras
        self.assertIn("Ashwini", calendar.NAKSHATRAS)
        self.assertIn("Revati", calendar.NAKSHATRAS)
    
    def test_festival_rule_creation(self):
        """Test festival rule structure and validation"""
        # Test major festival rule
        diwali_rule = FestivalRule(
            name="Diwali",
            english_name="Diwali",
            festival_type=FestivalType.LUNAR,
            category=FestivalCategory.MAJOR,
            regions=[Region.ALL_INDIA],
            month="Kartik",
            paksha="krishna",
            tithi=15,
            description="Festival of lights"
        )
        
        self.assertEqual(diwali_rule.name, "Diwali")
        self.assertEqual(diwali_rule.festival_type, FestivalType.LUNAR)
        self.assertEqual(diwali_rule.category, FestivalCategory.MAJOR)
        self.assertEqual(diwali_rule.tithi, 15)
        self.assertEqual(diwali_rule.duration_days, 1)
    
    def test_festival_engine_initialization(self):
        """Test festival engine initialization and database loading"""
        self.assertIsInstance(self.festival_engine, FestivalEngine)
        self.assertGreater(len(self.festival_engine.festival_rules), 0)
        
        # Check that major festivals are loaded
        festival_names = [rule.name for rule in self.festival_engine.festival_rules]
        
        # Major festivals should be present
        self.assertIn("Diwali", festival_names)
        self.assertIn("Holi", festival_names)
        self.assertIn("Krishna Janmashtami", festival_names)
        self.assertIn("Ram Navami", festival_names)
        
        # Regional festivals should be present
        self.assertIn("Durga Puja", festival_names)
        self.assertIn("Onam", festival_names)
        
        # Spiritual observances should be present
        self.assertIn("Ekadashi", festival_names)
        self.assertIn("Maha Shivaratri", festival_names)
    
    def test_festival_calculation(self):
        """Test calculation of festivals for a year"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        # Should have festivals
        self.assertGreater(len(festivals), 0)
        
        # Check that all festivals have valid dates
        for festival in festivals:
            self.assertIsInstance(festival.date, date)
            self.assertEqual(festival.year, year)
            self.assertIsInstance(festival.festival_rule, FestivalRule)
    
    def test_lunar_festival_calculation(self):
        """Test calculation of lunar festivals"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        # Should have festivals
        self.assertGreater(len(festivals), 0)
        
        # Check that all festivals have valid dates
        for festival in festivals:
            self.assertIsInstance(festival.date, date)
            self.assertEqual(festival.year, year)
            self.assertIsInstance(festival.festival_rule, FestivalRule)
        
        # Check for specific major festivals
        festival_names = [f.festival_rule.name for f in festivals]
        self.assertIn("Diwali", festival_names)
        self.assertIn("Holi", festival_names)
    
    def test_solar_festival_calculation(self):
        """Test calculation of solar festivals"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        # Look for solar festivals
        solar_festivals = [f for f in festivals if f.festival_rule.festival_type == FestivalType.SOLAR]
        self.assertGreater(len(solar_festivals), 0)
        
        # Check for Makar Sankranti
        sankranti_festivals = [f for f in solar_festivals if f.festival_rule.name == "Makar Sankranti"]
        self.assertGreater(len(sankranti_festivals), 0)
        
        # Makar Sankranti should be around January 14/15
        for festival in sankranti_festivals:
            self.assertEqual(festival.date.month, 1)
            self.assertIn(festival.date.day, [13, 14, 15])
    
    def test_ekadashi_calculation(self):
        """Test calculation of Ekadashi observances"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        # Look for Ekadashi festivals
        ekadashi_festivals = [f for f in festivals if f.festival_rule.name == "Ekadashi"]
        
        # Should have at least 20 Ekadashi dates (2 per month minimum)
        self.assertGreaterEqual(len(ekadashi_festivals), 20)
        
        # Check that both paksha types are present
        paksha_types = set()
        for festival in ekadashi_festivals:
            if 'paksha' in festival.additional_info:
                paksha_types.add(festival.additional_info['paksha'])
        
        self.assertIn('shukla', paksha_types)
        self.assertIn('krishna', paksha_types)
    
    def test_regional_filtering(self):
        """Test regional festival filtering"""
        year = 2024
        
        # Test all India festivals
        all_india_festivals = self.festival_engine.calculate_festival_dates(
            year, regions=[Region.ALL_INDIA]
        )
        self.assertGreater(len(all_india_festivals), 0)
        
        # Test Bengal specific festivals
        bengal_festivals = self.festival_engine.calculate_festival_dates(
            year, regions=[Region.BENGAL]
        )
        
        # Should include both all-India and Bengal specific festivals
        bengal_names = [f.festival_rule.name for f in bengal_festivals]
        self.assertIn("Durga Puja", bengal_names)  # Bengal specific
        self.assertIn("Diwali", bengal_names)      # All India
        
        # Test South India festivals
        south_festivals = self.festival_engine.calculate_festival_dates(
            year, regions=[Region.SOUTH_INDIA]
        )
        south_names = [f.festival_rule.name for f in south_festivals]
        # Should include south-specific festivals
        # (In our current implementation, we have some marked as SOUTH_INDIA)
    
    def test_category_filtering(self):
        """Test festival category filtering"""
        year = 2024
        
        # Test major festivals only
        major_festivals = self.festival_engine.calculate_festival_dates(
            year, categories=[FestivalCategory.MAJOR]
        )
        
        for festival in major_festivals:
            self.assertEqual(festival.festival_rule.category, FestivalCategory.MAJOR)
        
        # Should include major festivals like Diwali, Holi
        major_names = [f.festival_rule.name for f in major_festivals]
        self.assertIn("Diwali", major_names)
        self.assertIn("Holi", major_names)
        
        # Test spiritual observances only
        spiritual_festivals = self.festival_engine.calculate_festival_dates(
            year, categories=[FestivalCategory.SPIRITUAL]
        )
        
        for festival in spiritual_festivals:
            self.assertEqual(festival.festival_rule.category, FestivalCategory.SPIRITUAL)
        
        spiritual_names = [f.festival_rule.name for f in spiritual_festivals]
        self.assertIn("Ekadashi", spiritual_names)
    
    def test_month_specific_festivals(self):
        """Test getting festivals for specific months"""
        year = 2024
        
        # Test January festivals
        jan_festivals = self.festival_engine.get_festivals_for_month(year, 1)
        for festival in jan_festivals:
            self.assertEqual(festival.date.month, 1)
        
        # Should include Makar Sankranti in January
        jan_names = [f.festival_rule.name for f in jan_festivals]
        self.assertIn("Makar Sankranti", jan_names)
        
        # Test October festivals (likely to have Diwali)
        oct_festivals = self.festival_engine.get_festivals_for_month(year, 10)
        oct_names = [f.festival_rule.name for f in oct_festivals]
        # Note: Diwali date varies, might not always be in October
    
    def test_date_specific_festivals(self):
        """Test getting festivals for specific dates"""
        # Test with a known festival date (approximate)
        test_date = date(2024, 1, 14)  # Makar Sankranti
        
        festivals = self.festival_engine.get_festivals_for_date(test_date)
        
        # Might have festivals on this date
        if festivals:
            for festival in festivals:
                self.assertEqual(festival.date, test_date)
    
    def test_calendar_generation(self):
        """Test comprehensive calendar generation"""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        calendar = self.festival_engine.generate_calendar(start_date, end_date)
        
        self.assertIsInstance(calendar, dict)
        
        # Should have entries for various dates
        self.assertGreater(len(calendar), 0)
        
        # Check that all dates are within range
        for date_str, festivals in calendar.items():
            festival_date = date.fromisoformat(date_str)
            self.assertGreaterEqual(festival_date, start_date)
            self.assertLessEqual(festival_date, end_date)
            
            # Each date should have a list of festivals
            self.assertIsInstance(festivals, list)
            for festival in festivals:
                self.assertIsInstance(festival, FestivalDate)
    
    def test_json_export(self):
        """Test JSON export functionality"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)[:10]  # Limit for testing
        
        json_output = self.festival_engine.export_to_json(festivals)
        
        # Should be valid JSON
        parsed_data = json.loads(json_output)
        self.assertIsInstance(parsed_data, list)
        
        # Check structure of first festival
        if parsed_data:
            first_festival = parsed_data[0]
            required_fields = [
                'name', 'english_name', 'date', 'year', 'type', 
                'category', 'regions', 'description'
            ]
            
            for field in required_fields:
                self.assertIn(field, first_festival)
    
    def test_ical_export(self):
        """Test iCal export functionality"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)[:5]  # Limit for testing
        
        ical_output = self.festival_engine.export_to_ical(festivals)
        
        # Should contain iCal headers
        self.assertIn("BEGIN:VCALENDAR", ical_output)
        self.assertIn("END:VCALENDAR", ical_output)
        self.assertIn("VERSION:2.0", ical_output)
        self.assertIn("PRODID:", ical_output)
        
        # Should contain events
        self.assertIn("BEGIN:VEVENT", ical_output)
        self.assertIn("END:VEVENT", ical_output)
        
        # Should contain festival information
        if festivals:
            self.assertIn(festivals[0].festival_rule.english_name, ical_output)
    
    def test_convenience_functions(self):
        """Test convenience functions for common use cases"""
        year = 2024
        
        # Test get_major_festivals
        major_festivals = get_major_festivals(year, self.kaal)
        self.assertIsInstance(major_festivals, list)
        
        if major_festivals:
            for festival in major_festivals:
                self.assertEqual(festival.festival_rule.category, FestivalCategory.MAJOR)
        
        # Test get_regional_festivals
        bengal_festivals = get_regional_festivals(year, Region.BENGAL, self.kaal)
        self.assertIsInstance(bengal_festivals, list)
        
        # Test get_spiritual_observances
        spiritual_festivals = get_spiritual_observances(year, self.kaal)
        self.assertIsInstance(spiritual_festivals, list)
        
        if spiritual_festivals:
            for festival in spiritual_festivals:
                self.assertEqual(festival.festival_rule.category, FestivalCategory.SPIRITUAL)
    
    def test_multi_year_calculation(self):
        """Test festival calculation across multiple years"""
        start_date = date(2024, 6, 1)
        end_date = date(2025, 5, 31)
        
        calendar = self.festival_engine.generate_calendar(start_date, end_date)
        
        # Should span multiple years
        years_found = set()
        for date_str in calendar.keys():
            festival_date = date.fromisoformat(date_str)
            years_found.add(festival_date.year)
        
        self.assertIn(2024, years_found)
        self.assertIn(2025, years_found)
    
    def test_festival_date_structure(self):
        """Test FestivalDate object structure and data integrity"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        if festivals:
            festival = festivals[0]
            
            # Check required attributes
            self.assertIsInstance(festival.festival_rule, FestivalRule)
            self.assertIsInstance(festival.date, date)
            self.assertEqual(festival.year, year)
            self.assertIsInstance(festival.additional_info, dict)
            self.assertIsInstance(festival.regional_variations, dict)
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with empty regions list
        festivals = self.festival_engine.calculate_festival_dates(2024, regions=[])
        # Should still work with default behavior
        
        # Test with very early year
        early_festivals = self.festival_engine.calculate_festival_dates(1000)
        # Should handle gracefully
        
        # Test with future year
        future_festivals = self.festival_engine.calculate_festival_dates(3000)
        # Should handle gracefully
    
    def test_festival_types_coverage(self):
        """Test that all festival types are represented"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        festival_types = set()
        for festival in festivals:
            festival_types.add(festival.festival_rule.festival_type)
        
        # Should have multiple festival types
        self.assertIn(FestivalType.LUNAR, festival_types)
        self.assertIn(FestivalType.SOLAR, festival_types)
        # May have others depending on implementation
    
    def test_festival_categories_coverage(self):
        """Test that multiple festival categories are represented"""
        year = 2024
        festivals = self.festival_engine.calculate_festival_dates(year)
        
        categories = set()
        for festival in festivals:
            categories.add(festival.festival_rule.category)
        
        # Should have multiple categories
        self.assertIn(FestivalCategory.MAJOR, categories)
        self.assertIn(FestivalCategory.SPIRITUAL, categories)
        # May have others depending on implementation

if __name__ == '__main__':
    unittest.main() 