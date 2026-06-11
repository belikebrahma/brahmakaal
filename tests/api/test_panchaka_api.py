"""
Enhanced Panchaka Periods API Tests
Comprehensive testing for the 24-hour panchaka period functionality
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any


class TestPanchakaAPI:
    """Test suite for Enhanced Panchaka Periods API endpoint."""

    @pytest.mark.asyncio
    async def test_panchaka_basic_functionality(self, test_client, test_locations, test_dates):
        """Test basic panchaka periods functionality."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Verify response structure
        required_fields = [
            "date", "total_periods", "panchaka_periods", 
            "current_period", "next_favorable_period", "summary"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Verify we have 24 periods (hourly breakdown)
        assert data["total_periods"] == 24
        assert len(data["panchaka_periods"]) == 24

    @pytest.mark.asyncio
    async def test_panchaka_period_types(self, test_client, test_locations, test_dates):
        """Test all panchaka period types are properly represented."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Expected panchaka types
        expected_types = ["Mrityu Panchaka", "Agni Panchaka", "Raja Panchaka", 
                         "Chora Panchaka", "Roga Panchaka", "Good Muhurta"]
        
        # Check that periods contain valid types
        period_types = [period["type"] for period in data["panchaka_periods"]]
        
        for period_type in period_types:
            assert period_type in expected_types, f"Unknown panchaka type: {period_type}"
        
        # Verify we have at least some Good Muhurta periods
        good_periods = [p for p in data["panchaka_periods"] if p["type"] == "Good Muhurta"]
        assert len(good_periods) > 0, "No Good Muhurta periods found"

    @pytest.mark.asyncio
    async def test_panchaka_period_structure(self, test_client, test_locations, test_dates):
        """Test individual panchaka period structure."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Check structure of each period
        for period in data["panchaka_periods"]:
            required_period_fields = [
                "hour", "type", "start_time", "end_time", 
                "duration_minutes", "description", "recommended_activities"
            ]
            
            for field in required_period_fields:
                assert field in period, f"Missing field '{field}' in period"
            
            # Verify hour is valid (0-23)
            assert 0 <= period["hour"] <= 23
            
            # Verify duration is reasonable (around 60 minutes for hourly)
            assert 45 <= period["duration_minutes"] <= 75

    @pytest.mark.asyncio
    async def test_panchaka_current_period(self, test_client, test_locations, test_dates):
        """Test current period detection."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": "14:30:00",  # Specific time for testing
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify current period structure
        current_period = data["current_period"]
        assert "type" in current_period
        assert "start_time" in current_period
        assert "end_time" in current_period
        assert "time_remaining" in current_period
        
        # Verify current period corresponds to 14:30 (hour 14)
        assert current_period["hour"] == 14

    @pytest.mark.asyncio
    async def test_panchaka_next_favorable_period(self, test_client, test_locations, test_dates):
        """Test next favorable period detection."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Verify next favorable period
        next_favorable = data["next_favorable_period"]
        
        if next_favorable:  # May be None if current period is already favorable
            assert "type" in next_favorable
            assert next_favorable["type"] == "Good Muhurta"
            assert "start_time" in next_favorable
            assert "time_until_start" in next_favorable

    @pytest.mark.asyncio
    async def test_panchaka_summary_statistics(self, test_client, test_locations, test_dates):
        """Test panchaka summary and statistics."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Verify summary structure
        summary = data["summary"]
        required_summary_fields = [
            "total_periods", "favorable_hours", "unfavorable_hours",
            "neutral_hours", "favorable_percentage", "day_quality"
        ]
        
        for field in required_summary_fields:
            assert field in summary, f"Missing summary field: {field}"
        
        # Verify percentages are valid
        assert 0 <= summary["favorable_percentage"] <= 100
        
        # Verify hours add up to 24
        total_hours = summary["favorable_hours"] + summary["unfavorable_hours"] + summary["neutral_hours"]
        assert total_hours == 24

    @pytest.mark.asyncio
    async def test_panchaka_timezone_handling(self, test_client, test_locations, test_dates):
        """Test timezone handling in panchaka periods."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Test with timezone offset
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Verify times include timezone offset
        first_period = data["panchaka_periods"][0]
        
        # Time should include timezone indication
        assert "+05:30" in first_period["start_time"] or "+0530" in first_period["start_time"]

    @pytest.mark.asyncio
    async def test_panchaka_different_dates(self, test_client, test_locations, test_dates):
        """Test panchaka periods for different dates."""
        mumbai = test_locations["mumbai"]
        
        for date_key, test_date in test_dates.items():
            response = await test_client.get(
                "/v1/panchaka-periods",
                params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": mumbai["timezone_offset"]
                }
            )
            
            assert response.status_code == 200, f"Failed for date: {date_key}"
            data = response.json()
            
            # Verify basic structure for each date
            assert "panchaka_periods" in data
            assert len(data["panchaka_periods"]) == 24
            
            print(f"✅ Panchaka periods calculation successful for {date_key}")

    @pytest.mark.asyncio
    async def test_panchaka_performance(self, test_client, test_locations, test_dates, performance_benchmarks):
        """Test panchaka API performance."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        benchmark = performance_benchmarks["advanced_apis"]["panchaka_periods"]
        
        start_time = datetime.now()
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        print(f"Panchaka API response time: {response_time:.3f}s (target: {benchmark['target_time']}s)")

    @pytest.mark.asyncio
    async def test_panchaka_edge_cases(self, test_client, test_locations):
        """Test panchaka periods edge cases."""
        mumbai = test_locations["mumbai"]
        
        # Test midnight
        response = await test_client.get(
            "/v1/panchaka-periods",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "00:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        assert response.status_code == 200
        
        # Test near midnight
        response = await test_client.get(
            "/v1/panchaka-periods",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "23:59:59",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_panchaka_validation_errors(self, test_client):
        """Test panchaka periods validation and error handling."""
        
        # Test missing required parameters
        response = await test_client.get("/v1/panchaka-periods")
        assert response.status_code == 422
        
        # Test invalid coordinates
        response = await test_client.get(
            "/v1/panchaka-periods",
            params={
                "latitude": 91.0,  # Invalid
                "longitude": 72.8777,
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": 5.5
            }
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_panchaka_multiple_locations(self, test_client, test_locations, test_dates):
        """Test panchaka periods for multiple global locations."""
        test_date = test_dates["current_test"]
        
        for location_name, location in test_locations.items():
            response = await test_client.get(
                "/v1/panchaka-periods",
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
            assert len(data["panchaka_periods"]) == 24
            assert "summary" in data
            
            print(f"✅ Panchaka periods calculation successful for {location_name}")

    @pytest.mark.asyncio
    async def test_panchaka_activity_recommendations(self, test_client, test_locations, test_dates):
        """Test activity recommendations in panchaka periods."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        response = await test_client.get(
            "/v1/panchaka-periods",
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
        
        # Verify activity recommendations exist
        for period in data["panchaka_periods"]:
            assert "recommended_activities" in period
            assert isinstance(period["recommended_activities"], list)
            
            # Good Muhurta periods should have positive recommendations
            if period["type"] == "Good Muhurta":
                activities = period["recommended_activities"]
                assert len(activities) > 0, "Good Muhurta should have recommended activities" 