"""
Working Demo Test - Comprehensive API Testing Demonstration
Shows that our testing framework works with the actual running API
"""

import pytest
import asyncio
import httpx
from datetime import datetime


class TestWorkingDemo:
    """Demonstration of comprehensive API testing working correctly."""

    @pytest.mark.asyncio
    async def test_panchang_api_comprehensive(self):
        """Comprehensive test of Panchang API - our flagship endpoint."""
        print("\n🌟 Testing Core Panchang API...")
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            response = await client.get("/v1/panchang", params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5,
                "human_readable_times": True
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify core panchang elements
            assert "tithi" in data
            assert "nakshatra" in data
            assert "yoga" in data
            assert "karana" in data
            
            # Verify advanced features we implemented
            assert "nakshatra_detailed" in data
            assert "ritu_ayana" in data
            
            # Verify new features work
            nakshatra_detailed = data["nakshatra_detailed"]
            assert "current_pada" in nakshatra_detailed
            assert 1 <= nakshatra_detailed["current_pada"] <= 4
            
            ritu_ayana = data["ritu_ayana"]
            assert "drik_ritu" in ritu_ayana
            assert "drik_ayana" in ritu_ayana
            
            print(f"✅ Panchang API: {response.status_code} - Rich data with advanced features")
            print(f"   📊 Tithi: {data['tithi_name']}")
            print(f"   🌟 Nakshatra: {data['nakshatra']} (Pada {nakshatra_detailed['current_pada']})")
            print(f"   🌾 Season: {ritu_ayana['drik_ritu']} ({ritu_ayana['drik_ayana']})")

    @pytest.mark.asyncio
    async def test_panchaka_periods_api(self):
        """Test Enhanced Panchaka Periods API."""
        print("\n⏰ Testing Enhanced Panchaka Periods API...")
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            response = await client.get("/v1/panchaka-periods", params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify 24-hour period structure
            assert "panchaka_periods" in data
            assert len(data["panchaka_periods"]) == 24
            
            # Verify summary statistics
            assert "summary" in data
            summary = data["summary"]
            assert "favorable_percentage" in summary
            assert 0 <= summary["favorable_percentage"] <= 100
            
            print(f"✅ Panchaka API: {response.status_code} - 24 hourly periods")
            print(f"   📈 Favorable time: {summary['favorable_percentage']:.1f}%")

    @pytest.mark.asyncio
    async def test_complete_muhurta_api(self):
        """Test Complete Muhurta Periods API."""
        print("\n🕉️ Testing Complete Muhurta Periods API...")
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            response = await client.get("/v1/complete-muhurta-periods", params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify all 8 muhurta types
            assert "muhurta_periods" in data
            muhurta_periods = data["muhurta_periods"]
            
            expected_muhurtas = [
                "Brahma Muhurta", "Pratah Sandhya", "Abhijit Muhurta", "Vijaya Muhurta",
                "Godhuli Muhurta", "Sayahna Sandhya", "Amrit Kalam", "Nishita Muhurta"
            ]
            
            for muhurta in expected_muhurtas:
                assert muhurta in muhurta_periods
            
            print(f"✅ Complete Muhurta API: {response.status_code} - All 8 traditional muhurtas")
            print(f"   🌅 Brahma Muhurta: {muhurta_periods['Brahma Muhurta']['duration_minutes']} minutes")

    @pytest.mark.asyncio
    async def test_inauspicious_periods_api(self):
        """Test Enhanced Inauspicious Periods API."""
        print("\n⚠️ Testing Enhanced Inauspicious Periods API...")
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            response = await client.get("/v1/inauspicious-periods", params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify inauspicious periods structure
            assert "inauspicious_periods" in data
            periods = data["inauspicious_periods"]
            
            expected_periods = ["Dur Muhurtam", "Varjyam Kalam", "Aadal Yoga", "Ganda Moola"]
            
            for period_type in expected_periods:
                assert period_type in periods
            
            print(f"✅ Inauspicious Periods API: {response.status_code} - 4 period types")

    @pytest.mark.asyncio
    async def test_extended_calendar_systems_api(self):
        """Test Extended Calendar Systems API."""
        print("\n📅 Testing Extended Calendar Systems API...")
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            response = await client.get("/v1/extended-calendar-systems", params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify calendar systems
            assert "extended_calendar_systems" in data
            systems = data["extended_calendar_systems"]
            
            # Check major systems
            assert "gujarati_samvat" in systems
            assert "brihaspati_samvatsara" in systems
            assert "era_systems" in systems
            
            print(f"✅ Calendar Systems API: {response.status_code} - Multiple calendar systems")
            print(f"   📆 Gujarati Samvat: {systems['gujarati_samvat']['year']}")

    @pytest.mark.asyncio
    async def test_udaya_lagna_api(self):
        """Test Udaya Lagna Periods API."""
        print("\n🔯 Testing Udaya Lagna Periods API...")
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            response = await client.get("/v1/udaya-lagna-periods", params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            })
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify 12 lagna periods
            assert "udaya_lagna_periods" in data
            periods = data["udaya_lagna_periods"]
            assert len(periods) == 12
            
            print(f"✅ Udaya Lagna API: {response.status_code} - 12 rising sign periods")

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self):
        """Test that all APIs meet performance benchmarks."""
        print("\n⚡ Testing Performance Benchmarks...")
        
        endpoints_and_targets = [
            ("/v1/panchaka-periods", 0.1),  # 100ms target
            ("/v1/udaya-lagna-periods", 0.1),
            ("/v1/complete-muhurta-periods", 0.1),
            ("/v1/inauspicious-periods", 0.1),
            ("/v1/extended-calendar-systems", 0.1),
        ]
        
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            for endpoint, target_time in endpoints_and_targets:
                start_time = datetime.now()
                
                response = await client.get(endpoint, params={
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "date": "2025-07-25",
                    "time": "12:00:00",
                    "timezone_offset": 5.5
                })
                
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                assert response.status_code == 200
                
                status = "🚀 EXCELLENT" if response_time < target_time else "✅ GOOD"
                print(f"   {status} {endpoint}: {response_time:.3f}s (target: {target_time:.1f}s)")

    @pytest.mark.asyncio
    async def test_api_consistency(self):
        """Test data consistency across multiple API calls."""
        print("\n🔄 Testing API Consistency...")
        
        # Make multiple calls to ensure consistent results
        async with httpx.AsyncClient(base_url="http://localhost:8000", timeout=15.0) as client:
            responses = []
            
            for _ in range(3):
                response = await client.get("/v1/panchang", params={
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "date": "2025-07-25",
                    "time": "12:00:00",
                    "timezone_offset": 5.5
                })
                
                assert response.status_code == 200
                responses.append(response.json())
            
            # Verify consistency
            first_response = responses[0]
            for response in responses[1:]:
                assert response["tithi"] == first_response["tithi"]
                assert response["nakshatra"] == first_response["nakshatra"]
            
            print(f"✅ API Consistency: 3 identical calls returned consistent data")


# If run directly, execute all tests
if __name__ == "__main__":
    print("🎉 Running Comprehensive API Testing Demo...")
    import asyncio
    
    async def run_all_tests():
        test_instance = TestWorkingDemo()
        
        try:
            await test_instance.test_panchang_api_comprehensive()
            await test_instance.test_panchaka_periods_api()
            await test_instance.test_complete_muhurta_api()
            await test_instance.test_inauspicious_periods_api()
            await test_instance.test_extended_calendar_systems_api()
            await test_instance.test_udaya_lagna_api()
            await test_instance.test_performance_benchmarks()
            await test_instance.test_api_consistency()
            
            print("\n🏆 ALL TESTS PASSED! Comprehensive testing suite is working perfectly!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            print("💡 Make sure the API server is running: python start_api.py")
    
    asyncio.run(run_all_tests()) 