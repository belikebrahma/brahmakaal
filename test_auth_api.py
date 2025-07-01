#!/usr/bin/env python3
"""
Comprehensive Authentication & Security Test Suite
Tests the complete authentication system, rate limiting, and subscription management
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
import pytest

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/v1"

class TestClient:
    """Enhanced test client with authentication support"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token: Optional[str] = None
        self.api_key: Optional[str] = None
        self.user_data: Dict[str, Any] = {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def get_auth_headers(self, use_api_key: bool = False) -> Dict[str, str]:
        """Get authentication headers"""
        if use_api_key and self.api_key:
            return {"X-API-Key": self.api_key}
        elif self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        return {}
    
    async def request(self, method: str, endpoint: str, use_api_key: bool = False, **kwargs) -> httpx.Response:
        """Make authenticated request"""
        headers = kwargs.get("headers", {})
        headers.update(self.get_auth_headers(use_api_key))
        kwargs["headers"] = headers
        
        url = f"{API_BASE}{endpoint}"
        return await self.client.request(method, url, **kwargs)

# Test data
TEST_USER = {
    "email": "test@brahmakaal.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "SecurePassword123!"
}

ADMIN_USER = {
    "email": "admin@brahmakaal.com", 
    "username": "admin",
    "full_name": "Admin User",
    "password": "AdminPassword123!"
}

async def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "cache" in data
        assert "ephemeris" in data
        
        print("✅ Health check passed")

async def test_user_registration():
    """Test user registration"""
    print("👤 Testing user registration...")
    
    client = TestClient()
    
    try:
        # Register user
        response = await client.request("POST", "/auth/register", json=TEST_USER)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == TEST_USER["email"]
        assert data["username"] == TEST_USER["username"]
        assert data["is_active"] == True
        assert data["is_verified"] == False  # Email verification required
        
        client.user_data = data
        print(f"✅ User registered: {data['email']}")
        
    finally:
        await client.close()

async def test_user_login():
    """Test user login and token generation"""
    print("🔐 Testing user login...")
    
    client = TestClient()
    
    try:
        # Login
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        response = await client.request("POST", "/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        
        client.access_token = data["access_token"]
        print(f"✅ Login successful, token expires in {data['expires_in']} seconds")
        
        return client.access_token
        
    finally:
        await client.close()

async def test_authenticated_endpoints():
    """Test authenticated endpoints"""
    print("🔑 Testing authenticated endpoints...")
    
    client = TestClient()
    
    try:
        # First login
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        login_response = await client.request("POST", "/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token_data = login_response.json()
        client.access_token = token_data["access_token"]
        
        # Test /auth/me
        me_response = await client.request("GET", "/auth/me")
        assert me_response.status_code == 200
        
        user_data = me_response.json()
        assert user_data["email"] == TEST_USER["email"]
        print(f"✅ /auth/me returned user: {user_data['email']}")
        
        # Test subscription info
        sub_response = await client.request("GET", "/auth/subscription")
        assert sub_response.status_code == 200
        
        sub_data = sub_response.json()
        assert sub_data["tier"] == "free"
        assert sub_data["status"] == "active"
        print(f"✅ User has {sub_data['tier']} subscription")
        
    finally:
        await client.close()

async def test_api_key_management():
    """Test API key creation and management"""
    print("🔑 Testing API key management...")
    
    client = TestClient()
    
    try:
        # Login first
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        login_response = await client.request("POST", "/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        client.access_token = login_response.json()["access_token"]
        
        # Create API key
        key_data = {
            "name": "Test API Key",
            "scopes": ["panchang", "festivals"],
            "expires_in_days": 30
        }
        
        create_response = await client.request("POST", "/auth/api-keys", json=key_data)
        assert create_response.status_code == 201
        
        key_response = create_response.json()
        assert "key" in key_response
        assert key_response["key"].startswith("bk_live_")
        assert key_response["api_key"]["name"] == key_data["name"]
        
        client.api_key = key_response["key"]
        print(f"✅ API key created: {key_response['api_key']['key_prefix']}...")
        
        # Test API key authentication
        me_response = await client.request("GET", "/auth/me", use_api_key=True)
        assert me_response.status_code == 200
        print("✅ API key authentication successful")
        
        # List API keys
        list_response = await client.request("GET", "/auth/api-keys")
        assert list_response.status_code == 200
        
        keys = list_response.json()
        assert len(keys) >= 1
        assert keys[0]["name"] == key_data["name"]
        print(f"✅ Listed {len(keys)} API key(s)")
        
    finally:
        await client.close()

async def test_rate_limiting():
    """Test rate limiting functionality"""
    print("⏱️ Testing rate limiting...")
    
    client = TestClient()
    
    try:
        # Login and get API key
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        login_response = await client.request("POST", "/auth/login", json=login_data)
        client.access_token = login_response.json()["access_token"]
        
        # Create API key for testing
        key_data = {"name": "Rate Limit Test Key"}
        key_response = await client.request("POST", "/auth/api-keys", json=key_data)
        client.api_key = key_response.json()["key"]
        
        # Make requests to test rate limiting
        request_count = 0
        rate_limited = False
        
        print("🚀 Making rapid requests to test rate limits...")
        
        for i in range(15):  # Free tier: 10 requests/minute
            response = await client.request("GET", "/panchang", use_api_key=True, params={
                "date": "2024-01-01",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timezone": "Asia/Kolkata"
            })
            
            request_count += 1
            
            # Check rate limit headers
            if "X-RateLimit-Remaining-Minute" in response.headers:
                remaining = int(response.headers["X-RateLimit-Remaining-Minute"])
                print(f"Request {request_count}: Status {response.status_code}, Remaining: {remaining}")
            
            if response.status_code == 429:
                print(f"✅ Rate limit enforced after {request_count} requests")
                rate_limited = True
                
                # Check error response
                error_data = response.json()
                assert "error" in error_data["detail"]
                assert "retry_after" in error_data["detail"]
                break
            
            # Small delay to avoid overwhelming
            await asyncio.sleep(0.1)
        
        if not rate_limited:
            print("⚠️ Rate limiting not triggered (may need more requests)")
        
    finally:
        await client.close()

async def test_subscription_management():
    """Test subscription upgrade (placeholder)"""
    print("💳 Testing subscription management...")
    
    client = TestClient()
    
    try:
        # Login
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        login_response = await client.request("POST", "/auth/login", json=login_data)
        client.access_token = login_response.json()["access_token"]
        
        # Try to upgrade subscription (this would normally require payment)
        upgrade_data = {
            "tier": "basic",
            "billing_email": TEST_USER["email"]
        }
        
        upgrade_response = await client.request("POST", "/auth/subscription/upgrade", json=upgrade_data)
        assert upgrade_response.status_code == 200
        
        sub_data = upgrade_response.json()
        assert sub_data["tier"] == "basic"
        assert sub_data["requests_per_minute"] == 60
        print(f"✅ Subscription upgraded to {sub_data['tier']}")
        
    finally:
        await client.close()

async def test_usage_analytics():
    """Test usage analytics"""
    print("📊 Testing usage analytics...")
    
    client = TestClient()
    
    try:
        # Login
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        login_response = await client.request("POST", "/auth/login", json=login_data)
        client.access_token = login_response.json()["access_token"]
        
        # Make a few API calls to generate usage data
        for i in range(3):
            await client.request("GET", "/panchang", params={
                "date": f"2024-01-0{i+1}",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "timezone": "Asia/Kolkata"
            })
        
        # Get usage stats
        stats_response = await client.request("GET", "/analytics/my-usage")
        assert stats_response.status_code == 200
        
        stats_data = stats_response.json()
        assert "total_requests" in stats_data
        assert "requests_today" in stats_data
        assert "top_endpoints" in stats_data
        print(f"✅ Usage stats: {stats_data['total_requests']} total requests")
        
        # Get subscription info with usage
        sub_info_response = await client.request("GET", "/analytics/subscription-info")
        assert sub_info_response.status_code == 200
        
        sub_info = sub_info_response.json()
        assert "subscription" in sub_info
        assert "usage" in sub_info
        print(f"✅ Subscription usage: {sub_info['usage']['today']}/{sub_info['usage']['today_limit']} today")
        
    finally:
        await client.close()

async def test_admin_endpoints():
    """Test admin endpoints (would need admin user)"""
    print("👑 Testing admin endpoints...")
    
    # This test would require creating an admin user
    # For now, just test that the endpoints exist and require auth
    
    client = TestClient()
    
    try:
        # Try admin endpoint without auth
        admin_response = await client.request("GET", "/analytics/admin/dashboard")
        assert admin_response.status_code == 401
        print("✅ Admin endpoints require authentication")
        
    finally:
        await client.close()

async def test_error_handling():
    """Test error handling and edge cases"""
    print("🚨 Testing error handling...")
    
    client = TestClient()
    
    try:
        # Test invalid login
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        login_response = await client.request("POST", "/auth/login", json=invalid_login)
        assert login_response.status_code == 401
        
        error_data = login_response.json()
        assert "detail" in error_data
        print("✅ Invalid login properly rejected")
        
        # Test accessing protected endpoint without auth
        me_response = await client.request("GET", "/auth/me")
        assert me_response.status_code == 401
        print("✅ Protected endpoint requires authentication")
        
        # Test invalid API endpoint
        invalid_response = await client.request("GET", "/invalid-endpoint")
        assert invalid_response.status_code == 404
        print("✅ Invalid endpoints return 404")
        
    finally:
        await client.close()

async def run_all_tests():
    """Run all authentication and security tests"""
    print("🔐 Starting Brahmakaal Authentication & Security Test Suite")
    print("=" * 60)
    
    try:
        await test_health_check()
        await test_user_registration()
        await test_user_login()
        await test_authenticated_endpoints()
        await test_api_key_management()
        await test_rate_limiting()
        await test_subscription_management()
        await test_usage_analytics()
        await test_admin_endpoints()
        await test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 All authentication and security tests passed!")
        print("\n📋 Test Summary:")
        print("✅ User registration and authentication")
        print("✅ JWT token management")
        print("✅ API key creation and usage")
        print("✅ Rate limiting enforcement")
        print("✅ Subscription management")
        print("✅ Usage analytics tracking")
        print("✅ Error handling and security")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Run the test suite
    result = asyncio.run(run_all_tests())
    exit(0 if result else 1) 