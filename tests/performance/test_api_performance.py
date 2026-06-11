"""
API Performance Tests
Comprehensive performance testing for all Brahmakaal API endpoints
"""

import pytest
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List
import statistics


class TestAPIPerformance:
    """Test suite for API performance and benchmarking."""

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_panchang_api_performance(self, test_client, test_locations, 
                                          test_dates, performance_benchmarks):
        """Test core panchang API performance."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        benchmark = performance_benchmarks["core_apis"]["panchang"]
        
        # Warm up the API
        await test_client.get("/v1/panchang", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        # Performance test
        response_times = []
        for _ in range(5):
            start_time = time.time()
            
            response = await test_client.get("/v1/panchang", params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            response_times.append(response_time)
        
        # Analyze performance
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        assert avg_time < benchmark["target_time"], f"Average response time {avg_time:.3f}s exceeds target {benchmark['target_time']}s"
        assert max_time < benchmark["max_time"], f"Max response time {max_time:.3f}s exceeds limit {benchmark['max_time']}s"
        
        print(f"Panchang API - Avg: {avg_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_advanced_apis_performance(self, test_client, test_locations, 
                                           test_dates, performance_benchmarks):
        """Test performance of all advanced API endpoints."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        advanced_benchmarks = performance_benchmarks["advanced_apis"]
        
        # Test each advanced API endpoint
        endpoints = [
            ("/v1/panchaka-periods", "panchaka_periods"),
            ("/v1/udaya-lagna-periods", "udaya_lagna_periods"),
            ("/v1/complete-muhurta-periods", "complete_muhurta_periods"),
            ("/v1/inauspicious-periods", "inauspicious_periods"),
            ("/v1/extended-calendar-systems", "extended_calendar_systems")
        ]
        
        for endpoint, benchmark_key in endpoints:
            benchmark = advanced_benchmarks[benchmark_key]
            
            # Warm up
            await test_client.get(endpoint, params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            # Performance test
            response_times = []
            for _ in range(3):
                start_time = time.time()
                
                response = await test_client.get(endpoint, params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": mumbai["timezone_offset"]
                })
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert response.status_code == 200
                response_times.append(response_time)
            
            # Analyze performance
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            
            assert avg_time < benchmark["target_time"], f"{endpoint} avg time {avg_time:.3f}s exceeds target {benchmark['target_time']}s"
            assert max_time < benchmark["max_time"], f"{endpoint} max time {max_time:.3f}s exceeds limit {benchmark['max_time']}s"
            
            print(f"{endpoint} - Avg: {avg_time:.3f}s, Max: {max_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, test_client, test_locations, test_dates):
        """Test performance under concurrent load."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        async def make_panchang_request():
            response = await test_client.get("/v1/panchang", params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            })
            return response.status_code == 200, time.time()
        
        # Test with 10 concurrent requests
        concurrent_requests = 10
        start_time = time.time()
        
        tasks = [make_panchang_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all requests succeeded
        success_count = sum(1 for success, _ in results if success)
        assert success_count == concurrent_requests, f"Only {success_count}/{concurrent_requests} requests succeeded"
        
        # Performance should be reasonable even under load
        avg_time_per_request = total_time / concurrent_requests
        assert avg_time_per_request < 5.0, f"Concurrent avg time {avg_time_per_request:.3f}s too high"
        
        print(f"Concurrent load test - {concurrent_requests} requests in {total_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self, test_client, test_locations, test_dates):
        """Test memory usage stability over multiple requests."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Make multiple requests to check for memory leaks
        for i in range(20):
            response = await test_client.get("/v1/panchang", params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date["date"],
                "time": test_date["time"],
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            assert response.status_code == 200
            
            # Verify response is complete (basic check for memory issues)
            data = response.json()
            assert "tithi" in data
            assert "nakshatra" in data
        
        print(f"✅ Memory stability test completed - 20 requests")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_different_locations_performance(self, test_client, test_locations, test_dates):
        """Test performance consistency across different global locations."""
        test_date = test_dates["current_test"]
        
        performance_data = {}
        
        for location_name, location in test_locations.items():
            response_times = []
            
            # Test 3 times for each location
            for _ in range(3):
                start_time = time.time()
                
                response = await test_client.get("/v1/panchang", params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": location["timezone_offset"]
                })
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert response.status_code == 200
                response_times.append(response_time)
            
            avg_time = statistics.mean(response_times)
            performance_data[location_name] = avg_time
            
            # Performance should be consistent regardless of location
            assert avg_time < 5.0, f"Performance for {location_name} too slow: {avg_time:.3f}s"
        
        # Verify performance variance is reasonable
        performance_values = list(performance_data.values())
        max_variance = max(performance_values) - min(performance_values)
        assert max_variance < 2.0, f"Performance variance too high: {max_variance:.3f}s"
        
        for location, time_taken in performance_data.items():
            print(f"{location}: {time_taken:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_large_date_range_performance(self, test_client, test_locations):
        """Test performance with calculations across large date ranges."""
        mumbai = test_locations["mumbai"]
        
        # Test with dates spread across different years
        test_dates = [
            "2020-01-01", "2021-06-15", "2022-12-31", 
            "2023-03-21", "2024-09-15", "2025-07-25"
        ]
        
        total_start_time = time.time()
        
        for test_date in test_dates:
            start_time = time.time()
            
            response = await test_client.get("/v1/panchang", params={
                "latitude": mumbai["latitude"],
                "longitude": mumbai["longitude"],
                "date": test_date,
                "time": "12:00:00",
                "timezone_offset": mumbai["timezone_offset"]
            })
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == 200
            assert response_time < 5.0, f"Date {test_date} took too long: {response_time:.3f}s"
        
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        
        print(f"Large date range test - 6 dates in {total_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_response_size_efficiency(self, test_client, test_locations, test_dates):
        """Test API response size efficiency."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Test core panchang response size
        response = await test_client.get("/v1/panchang", params={
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        })
        
        assert response.status_code == 200
        
        # Check response size is reasonable
        response_data = response.json()
        response_size = len(str(response_data))
        
        # Response should be comprehensive but not excessive
        assert 1000 < response_size < 50000, f"Response size {response_size} bytes seems unreasonable"
        
        # Verify response contains expected data density
        field_count = len(response_data)
        assert field_count > 10, f"Response has too few fields: {field_count}"
        
        print(f"Panchang response size: {response_size} bytes, {field_count} fields")

    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_extended_load_test(self, test_client, test_locations, test_dates):
        """Extended load test for sustained performance."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        # Run 50 requests to test sustained performance
        response_times = []
        errors = 0
        
        for i in range(50):
            try:
                start_time = time.time()
                
                response = await test_client.get("/v1/panchang", params={
                    "latitude": mumbai["latitude"],
                    "longitude": mumbai["longitude"],
                    "date": test_date["date"],
                    "time": test_date["time"],
                    "timezone_offset": mumbai["timezone_offset"]
                })
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    response_times.append(response_time)
                else:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                print(f"Request {i} failed: {e}")
        
        # Analyze results
        if response_times:
            avg_time = statistics.mean(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            # Performance should remain stable
            assert avg_time < 3.0, f"Average time degraded to {avg_time:.3f}s"
            assert max_time < 10.0, f"Max time too high: {max_time:.3f}s"
            
            # Error rate should be low
            error_rate = errors / 50
            assert error_rate < 0.1, f"Error rate too high: {error_rate*100:.1f}%"
            
            print(f"Extended load test - 50 requests: Avg {avg_time:.3f}s, Errors: {errors}")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_effectiveness(self, test_client, test_locations, test_dates):
        """Test cache effectiveness for repeated requests."""
        mumbai = test_locations["mumbai"]
        test_date = test_dates["current_test"]
        
        request_params = {
            "latitude": mumbai["latitude"],
            "longitude": mumbai["longitude"],
            "date": test_date["date"],
            "time": test_date["time"],
            "timezone_offset": mumbai["timezone_offset"]
        }
        
        # First request (cache miss)
        start_time = time.time()
        first_response = await test_client.get("/v1/panchang", params=request_params)
        first_time = time.time() - start_time
        
        assert first_response.status_code == 200
        
        # Second identical request (potential cache hit)
        start_time = time.time()
        second_response = await test_client.get("/v1/panchang", params=request_params)
        second_time = time.time() - start_time
        
        assert second_response.status_code == 200
        
        # Responses should be identical
        assert first_response.json() == second_response.json()
        
        # Note: Cache effectiveness depends on implementation
        # This test documents performance rather than enforcing it
        print(f"Cache test - First: {first_time:.3f}s, Second: {second_time:.3f}s")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_error_handling_performance(self, test_client):
        """Test performance of error handling."""
        # Test invalid request performance
        start_time = time.time()
        
        response = await test_client.get("/v1/panchang", params={
            "latitude": 91.0,  # Invalid latitude
            "longitude": 72.8777,
            "date": "2025-07-25",
            "time": "12:00:00",
            "timezone_offset": 5.5
        })
        
        end_time = time.time()
        error_response_time = end_time - start_time
        
        # Error responses should be fast
        assert response.status_code == 422
        assert error_response_time < 1.0, f"Error response too slow: {error_response_time:.3f}s"
        
        print(f"Error handling performance: {error_response_time:.3f}s") 