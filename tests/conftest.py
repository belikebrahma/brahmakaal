"""
Pytest Configuration and Fixtures for Brahmakaal API Testing Suite
Provides common fixtures, test data, and configuration for all tests
"""

import pytest
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaal_engine.kaal import Kaal
from kaal_engine.api.app import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def kaal_engine():
    """Initialize Kaal engine for testing."""
    return Kaal("de421.bsp")  # Use smaller ephemeris file for testing


@pytest.fixture
async def test_client():
    """Create ASGI test client (no live server needed)."""
    from httpx._transports.asgi import ASGITransport
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver", timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def test_locations():
    """Standard test locations with known characteristics."""
    return {
        "mumbai": {
            "name": "Mumbai",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "timezone_offset": 5.5,
            "elevation": 14
        },
        "delhi": {
            "name": "Delhi", 
            "latitude": 28.6139,
            "longitude": 77.2090,
            "timezone_offset": 5.5,
            "elevation": 216
        },
        "london": {
            "name": "London",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "timezone_offset": 0.0,
            "elevation": 35
        },
        "new_york": {
            "name": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone_offset": -5.0,
            "elevation": 10
        }
    }


@pytest.fixture(scope="session")
def test_dates():
    """Standard test dates for validation."""
    return {
        "summer_solstice_2025": {
            "date": "2025-06-21",
            "time": "12:00:00",
            "description": "Summer Solstice 2025"
        },
        "winter_solstice_2025": {
            "date": "2025-12-21", 
            "time": "12:00:00",
            "description": "Winter Solstice 2025"
        },
        "diwali_2025": {
            "date": "2025-11-01",
            "time": "18:00:00",
            "description": "Diwali 2025 (approximate)"
        },
        "current_test": {
            "date": "2025-07-25",
            "time": "12:00:00", 
            "description": "Current test date"
        },
        "new_moon": {
            "date": "2025-07-24",
            "time": "19:11:00",
            "description": "New Moon July 2025"
        },
        "full_moon": {
            "date": "2025-08-09",
            "time": "07:55:00",
            "description": "Full Moon August 2025"
        }
    }


@pytest.fixture(scope="session")
def drik_panchang_validation_data():
    """Known validation data from Drik Panchang for accuracy testing."""
    return {
        "mumbai_2025_07_25": {
            "date": "2025-07-25",
            "location": "mumbai",
            "expected": {
                "tithi": "Pratipada",
                "paksha": "Shukla",
                "nakshatra": "Pushya",
                "sunrise": "06:12",  # Approximate time
                "sunset": "19:16",   # Approximate time
                "solar_noon": "12:44",
                "ritu": "Varsha",
                "ayana": "Dakshinayana",
                "weekday": "Friday"
            }
        },
        "delhi_2025_12_21": {
            "date": "2025-12-21",
            "location": "delhi", 
            "expected": {
                "tithi": "Ekadashi",
                "nakshatra": "Uttara Ashadha",
                "sunrise": "07:09",
                "sunset": "17:29",
                "ritu": "Shishir",
                "ayana": "Uttarayana"
            }
        }
    }


@pytest.fixture(scope="session")
def performance_benchmarks():
    """Performance benchmarks for API response times."""
    return {
        "core_apis": {
            "panchang": {"max_time": 3.0, "target_time": 2.0},
            "horoscope": {"max_time": 5.0, "target_time": 3.0},
            "muhurta": {"max_time": 10.0, "target_time": 5.0},
            "transits": {"max_time": 2.0, "target_time": 1.0},
            "ayanamsha": {"max_time": 1.0, "target_time": 0.5}
        },
        "advanced_apis": {
            "panchaka_periods": {"max_time": 0.1, "target_time": 0.06},
            "udaya_lagna_periods": {"max_time": 0.1, "target_time": 0.05},
            "complete_muhurta_periods": {"max_time": 0.1, "target_time": 0.06},
            "inauspicious_periods": {"max_time": 0.1, "target_time": 0.05},
            "extended_calendar_systems": {"max_time": 0.1, "target_time": 0.03}
        }
    }


@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


@pytest.fixture
def sample_api_requests():
    """Sample API request data for testing."""
    return {
        "panchang": {
            "latitude": 19.0760,
            "longitude": 72.8777,
            "date": "2025-07-25",
            "time": "12:00:00",
            "timezone_offset": 5.5,
            "ayanamsha": "LAHIRI",
            "human_readable_times": True
        },
        "horoscope": {
            "latitude": 19.0760,
            "longitude": 72.8777,
            "date": "1990-01-01",
            "time": "12:00:00",
            "timezone_offset": 5.5,
            "ayanamsha": "LAHIRI"
        },
        "muhurta": {
            "latitude": 19.0760,
            "longitude": 72.8777,
            "date": "2025-07-25",
            "activity": "wedding",
            "duration_hours": 2,
            "timezone_offset": 5.5
        }
    }


@pytest.fixture(scope="session")
def accuracy_tolerances():
    """Acceptable tolerances for accuracy testing."""
    return {
        "time_difference_minutes": 10,  # ±10 minutes for time calculations
        "coordinate_precision": 0.01,   # ±0.01 degrees for coordinates
        "percentage_precision": 1.0,    # ±1% for percentage calculations
        "ayanamsha_precision": 0.001    # ±0.001 degrees for ayanamsha
    }


@pytest.fixture
def mock_server_data():
    """Mock server response data for testing."""
    return {
        "success_response": {
            "status": "success",
            "data": {},
            "timestamp": datetime.utcnow().isoformat()
        },
        "error_response": {
            "status": "error",
            "message": "Test error",
            "code": 400
        }
    }


class TestHelpers:
    """Helper utilities for testing."""
    
    @staticmethod
    def assert_time_within_tolerance(actual: str, expected: str, tolerance_minutes: int = 10):
        """Assert that actual time is within tolerance of expected time."""
        from datetime import datetime
        
        actual_time = datetime.strptime(actual, "%H:%M").time()
        expected_time = datetime.strptime(expected, "%H:%M").time()
        
        # Convert to minutes for comparison
        actual_minutes = actual_time.hour * 60 + actual_time.minute
        expected_minutes = expected_time.hour * 60 + expected_time.minute
        
        difference = abs(actual_minutes - expected_minutes)
        assert difference <= tolerance_minutes, f"Time difference {difference} minutes exceeds tolerance {tolerance_minutes}"
    
    @staticmethod
    def assert_api_response_structure(response_data: Dict[str, Any], required_fields: List[str]):
        """Assert that API response has required structure."""
        for field in required_fields:
            assert field in response_data, f"Required field '{field}' missing from response"
    
    @staticmethod
    def extract_time_from_datetime(datetime_str: str) -> str:
        """Extract HH:MM format from datetime string."""
        try:
            # Handle different datetime formats
            if "T" in datetime_str:
                time_part = datetime_str.split("T")[1]
            else:
                time_part = datetime_str.split(" ")[1]
            
            # Extract HH:MM
            return time_part[:5]
        except (IndexError, ValueError):
            return datetime_str


@pytest.fixture
def test_helpers():
    """Test helper utilities."""
    return TestHelpers


# Pytest configuration
def pytest_configure(config):
    """Pytest configuration."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "accuracy: marks tests as accuracy validation tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Mark tests in accuracy/ as accuracy tests
        if "accuracy" in str(item.fspath):
            item.add_marker(pytest.mark.accuracy)
        
        # Mark tests in performance/ as performance tests
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        
        # Mark tests in integration/ as integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration) 