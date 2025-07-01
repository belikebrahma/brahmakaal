#!/usr/bin/env python3
"""
Brahmakaal API Test Script
Tests the Phase 3 Enterprise API endpoints
"""

import asyncio
import json
import time
from datetime import datetime, date
import httpx

API_BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 TESTING BRAHMAKAAL ENTERPRISE API")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Root endpoint
        print("\n🧪 Test 1: Root endpoint")
        try:
            response = await client.get(f"{API_BASE_URL}/")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Service: {data['service']}")
                print(f"Version: {data['version']}")
                print("✅ Root endpoint: PASSED")
            else:
                print("❌ Root endpoint: FAILED")
        except Exception as e:
            print(f"❌ Root endpoint error: {e}")
        
        # Test 2: Health check
        print("\n🧪 Test 2: Health check")
        try:
            response = await client.get(f"{API_BASE_URL}/v1/health")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Health Status: {data['status']}")
                print(f"Database: {'✅' if data['database_connected'] else '❌'}")
                print(f"Cache: {'✅' if data['cache_connected'] else '❌'}")
                print(f"Ephemeris: {'✅' if data['ephemeris_loaded'] else '❌'}")
                print("✅ Health check: PASSED")
            else:
                print("❌ Health check: FAILED")
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        # Test 3: Panchang calculation (GET)
        print("\n🧪 Test 3: Panchang calculation (GET)")
        try:
            # Mumbai coordinates
            params = {
                "lat": 19.0760,
                "lon": 72.8777,
                "date": "2024-01-01"
            }
            response = await client.get(f"{API_BASE_URL}/v1/panchang", params=params)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Tithi: {data['tithi']} ({data['tithi_name']})")
                print(f"Nakshatra: {data['nakshatra']}")
                print(f"Calculation Time: {data['calculation_time_ms']}ms")
                print("✅ Panchang GET: PASSED")
            else:
                print(f"❌ Panchang GET: FAILED - {response.text}")
        except Exception as e:
            print(f"❌ Panchang GET error: {e}")
        
        # Test 4: Panchang calculation (POST)
        print("\n🧪 Test 4: Panchang calculation (POST)")
        try:
            panchang_request = {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "date": "2024-01-01",
                "time": "12:00:00",
                "elevation": 0.0,
                "ayanamsha": "LAHIRI",
                "timezone_offset": 5.5
            }
            response = await client.post(f"{API_BASE_URL}/v1/panchang", json=panchang_request)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Location: Delhi")
                print(f"Tithi: {data['tithi']} ({data['tithi_name']})")
                print(f"Nakshatra: {data['nakshatra']}")
                print(f"Sunrise: {data['sunrise']}")
                print("✅ Panchang POST: PASSED")
            else:
                print(f"❌ Panchang POST: FAILED - {response.text}")
        except Exception as e:
            print(f"❌ Panchang POST error: {e}")
        
        # Test 5: Muhurta types
        print("\n🧪 Test 5: Muhurta types")
        try:
            response = await client.get(f"{API_BASE_URL}/v1/muhurta/types")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Available types: {list(data.keys())}")
                print("✅ Muhurta types: PASSED")
            else:
                print("❌ Muhurta types: FAILED")
        except Exception as e:
            print(f"❌ Muhurta types error: {e}")
        
        # Test 6: Festival regions
        print("\n🧪 Test 6: Festival regions")
        try:
            response = await client.get(f"{API_BASE_URL}/v1/festivals/regions")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Available regions: {len(data)} regions")
                print("✅ Festival regions: PASSED")
            else:
                print("❌ Festival regions: FAILED")
        except Exception as e:
            print(f"❌ Festival regions error: {e}")
        
        # Test 7: Festivals (GET)
        print("\n🧪 Test 7: Festivals (GET)")
        try:
            params = {
                "year": 2024,
                "month": 10,
                "regions": "all_india",
                "categories": "major"
            }
            response = await client.get(f"{API_BASE_URL}/v1/festivals", params=params)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Festivals found: {data['total_festivals']}")
                if data['festivals']:
                    print(f"First festival: {data['festivals'][0]['name']} on {data['festivals'][0]['date']}")
                print("✅ Festivals GET: PASSED")
            else:
                print(f"❌ Festivals GET: FAILED - {response.text}")
        except Exception as e:
            print(f"❌ Festivals GET error: {e}")
        
        # Test 8: Ayanamsha comparison
        print("\n🧪 Test 8: Ayanamsha comparison")
        try:
            params = {"date": "2024-01-01"}
            response = await client.get(f"{API_BASE_URL}/v1/ayanamsha", params=params)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                lahiri = data['ayanamsha_values'].get('LAHIRI', 0)
                print(f"Lahiri Ayanamsha: {lahiri:.6f}°")
                print(f"Systems compared: {len(data['ayanamsha_values'])}")
                print("✅ Ayanamsha comparison: PASSED")
            else:
                print(f"❌ Ayanamsha comparison: FAILED - {response.text}")
        except Exception as e:
            print(f"❌ Ayanamsha comparison error: {e}")
        
        # Test 9: API Documentation
        print("\n🧪 Test 9: API Documentation")
        try:
            response = await client.get(f"{API_BASE_URL}/docs")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ API Documentation: ACCESSIBLE")
            else:
                print("❌ API Documentation: FAILED")
        except Exception as e:
            print(f"❌ API Documentation error: {e}")

def main():
    """Run the API tests"""
    print("Starting API tests...")
    print("Make sure the API server is running on http://localhost:8000")
    print("Use: python start_api.py in another terminal")
    print("-" * 50)
    
    asyncio.run(test_api_endpoints())
    
    print("\n" + "=" * 50)
    print("🎉 API TESTING COMPLETE!")
    print("📖 View full documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 