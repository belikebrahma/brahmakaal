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

### **Method 1: JWT Bearer Token** (Recommended for applications)

```bash
# Login to get tokens
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "brahma@brahmakaal.com",
    "password": "brahma123"
  }'

# Response includes access_token - use in requests:
curl -H "Authorization: Bearer <your_access_token>" \
  http://localhost:8000/v1/panchang?lat=28.6139&lon=77.2090&date=2025-01-01
```

### **Method 2: API Key** (Recommended for quick testing)

```bash
# Use Brahma's API key directly
curl -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
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

### **Muhurta (Auspicious Times)**
```bash
# Find auspicious times for marriage
curl -X POST http://localhost:8000/v1/muhurta \
  -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  -H "Content-Type: application/json" \
  -d '{
    "muhurta_type": "MARRIAGE",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "start_date": "2025-01-01T00:00:00",
    "end_date": "2025-01-31T23:59:59",
    "duration_minutes": 120,
    "min_quality": "GOOD"
  }'
```

---

## 📚 **Step 4: Explore Documentation**

### **Interactive Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### **All Available Endpoints**
```
System Health:
├── GET /v1/health              # Quick health check
└── GET /v1/status              # Detailed system metrics

Authentication:
├── POST /v1/auth/register      # Create new account
├── POST /v1/auth/login         # Get JWT tokens
├── POST /v1/auth/refresh       # Refresh access token
├── GET  /v1/auth/me           # Current user info
└── GET  /v1/auth/subscription  # Subscription details

API Keys:
├── POST   /v1/auth/api-keys           # Create API key
├── GET    /v1/auth/api-keys           # List your keys
└── DELETE /v1/auth/api-keys/{key_id}  # Delete API key

Vedic Calculations:
├── GET  /v1/panchang           # Quick panchang calculation
├── POST /v1/panchang           # Detailed panchang (50+ params)
├── POST /v1/festivals          # Festival calendar generation
├── GET  /v1/festivals          # Quick festival lookup
├── GET  /v1/ayanamsha          # Ayanamsha comparison
├── POST /v1/muhurta            # Muhurta calculations
└── GET  /v1/muhurta/types      # Available muhurta types

Analytics:
├── GET /v1/my-usage                    # Your usage stats
├── GET /v1/subscription-info           # Subscription details
├── GET /v1/admin/dashboard             # Admin dashboard
└── GET /v1/admin/users                 # User management
```

---

## 💎 **Step 5: Understand Subscription Tiers**

| Tier | Price | Req/Min | Req/Day | Your Access |
|------|-------|---------|---------|-------------|
| **Free** | $0 | 10 | 100 | Basic APIs |
| **Basic** | $29/mo | 60 | 5,000 | + Muhurta, iCal export |
| **Premium** | $99/mo | 300 | 50,000 | + Webhooks, CSV export |
| **Enterprise** | $299/mo | 1,000 | 200,000 | + Custom integration |
| **🕉️ Brahma** | Test | **∞** | **∞** | **Unlimited Everything** |

**As Brahma user, you have unlimited access to all features!**

---

## 🛠️ **Step 6: Development Setup** (Optional)

### **If you want to run your own instance:**

```bash
# 1. Clone and setup
git clone <repo-url>
cd brahmakaal

# 2. Install dependencies
pip install fastapi uvicorn sqlalchemy asyncpg redis bcrypt 'passlib[bcrypt]' python-jose[cryptography]

# 3. Set environment variables
export DATABASE_URL="your_postgresql_url"
export JWT_SECRET_KEY="your_secret_key"
export REDIS_URL="redis://localhost:6379/0"

# 4. Start server
python start_auth_api.py

# 5. Server runs on http://localhost:8000
```

---

## 🐍 **Step 7: Python Client Example**

```python
import requests
import json

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

# Get this year's festivals
festival_response = requests.post(
    "http://localhost:8000/v1/festivals",
    json={
        "year": 2025,
        "regions": ["ALL_INDIA"],
        "categories": ["MAJOR"]
    },
    headers=headers
)

festivals = festival_response.json()
print(f"Found {len(festivals['festivals'])} major festivals")
for festival in festivals['festivals'][:5]:
    print(f"- {festival['name']}: {festival['date']}")
```

---

## 📱 **Step 8: JavaScript/Web Example**

```javascript
// Using API Key
const API_KEY = 'bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw';
const BASE_URL = 'http://localhost:8000/v1';

// Get panchang data
async function getPanchang(lat, lon, date) {
    const response = await fetch(
        `${BASE_URL}/panchang?lat=${lat}&lon=${lon}&date=${date}&ayanamsha=LAHIRI`,
        {
            headers: {
                'X-API-Key': API_KEY
            }
        }
    );
    
    const panchang = await response.json();
    console.log('Tithi:', panchang.tithi_name);
    console.log('Nakshatra:', panchang.nakshatra);
    return panchang;
}

// Example usage
getPanchang(28.6139, 77.2090, '2025-01-01');
```

---

## ⚡ **Step 9: Advanced Features**

### **Batch Processing** (Enterprise Feature)
```python
# Process multiple dates at once
dates = ['2025-01-01', '2025-01-02', '2025-01-03']
results = []

for date in dates:
    response = requests.get(
        f"http://localhost:8000/v1/panchang",
        params={"lat": 28.6139, "lon": 77.2090, "date": date},
        headers={"X-API-Key": "bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw"}
    )
    results.append(response.json())

print(f"Processed {len(results)} calculations")
```

### **Export Formats** (Premium+ Feature)
```bash
# Get festivals in iCal format
curl -X POST http://localhost:8000/v1/festivals \
  -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  -d '{"year": 2025, "export_format": "ical"}'

# CSV export also available
curl -X POST http://localhost:8000/v1/festivals \
  -H "X-API-Key: bk_live_spPpLTAJKFiin6mxgv76LX1Olr3OshL-F6a_bicnchw" \
  -d '{"year": 2025, "export_format": "csv"}'
```

---

## 🆘 **Step 10: Getting Help**

### **Common Issues**
1. **API Key not working?** → Check that server is running on port 8000
2. **Date format errors?** → Use YYYY-MM-DD format (ISO 8601)
3. **Coordinate issues?** → Use decimal degrees (positive for N/E, negative for S/W)
4. **Ayanamsha errors?** → Use: LAHIRI, RAMAN, KRISHNAMURTI, etc.

### **Support Resources**
- **📚 Full Documentation**: Check `/docs` endpoint
- **🔧 Health Check**: Monitor `/v1/health` for system status
- **📊 Usage Stats**: Use `/v1/my-usage` to track your requests
- **🎯 Test Examples**: All examples above use the Brahma test account

### **Rate Limits**
- **Brahma User**: Unlimited (perfect for testing!)
- **Free Tier**: 10 req/min, 100 req/day
- **Paid Tiers**: See subscription table above

---

## 🎉 **You're Ready!**

**🎯 You now have everything needed to start using the Brahmakaal Enterprise API:**

✅ Test user credentials with unlimited access  
✅ All authentication methods explained  
✅ Working examples in multiple languages  
✅ Complete endpoint documentation  
✅ Advanced features showcase  

**🚀 Start building your Vedic astronomy application today!**

---

*The Brahmakaal Enterprise API makes ancient Vedic astronomy calculations accessible to modern developers worldwide. Built with ❤️ for the global spiritual and astronomical community.* 