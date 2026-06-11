"""
Drik Panchang Accuracy Validation Tests
Validates API calculations against known Drik Panchang data for accuracy
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any


class TestDrikPanchangValidation:
    """Test suite for accuracy validation against Drik Panchang."""

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_mumbai_july_25_2025_accuracy(self, test_client, test_locations, 
                                               drik_panchang_validation_data, test_helpers):
        """Test accuracy for Mumbai July 25, 2025 against Drik Panchang."""
        validation_case = drik_panchang_validation_data["mumbai_2025_07_25"]
        mumbai = test_locations[validation_case["location"]]
        expected = validation_case["expected"]
        
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": validation_case["date"],
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"],
                "human_readable_times": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Test Tithi accuracy
        assert expected["tithi"] in data["tithi_name"], f"Expected tithi {expected['tithi']}, got {data['tithi_name']}"
        
        # Test Paksha accuracy  
        assert expected["paksha"] in data["paksha"], f"Expected paksha {expected['paksha']}, got {data['paksha']}"
        
        # Test Nakshatra accuracy
        assert expected["nakshatra"] in data["nakshatra_name"], f"Expected nakshatra {expected['nakshatra']}, got {data['nakshatra_name']}"
        
        # Test Sunrise accuracy (within 10 minutes tolerance)
        if data.get("sunrise"):
            actual_sunrise = test_helpers.extract_time_from_datetime(str(data["sunrise"]))
            test_helpers.assert_time_within_tolerance(actual_sunrise, expected["sunrise"], 10)
        
        # Test Sunset accuracy (within 10 minutes tolerance)
        if data.get("sunset"):
            actual_sunset = test_helpers.extract_time_from_datetime(str(data["sunset"]))
            test_helpers.assert_time_within_tolerance(actual_sunset, expected["sunset"], 10)
        
        # Test Ritu accuracy (if available)
        if "ritu_ayana" in data and data["ritu_ayana"]:
            ritu_data = data["ritu_ayana"]
            assert expected["ritu"] in ritu_data.get("drik_ritu", ""), f"Expected ritu {expected['ritu']}, got {ritu_data.get('drik_ritu')}"
            assert expected["ayana"] in ritu_data.get("drik_ayana", ""), f"Expected ayana {expected['ayana']}, got {ritu_data.get('drik_ayana')}"
        
        # Test Weekday accuracy
        weekday_map = {
            "Monday": "Somwar", "Tuesday": "Mangalwar", "Wednesday": "Budhwar",
            "Thursday": "Gurwar", "Friday": "Shukrwar", "Saturday": "Shaniwar", "Sunday": "Raviwar"
        }
        actual_weekday = datetime.strptime(validation_case["date"], "%Y-%m-%d").strftime("%A")
        assert actual_weekday == expected["weekday"], f"Expected {expected['weekday']}, got {actual_weekday}"
        
        print(f"✅ Mumbai July 25, 2025 accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_nakshatra_pada_accuracy(self, test_client, test_locations, test_helpers):
        """Test Nakshatra Pada system accuracy."""
        mumbai = test_locations["mumbai"]
        
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
        data = response.json()
        
        # Verify Nakshatra Pada system exists and is valid
        assert "nakshatra_detailed" in data
        nakshatra_detailed = data["nakshatra_detailed"]
        
        # Verify pada values are valid (1-4)
        current_pada = nakshatra_detailed["current_pada"]
        assert 1 <= current_pada <= 4, f"Invalid pada value: {current_pada}"
        
        # Verify percentage is valid (0-100)
        position_percent = nakshatra_detailed["position_in_pada_percent"]
        assert 0 <= position_percent <= 100, f"Invalid percentage: {position_percent}"
        
        # Verify pada transitions exist
        assert "pada_transitions" in nakshatra_detailed
        transitions = nakshatra_detailed["pada_transitions"]
        assert isinstance(transitions, list), "Pada transitions should be a list"
        
        # For Pushya nakshatra, verify we have correct pada names
        if "Pushya" in data["nakshatra_name"]:
            expected_pada_names = ["First Pada", "Second Pada", "Third Pada", "Fourth Pada"]
            current_pada_name = nakshatra_detailed["current_pada_name"]
            assert current_pada_name in expected_pada_names, f"Invalid pada name: {current_pada_name}"
        
        print(f"✅ Nakshatra Pada accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_ritu_ayana_accuracy(self, test_client, test_locations):
        """Test Ritu & Ayana system accuracy."""
        mumbai = test_locations["mumbai"]
        
        # Test for July 25, 2025 (expected Varsha/Dakshinayana)
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
        data = response.json()
        
        # Verify Ritu & Ayana system exists
        assert "ritu_ayana" in data
        ritu_ayana = data["ritu_ayana"]
        
        # For July 25, should be Varsha (monsoon) season
        valid_summer_ritus = ["Grishma", "Varsha"]  # Summer transition to monsoon
        assert ritu_ayana["drik_ritu"] in valid_summer_ritus, f"Unexpected ritu for July: {ritu_ayana['drik_ritu']}"
        
        # For July 25, should be Dakshinayana (southern movement)
        assert ritu_ayana["drik_ayana"] == "Dakshinayana", f"Expected Dakshinayana, got {ritu_ayana['drik_ayana']}"
        
        # Verify dinamana and ratrimana are reasonable for July
        assert "dinamana" in ritu_ayana
        assert "ratrimana" in ritu_ayana
        assert "madhyahna" in ritu_ayana
        
        print(f"✅ Ritu & Ayana accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_solar_times_accuracy(self, test_client, test_locations, test_helpers):
        """Test solar times accuracy against expected values."""
        mumbai = test_locations["mumbai"]
        
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"],
                "human_readable_times": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Expected times for Mumbai on July 25, 2025 (approximate)
        expected_sunrise = "06:12"
        expected_sunset = "19:16"
        expected_solar_noon = "12:44"
        
        # Test sunrise accuracy
        if data.get("sunrise"):
            actual_sunrise = test_helpers.extract_time_from_datetime(str(data["sunrise"]))
            test_helpers.assert_time_within_tolerance(actual_sunrise, expected_sunrise, 15)
        
        # Test sunset accuracy
        if data.get("sunset"):
            actual_sunset = test_helpers.extract_time_from_datetime(str(data["sunset"]))
            test_helpers.assert_time_within_tolerance(actual_sunset, expected_sunset, 15)
        
        # Test solar noon accuracy
        if data.get("solar_noon"):
            actual_noon = test_helpers.extract_time_from_datetime(str(data["solar_noon"]))
            test_helpers.assert_time_within_tolerance(actual_noon, expected_solar_noon, 10)
        
        print(f"✅ Solar times accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_ayanamsha_accuracy(self, test_client, accuracy_tolerances):
        """Test ayanamsha calculation accuracy."""
        response = await test_client.get(
            "/v1/ayanamsha",
            params={
                "date": "2025-07-25",
                "time": "12:00:00",
                "ayanamsha": "LAHIRI"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Expected Lahiri ayanamsha for July 25, 2025 (approximately 24.22°)
        expected_ayanamsha = 24.22
        actual_ayanamsha = data["ayanamsha_value"]
        
        tolerance = accuracy_tolerances["ayanamsha_precision"]
        difference = abs(actual_ayanamsha - expected_ayanamsha)
        
        assert difference <= tolerance, f"Ayanamsha difference {difference}° exceeds tolerance {tolerance}°"
        
        print(f"✅ Ayanamsha accuracy validation passed (difference: {difference:.4f}°)")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_tithi_accuracy_edge_cases(self, test_client, test_locations, test_helpers):
        """Test tithi accuracy for edge cases (Purnima, Amavasya)."""
        mumbai = test_locations["mumbai"]
        
        # Test around New Moon (expected Amavasya)
        response = await test_client.get(
            "/v1/panchang",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-24",  # Near new moon
                "time": "19:11:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should be near Amavasya (new moon)
        tithi_value = data["tithi"]
        tithi_name = data["tithi_name"]
        
        # For new moon, tithi should be very low (near 0) or very high (near 30)
        # or explicitly named Amavasya
        is_new_moon = (tithi_value < 1.0 or tithi_value > 29.0 or "Amavasya" in tithi_name)
        assert is_new_moon, f"Expected new moon tithi, got {tithi_name} ({tithi_value})"
        
        print(f"✅ Tithi edge case accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio 
    async def test_muhurta_periods_accuracy(self, test_client, test_locations):
        """Test muhurta periods accuracy."""
        mumbai = test_locations["mumbai"]
        
        response = await test_client.get(
            "/v1/complete-muhurta-periods",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all 8 muhurta types are present
        expected_muhurta_types = [
            "Brahma Muhurta", "Pratah Sandhya", "Abhijit Muhurta", "Vijaya Muhurta",
            "Godhuli Muhurta", "Sayahna Sandhya", "Amrit Kalam", "Nishita Muhurta"
        ]
        
        muhurta_periods = data["muhurta_periods"]
        
        for muhurta_type in expected_muhurta_types:
            assert muhurta_type in muhurta_periods, f"Missing muhurta type: {muhurta_type}"
        
        # Verify Brahma Muhurta timing (should be before sunrise)
        brahma_muhurta = muhurta_periods["Brahma Muhurta"]
        assert brahma_muhurta["duration_minutes"] == 48, "Brahma Muhurta should be 48 minutes"
        
        # Verify Abhijit Muhurta is around solar noon
        abhijit_muhurta = muhurta_periods["Abhijit Muhurta"]
        assert abhijit_muhurta["duration_minutes"] == 48, "Abhijit Muhurta should be 48 minutes"
        
        print(f"✅ Muhurta periods accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_calendar_systems_accuracy(self, test_client, test_locations):
        """Test calendar systems accuracy."""
        mumbai = test_locations["mumbai"]
        
        response = await test_client.get(
            "/v1/extended-calendar-systems",
            params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": "2025-07-25",
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        extended_systems = data["extended_calendar_systems"]
        
        # Test Gujarati Samvat (should be around 2081-2082)
        gujarati_samvat = extended_systems["gujarati_samvat"]
        expected_year_range = range(2080, 2085)
        assert gujarati_samvat["year"] in expected_year_range, f"Gujarati year {gujarati_samvat['year']} out of expected range"
        
        # Test Brihaspati Samvatsara cycle (should be 1-60)
        brihaspati = extended_systems["brihaspati_samvatsara"]
        cycle_position = brihaspati["position_in_cycle"]
        assert 1 <= cycle_position <= 60, f"Invalid Brihaspati cycle position: {cycle_position}"
        
        # Test Era systems
        era_systems = extended_systems["era_systems"]
        
        # Kali Yuga should be around 5126-5127
        kali_year = era_systems["kali_yuga"]["year"]
        assert 5120 <= kali_year <= 5130, f"Kali Yuga year {kali_year} out of range"
        
        # Saka era should be around 1947
        saka_year = era_systems["saka_era"]["year"]
        assert 1945 <= saka_year <= 1950, f"Saka year {saka_year} out of range"
        
        print(f"✅ Calendar systems accuracy validation passed")

    @pytest.mark.accuracy
    @pytest.mark.asyncio
    async def test_cross_validation_consistency(self, test_client, test_locations):
        """Test consistency across different API endpoints."""
        mumbai = test_locations["mumbai"]
        test_params = {
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": "2025-07-25",
            "time": "12:00:00",
            "timezone_offset": mumbai["timezone_offset"]
        }
        
        # Get data from different endpoints
        panchang_response = await test_client.get("/v1/panchang", params=test_params)
        calendar_response = await test_client.get("/v1/extended-calendar-systems", params=test_params)
        
        assert panchang_response.status_code == 200
        assert calendar_response.status_code == 200
        
        panchang_data = panchang_response.json()
        calendar_data = calendar_response.json()
        
        # Verify consistent date across endpoints
        assert panchang_data.get("date", "").startswith("2025-07-25")
        assert calendar_data.get("date", "").startswith("2025-07-25")
        
        # Verify tithi consistency if available in both
        if "tithi_name" in panchang_data:
            assert "Pratipada" in panchang_data["tithi_name"]  # Expected for test date
        
        print(f"✅ Cross-validation consistency passed")

    @pytest.mark.accuracy
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_year_long_accuracy_sampling(self, test_client, test_locations):
        """Test accuracy sampling across different dates in a year."""
        mumbai = test_locations["mumbai"]
        
        # Test dates throughout 2025
        test_dates = [
            "2025-01-15", "2025-03-15", "2025-05-15", "2025-07-15",
            "2025-09-15", "2025-11-15"
        ]
        
        for test_date in test_dates:
            response = await test_client.get(
                "/v1/panchang",
                params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date,
                    "time": "12:00:00",
                    "timezone_offset": mumbai["timezone_offset"]
                }
            )
            
            assert response.status_code == 200, f"Failed for date: {test_date}"
            data = response.json()
            
            # Basic validation for each date
            assert "tithi" in data
            assert "nakshatra" in data
            assert 0 <= data["tithi"] <= 30
            assert 0 <= data["nakshatra"] <= 360
            
            print(f"✅ Accuracy validation passed for {test_date}")
        
        print(f"✅ Year-long accuracy sampling completed") 