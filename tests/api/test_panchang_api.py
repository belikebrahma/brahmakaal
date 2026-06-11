"""
Enhanced Panchang API Tests
Comprehensive testing for the core panchang functionality with advanced features
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any


class TestPanchangAPI:
    """Test suite for Enhanced Panchang API endpoint."""

    @pytest.mark.asyncio
    async def test_panchang_basic_functionality(self, test_client, test_locations, test_dates):
        """Test basic panchang functionality."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"],
                "ayanamsha": "LAHIRI"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        required_fields = [
            "tithi", "tithi_name", "nakshatra", "nakshatra_name", 
            "yoga", "yoga_name", "karana", "karana_name",
            "sunrise", "sunset", "solar_noon", "moonrise", "moonset",
            "paksha", "vara", "ritu", "ayana"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(data["tithi"], (int, float))
        assert isinstance(data["tithi_name"], str)
        assert isinstance(data["nakshatra"], (int, float))
        assert isinstance(data["nakshatra_name"], str)

    @pytest.mark.asyncio
    async def test_panchang_advanced_features(self, test_client, test_locations, test_dates):
        """Test advanced panchang features (Nakshatra Pada & Ritu Ayana)."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Test Nakshatra Pada system
        assert "nakshatra_detailed" in data
        nakshatra_detailed = data["nakshatra_detailed"]
        
        assert "current_nakshatra" in nakshatra_detailed
        assert "current_pada" in nakshatra_detailed
        assert "current_pada_name" in nakshatra_detailed
        assert "position_in_pada_percent" in nakshatra_detailed
        assert "pada_transitions" in nakshatra_detailed
        
        # Verify pada values are valid (1-4)
        assert 1 <= nakshatra_detailed["current_pada"] <= 4
        assert 0 <= nakshatra_detailed["position_in_pada_percent"] <= 100
        
        # Test Ritu & Ayana system
        assert "ritu_ayana" in data
        ritu_ayana = data["ritu_ayana"]
        
        assert "drik_ritu" in ritu_ayana
        assert "drik_ayana" in ritu_ayana
        assert "dinamana" in ritu_ayana
        assert "ratrimana" in ritu_ayana
        assert "madhyahna" in ritu_ayana
        
        # Verify ritu values
        valid_ritus = ["Vasant", "Grishma", "Varsha", "Sharad", "Shishir", "Hemant"]
        assert ritu_ayana["drik_ritu"] in valid_ritus
        
        # Verify ayana values
        valid_ayanas = ["Uttarayana", "Dakshinayana"]
        assert ritu_ayana["drik_ayana"] in valid_ayanas

    @pytest.mark.asyncio
    async def test_panchang_human_readable_times(self, test_client, test_locations, test_dates):
        """Test human readable time formatting."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"],
                "human_readable_times": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify times are in human readable format
        time_fields = ["sunrise", "sunset", "solar_noon", "moonrise", "moonset"]
        
        for field in time_fields:
            if data.get(field):
                time_value = data[field]
                # Should be in format like "6:12 AM" or "7:16 PM"
                assert isinstance(time_value, str)
                assert any(x in time_value for x in ["AM", "PM"])

    @pytest.mark.asyncio
    async def test_panchang_different_ayanamshas(self, test_client, test_locations, test_dates):
        """Test different ayanamsha systems."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        ayanamshas = ["LAHIRI", "RAMAN", "KP", "KRISHNAMURTI"]
        
        for ayanamsha in ayanamshas:
            response = await test_client.get(
                "/v1/panchang",
                params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": mumbai["timezone_offset"],
                    "ayanamsha": ayanamsha
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            
            # Basic validation for each ayanamsha
            assert "tithi" in data
            assert "nakshatra" in data
            assert "ayanamsha" in data
            
            # Verify ayanamsha is correctly set
            assert data["ayanamsha"] == ayanamsha

    @pytest.mark.asyncio
    async def test_panchang_post_method(self, test_client, sample_api_requests):
        """Test POST method for panchang endpoint."""
        request_data = sample_api_requests["panchang"]
        
        response = await test_client.post("/v1/panchang", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify same response structure as GET
        required_fields = ["tithi", "nakshatra", "yoga", "karana"]
        for field in required_fields:
            assert field in data

    @pytest.mark.asyncio
    async def test_panchang_personalized(self, test_client, test_locations, test_dates):
        """Test personalized panchang endpoint."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchang/personalized",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"],
                "birth_date": "1990-01-01",
                "birth_time": "12:00:00"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should include transit information
        assert "transits" in data or "personalized_data" in data

    @pytest.mark.asyncio
    async def test_panchang_edge_cases(self, test_client, test_locations):
        """Test edge cases and boundary conditions."""
        mumbai = test_locations["mumbai"]
        
        # Test leap year date
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2024-02-29",  # Leap year
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        assert response.status_code == 200
        
        # Test midnight
        response = await test_client.get(
            "/v1/panchang", 
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "00:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        assert response.status_code == 200
        
        # Test noon
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_panchang_validation_errors(self, test_client):
        """Test validation and error handling."""
        
        # Test invalid latitude
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": 91.0,  # Invalid latitude
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            }
        )
        assert response.status_code == 422
        
        # Test invalid longitude
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": 19.0760,
                "longitude": 181.0,  # Invalid longitude
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            }
        )
        assert response.status_code == 422
        
        # Test invalid date format
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": 19.0760,
                "longitude": 72.8777,
                "date": "25-07-2025",  # Invalid format
                "time": "12:00:00",
                "timezone_offset": 5.5
            }
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_panchang_performance(self, test_client, test_locations, test_dates, performance_benchmarks):
        """Test panchang API performance."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        benchmark = performance_benchmarks["core_apis"]["panchang"]
        
        start_time = datetime.now()
        
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds()
        
        assert response.status_code == 200
        assert response_time < benchmark["max_time"], f"Response time {response_time}s exceeds max {benchmark['max_time']}s"
        
        # Log performance for monitoring
        print(f"Panchang API response time: {response_time:.3f}s (target: {benchmark['target_time']}s)")

    @pytest.mark.asyncio
    async def test_panchang_multiple_locations(self, test_client, test_locations, test_dates):
        """Test panchang calculations for multiple global locations."""
        test_date = test_dates["current_test"]
        
        for location_name, location in test_locations.items():
            response = await test_client.get(
                "/v1/panchang",
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": location["timezone_offset"]
                }
            )
            
            assert response.status_code == 200, f"Failed for location: {location_name}"
            data = response.json()
            
            # Verify basic calculations work for all locations
            assert "tithi" in data
            assert "nakshatra" in data
            assert "sunrise" in data
            assert "sunset" in data
            
            print(f"✅ Panchang calculation successful for {location_name}")

    @pytest.mark.asyncio
    async def test_panchang_consistency(self, test_client, test_locations, test_dates):
        """Test consistency of panchang calculations."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Make same request multiple times
        responses = []
        for _ in range(3):
            response = await test_client.get(
                "/v1/panchang",
                params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": mumbai["timezone_offset"]
                }
            )
            assert response.status_code == 200
            responses.append(response.json())
        
        # Verify all responses are identical
        first_response = responses[0]
        for response in responses[1:]:
            assert response["tithi"] == first_response["tithi"]
            assert response["nakshatra"] == first_response["nakshatra"]
            assert response["yoga"] == first_response["yoga"]
            assert response["karana"] == first_response["karana"] 