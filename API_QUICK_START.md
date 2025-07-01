# 🚀 **Brahmakaal Enterprise API - Quick Start Guide**

**Get started with the world's most advanced Vedic astronomy API in under 5 minutes!**

---

## ⚡ **Instant Access with Test User**

### 🕉️ **Brahma Test Account** (Ready to Use)
```
👤 Username: brahma
📧 Email: brahma@brahmakaal.com  
🔑 Password: brahma123
🏆 Role: Admin (Unlimited Access)
💎 Subscription: Enterprise
🔐 API Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw
📅 Expires: Never (100 years)
```

**Use these credentials to immediately start testing all API endpoints!**

---

## 🎯 **Step 1: Test System Health**

```bash
# Check if the API is running
curl http://localhost:8000/v1/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 1800,
  "database_connected": true,
  "ephemeris_loaded": true
}
```

---

## 🔐 **Step 2: Authentication Methods**

### **Method 1: API Key** (Recommended for quick testing)

```bash
# Use Brahma's API key directly
curl -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  http://localhost:8000/v1/panchang?lat=28.6139&lon=77.2090&date=2025-01-01
```

### **Method 2: JWT Bearer Token** (Recommended for applications)

```bash
# Login to get tokens
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "brahma@brahmakaal.com",
    "password": "brahma123"
  }'

# Use the returned access_token in requests:
curl -H "Authorization: Bearer <your_access_token>" \
  http://localhost:8000/v1/panchang?lat=28.6139&lon=77.2090&date=2025-01-01
```

---

## 📅 **Step 3: Try Core Calculations**

### **Panchang Calculation** (Most Popular)
```bash
# Quick panchang for Delhi, India
curl -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  "http://localhost:8000/v1/panchang?lat=28.6139&lon=77.2090&date=2025-01-01&ayanamsha=LAHIRI"

# Returns 50+ parameters including:
# - Tithi, Nakshatra, Yoga, Karana
# - Sunrise, sunset, moonrise, moonset
# - Rahu Kaal, Gulika Kaal, Brahma Muhurta
# - All planetary positions with signs
```

### **Festival Calendar**
```bash
# Get Hindu festivals for 2025
curl -X POST http://localhost:8000/v1/festivals \
  -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  -H "Content-Type: application/json" \
  -d '{
    "year": 2025,
    "regions": ["ALL_INDIA"],
    "categories": ["MAJOR"]
  }'
```

### **Ayanamsha Comparison**
```bash
# Compare all 10 ayanamsha systems
curl -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  "http://localhost:8000/v1/ayanamsha?date=2025-01-01"
```

---

## 📚 **Step 4: Explore Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### **Available Endpoints**
```
System Health:
├── GET /v1/health              # Quick health check
└── GET /v1/status              # Detailed system metrics

Authentication:
├── POST /v1/auth/register      # Create new account
├── POST /v1/auth/login         # Get JWT tokens
├── GET  /v1/auth/me           # Current user info
└── GET  /v1/auth/subscription  # Subscription details

Vedic Calculations:
├── GET  /v1/panchang           # Panchang calculation (50+ params)
├── POST /v1/festivals          # Festival calendar generation
├── GET  /v1/ayanamsha          # Ayanamsha comparison
└── POST /v1/muhurta            # Muhurta calculations
```

---

## 💎 **Step 5: Subscription Tiers**

| Tier | Price | Req/Min | Your Access |
|------|-------|---------|-------------|
| **Free** | $0 | 10 | Basic APIs |
| **Basic** | $29/mo | 60 | + Muhurta, iCal export |
| **Premium** | $99/mo | 300 | + Webhooks, CSV export |
| **Enterprise** | $299/mo | 1,000 | + Custom integration |
| **🕉️ Brahma** | Test | **∞** | **Unlimited Everything** |

**As Brahma user, you have unlimited access to all features!**

---

## 🐍 **Step 6: Python Client Example**

```python
import requests

# Using API Key (easiest)
headers = {
    "X-API-Key": "bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw"
}

# Get daily panchang for Delhi
response = requests.get(
    "http://localhost:8000/v1/panchang",
    params={
        "lat": 28.6139,  # Delhi coordinates
        "lon": 77.2090,
        "date": "2025-01-01",
        "ayanamsha": "LAHIRI"
    },
    headers=headers
)

panchang = response.json()
print(f"Today's Tithi: {panchang['tithi_name']}")
print(f"Nakshatra: {panchang['nakshatra']}")
print(f"Sunrise: {panchang['sunrise']}")
print(f"Sunset: {panchang['sunset']}")
```

---

## 🎉 **You're Ready!**

**🎯 You now have everything needed to start using the Brahmakaal Enterprise API:**

✅ Test user credentials with unlimited access  
✅ All authentication methods explained  
✅ Working examples in multiple languages  
✅ Complete endpoint documentation  

**🚀 Start building your Vedic astronomy application today!**

---

*Built with ❤️ for the global Vedic astronomy community.* 