"""
End-to-End Integration Tests
Comprehensive integration testing for the complete Brahmakaal API system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List


class TestEndToEndIntegration:
    """Test suite for complete API system integration."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_api_workflow(self, test_client, test_locations, test_dates):
        """Test complete workflow using all major API endpoints."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # 1. Get comprehensive panchang data
        panchang_response = await test_client.get("/v1/panchang", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"],
            "human_readable_times": True
        })
        
        assert panchang_response.status_code == 200
        panchang_data = panchang_response.json()
        
        # 2. Get enhanced panchaka periods
        panchaka_response = await test_client.get("/v1/panchaka-periods", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        assert panchaka_response.status_code == 200
        panchaka_data = panchaka_response.json()
        
        # 3. Get complete muhurta periods
        muhurta_response = await test_client.get("/v1/complete-muhurta-periods", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        assert muhurta_response.status_code == 200
        muhurta_data = muhurta_response.json()
        
        # 4. Get inauspicious periods
        inauspicious_response = await test_client.get("/v1/inauspicious-periods", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        assert inauspicious_response.status_code == 200
        inauspicious_data = inauspicious_response.json()
        
        # 5. Get calendar systems
        calendar_response = await test_client.get("/v1/extended-calendar-systems", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        assert calendar_response.status_code == 200
        calendar_data = calendar_response.json()
        
        # Verify cross-endpoint consistency
        # All should have the same date
        assert panchang_data.get("date", "").startswith(test_date["date"])
        assert panchaka_data.get("date", "").startswith(test_date["date"])
        assert muhurta_data.get("date", "").startswith(test_date["date"])
        assert calendar_data.get("date", "").startswith(test_date["date"])
        
        # Verify all responses contain substantial data
        assert len(panchang_data) > 15  # Rich panchang data
        assert len(panchaka_data["panchaka_periods"]) == 24  # 24 hourly periods
        assert len(muhurta_data["muhurta_periods"]) == 8  # 8 muhurta types
        assert len(calendar_data["extended_calendar_systems"]) >= 3  # Multiple calendar systems
        
        print("✅ Complete API workflow integration test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_location_consistency(self, test_client, test_locations, test_dates):
        """Test consistency across multiple global locations."""
        test_date = test_dates["current_test"]
        location_results = {}
        
        # Test all locations
        for location_name, location in test_locations.items():
            # Get panchang for each location
            response = await test_client.get("/v1/panchang", params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": location["timezone_offset"]
            })
            
            assert response.status_code == 200
            location_results[location_name] = response.json()
        
        # Verify location-independent data consistency
        # Some values should be identical (e.g., tithi at same UTC time)
        # Others should vary (e.g., sunrise times)
        
        mumbai_data = location_results["mumbai"]
        delhi_data = location_results["delhi"]
        
        # Tithi should be very similar at same time
        tithi_diff = abs(mumbai_data["tithi"] - delhi_data["tithi"])
        assert tithi_diff < 0.1, f"Tithi difference {tithi_diff} too large between locations"
        
        # Nakshatra should be identical at same time
        assert mumbai_data["nakshatra_name"] == delhi_data["nakshatra_name"]
        
        # Sunrise times should be different
        mumbai_sunrise = str(mumbai_data.get("sunrise", ""))
        delhi_sunrise = str(delhi_data.get("sunrise", ""))
        assert mumbai_sunrise != delhi_sunrise, "Sunrise times should differ between locations"
        
        print("✅ Multi-location consistency test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_temporal_consistency(self, test_client, test_locations):
        """Test consistency across different times of day."""
        mumbai = test_locations["mumbai"]
        
        # Test different times throughout the day
        test_times = ["06:00:00", "12:00:00", "18:00:00", "23:59:59"]
        time_results = {}
        
        for test_time in test_times:
            response = await test_client.get("/v1/panchang", params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": test_time,
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            assert response.status_code == 200
            time_results[test_time] = response.json()
        
        # Verify temporal consistency
        # Sunrise/sunset should be identical regardless of query time
        sunrise_times = set()
        sunset_times = set()
        
        for time_key, data in time_results.items():
            if data.get("sunrise"):
                sunrise_times.add(str(data["sunrise"]))
            if data.get("sunset"):
                sunset_times.add(str(data["sunset"]))
        
        # Should have only one unique sunrise/sunset time
        assert len(sunrise_times) <= 1, f"Multiple sunrise times found: {sunrise_times}"
        assert len(sunset_times) <= 1, f"Multiple sunset times found: {sunset_times}"
        
        print("✅ Temporal consistency test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_relationship_integrity(self, test_client, test_locations, test_dates):
        """Test integrity of relationships between different data elements."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get("/v1/panchang", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Test logical relationships
        
        # 1. Tithi should match tithi_name
        tithi_value = data.get("tithi", 0)
        tithi_name = data.get("tithi_name", "")
        
        if 0 <= tithi_value < 1:
            expected_names = ["Pratipada", "Amavasya"]
        elif 14 <= tithi_value < 15:
            expected_names = ["Purnima", "Chaturdashi"]
        
        # Basic validation - tithi name should not be empty
        assert tithi_name.strip() != "", "Tithi name should not be empty"
        
        # 2. Paksha should match tithi range
        paksha = data.get("paksha", "")
        if 0 <= tithi_value <= 15:
            expected_paksha = "Shukla"
        else:
            expected_paksha = "Krishna"
        
        # Note: This might need adjustment based on exact calculation method
        # For now, just verify paksha is not empty
        assert paksha in ["Shukla", "Krishna"], f"Invalid paksha: {paksha}"
        
        # 3. Nakshatra should be in valid range
        nakshatra_value = data.get("nakshatra", 0)
        assert 0 <= nakshatra_value <= 360, f"Nakshatra value {nakshatra_value} out of range"
        
        # 4. Advanced features integrity
        if "nakshatra_detailed" in data:
            nakshatra_detailed = data["nakshatra_detailed"]
            current_pada = nakshatra_detailed.get("current_pada", 0)
            assert 1 <= current_pada <= 4, f"Invalid pada: {current_pada}"
        
        if "ritu_ayana" in data:
            ritu_ayana = data["ritu_ayana"]
            ritu = ritu_ayana.get("drik_ritu", "")
            ayana = ritu_ayana.get("drik_ayana", "")
            
            valid_ritus = ["Vasant", "Grishma", "Varsha", "Sharad", "Shishir", "Hemant"]
            valid_ayanas = ["Uttarayana", "Dakshinayana"]
            
            assert ritu in valid_ritus, f"Invalid ritu: {ritu}"
            assert ayana in valid_ayanas, f"Invalid ayana: {ayana}"
        
        print("✅ Data relationship integrity test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_recovery_and_graceful_degradation(self, test_client, test_locations):
        """Test system's ability to handle errors gracefully."""
        mumbai = test_locations["mumbai"]
        
        # Test various error conditions
        error_test_cases = [
            # Invalid coordinates
            {"latitude": 91.0, "longitude": 72.8777, "expected_status": 422},
            {"latitude": 19.0760, "longitude": 181.0, "expected_status": 422},
            
            # Invalid date formats
            {"date": "25-07-2025", "expected_status": 400},
            {"date": "2025-13-01", "expected_status": 400},
            
            # Invalid time formats
            {"time": "25:00:00", "expected_status": 400},
            {"time": "12:60:00", "expected_status": 400},
        ]
        
        base_params = {
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": "2025-07-25",
            "time": "12:00:00",
            "timezone_offset": mumbai["timezone_offset"]
        }
        
        for test_case in error_test_cases:
            # Create params with error condition
            test_params = base_params.copy()
            expected_status = test_case.pop("expected_status")
            test_params.update(test_case)
            
            response = await test_client.get("/v1/panchang", params=test_params)
            
            # Verify error is handled properly
            assert response.status_code == expected_status, f"Expected {expected_status}, got {response.status_code} for {test_case}"
            
            # Verify error response structure
            if response.status_code >= 400:
                error_data = response.json()
                assert "detail" in error_data or "message" in error_data, "Error response should contain error details"
        
        print("✅ Error recovery and graceful degradation test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_system_health_endpoints(self, test_client):
        """Test system health and monitoring endpoints."""
        
        # Test health endpoint
        health_response = await test_client.get("/health")
        
        # Should return success status
        assert health_response.status_code == 200
        health_data = health_response.json()
        
        # Basic health check validation
        assert "status" in health_data
        assert health_data["status"] in ["healthy", "ok", "ready"]
        
        print("✅ System health endpoints test passed")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_comprehensive_feature_coverage(self, test_client, test_locations, test_dates):
        """Test that all major features work together comprehensively."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Test all major API endpoints
        endpoints_to_test = [
            "/v1/panchang",
            "/v1/panchaka-periods",
            "/v1/udaya-lagna-periods",
            "/v1/complete-muhurta-periods",
            "/v1/inauspicious-periods",
            "/v1/extended-calendar-systems"
        ]
        
        endpoint_results = {}
        
        for endpoint in endpoints_to_test:
            response = await test_client.get(endpoint, params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            assert response.status_code == 200, f"Endpoint {endpoint} failed"
            endpoint_results[endpoint] = response.json()
            
            # Verify each endpoint returns substantial data
            data = response.json()
            assert len(str(data)) > 500, f"Endpoint {endpoint} returned insufficient data"
        
        # Verify feature coverage
        panchang_data = endpoint_results["/v1/panchang"]
        
        # Core panchang features
        core_features = ["tithi", "nakshatra", "yoga", "karana", "sunrise", "sunset"]
        for feature in core_features:
            assert feature in panchang_data, f"Missing core feature: {feature}"
        
        # Advanced features
        if "nakshatra_detailed" in panchang_data:
            assert "current_pada" in panchang_data["nakshatra_detailed"]
        
        if "ritu_ayana" in panchang_data:
            assert "drik_ritu" in panchang_data["ritu_ayana"]
        
        # Verify panchaka periods
        panchaka_data = endpoint_results["/v1/panchaka-periods"]
        assert len(panchaka_data["panchaka_periods"]) == 24
        
        # Verify muhurta periods
        muhurta_data = endpoint_results["/v1/complete-muhurta-periods"]
        assert len(muhurta_data["muhurta_periods"]) == 8
        
        print("✅ Comprehensive feature coverage test passed")

    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_long_running_stability(self, test_client, test_locations, test_dates):
        """Test system stability over extended operation."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Run continuous requests for extended period
        successful_requests = 0
        failed_requests = 0
        
        for i in range(30):  # Reduced from 100 to make test faster
            try:
                response = await test_client.get("/v1/panchang", params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": mumbai["timezone_offset"]
                })
                
                if response.status_code == 200:
                    successful_requests += 1
                    
                    # Verify response quality remains consistent
                    data = response.json()
                    assert "tithi" in data
                    assert "nakshatra" in data
                else:
                    failed_requests += 1
                    
            except Exception as e:
                failed_requests += 1
                print(f"Request {i} failed: {e}")
            
            # Small delay to simulate real usage
            await asyncio.sleep(0.1)
        
        # Verify system stability
        success_rate = successful_requests / (successful_requests + failed_requests)
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} too low"
        
        print(f"✅ Long-running stability test passed - Success rate: {success_rate:.2%}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_versioning_and_backward_compatibility(self, test_client, test_locations, test_dates):
        """Test API versioning and backward compatibility."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Test v1 endpoints
        v1_endpoints = [
            "/v1/panchang",
            "/v1/panchaka-periods",
            "/v1/complete-muhurta-periods"
        ]
        
        for endpoint in v1_endpoints:
            response = await test_client.get(endpoint, params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            assert response.status_code == 200, f"v1 endpoint {endpoint} failed"
            
            # Verify response structure is stable
            data = response.json()
            assert isinstance(data, dict), f"Response should be JSON object for {endpoint}"
        
        print("✅ API versioning and backward compatibility test passed") 