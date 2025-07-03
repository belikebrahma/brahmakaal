# 🕉️ **Brahmakaal Enterprise API - Complete Documentation**

**Version 1.0.0** | **Production Ready** | **July 2025**

## 🎯 **Executive Summary**

Brahmakaal Enterprise API is a **world-class Vedic astronomy calculation service** featuring comprehensive panchang calculations, festival calendars, muhurta analysis, and ayanamsha comparisons. Built with modern async architecture, enterprise security, and professional-grade infrastructure.

### **🏆 Key Achievements**
- **✅ Complete Authentication System** with JWT + API Keys
- **✅ PostgreSQL Database** with SSL connectivity and connection pooling  
- **✅ 27 Production Endpoints** across 7 functional modules
- **✅ Subscription-Based Rate Limiting** (Free → Enterprise tiers)
- **✅ Professional Documentation** with OpenAPI/Swagger integration
- **✅ Enterprise Security** with CORS, middleware stack, and input validation
- **✅ Analytics & Usage Tracking** for billing and performance monitoring

---

## 🚀 **API Endpoints Overview**

### **📊 System Health & Monitoring**
```bash
GET /v1/health          # System health check
GET /v1/status          # Detailed system metrics
```

### **🔐 Authentication & User Management** 
```bash
POST /v1/auth/register       # User registration
POST /v1/auth/login          # JWT token login
POST /v1/auth/refresh        # Token refresh
GET  /v1/auth/me            # Current user info
GET  /v1/auth/subscription  # Subscription details

# API Key Management
POST   /v1/auth/api-keys           # Create API key
GET    /v1/auth/api-keys           # List user's keys
DELETE /v1/auth/api-keys/{key_id}  # Delete API key

# Subscription Management
POST /v1/auth/subscription/upgrade # Upgrade subscription tier
```

### **📅 Panchang (Lunar Calendar) System**
```bash
# Quick calculation (GET)
GET /v1/panchang?lat={lat}&lon={lon}&date={date}&ayanamsha={system}

# Detailed calculation (POST)
POST /v1/panchang
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "date": "2025-01-01",
  "time": "12:00:00", 
  "ayanamsha": "LAHIRI",
  "timezone_offset": 5.5
}

# Returns 50+ Parameters:
# - Panchang Elements: Tithi, Nakshatra, Yoga, Karana
# - Solar Times: Sunrise, sunset, solar noon, day length
# - Lunar Data: Moonrise, moonset, phase, illumination  
# - Time Periods: Rahu Kaal, Gulika Kaal, Brahma Muhurta
# - Planetary Positions: All 9 Grahas with signs & nakshatras
# - Advanced: Ayanamsha, sidereal time, seasonal data
```

### **🎉 Festival Calendar System**
```bash
# Generate festival calendar
POST /v1/festivals
{
  "year": 2025,
  "regions": ["ALL_INDIA", "NORTH_INDIA"],
  "categories": ["MAJOR", "RELIGIOUS"],
  "export_format": "json"  // json, ical, csv
}

# Quick festival lookup
GET /v1/festivals?year=2025&regions=ALL_INDIA

# Metadata endpoints
GET /v1/festivals/regions     # Available regions
GET /v1/festivals/categories  # Festival categories
```

### **🌟 Ayanamsha Calculation System**
```bash
# Compare all ayanamsha systems
GET /v1/ayanamsha?date=2025-01-01

# Returns comparisons of:
# LAHIRI, RAMAN, KRISHNAMURTI, YUKTESHWAR, 
# SURYASIDDHANTA, FAGAN_BRADLEY, DELUCE,
# PUSHYA_PAKSHA, GALACTIC_CENTER, TRUE_CITRA

GET /v1/ayanamsha/systems  # System descriptions
```

### **⏰ Muhurta (Electional Astrology)**
```bash
# Calculate auspicious times
POST /v1/muhurta  
{
  "muhurta_type": "MARRIAGE",  // BUSINESS, TRAVEL, EDUCATION, etc.
  "latitude": 28.6139,
  "longitude": 77.2090,
  "start_date": "2025-01-01T00:00:00",
  "end_date": "2025-01-31T23:59:59",
  "duration_minutes": 120,
  "min_quality": "GOOD",
  "max_results": 10
}

GET /v1/muhurta/types  # Available muhurta types
```

### **📊 Analytics & Usage Tracking**
```bash
GET /v1/my-usage              # Personal usage statistics
GET /v1/subscription-info     # Detailed subscription info

# Admin endpoints (Admin role required)
GET /v1/admin/dashboard       # System-wide analytics
GET /v1/admin/users           # User management
GET /v1/admin/users/{id}/analytics  # User-specific analytics
```

---

## 💎 **Subscription Tiers & Features**

| Tier | Price | Req/Min | Req/Day | Features |
|------|-------|---------|---------|----------|
| **Free** | $0 | 10 | 100 | Basic APIs, JSON export |
| **Basic** | $29/mo | 60 | 5,000 | All APIs, iCal export, historical data |
| **Premium** | $99/mo | 300 | 50,000 | All formats, webhooks, batch processing |
| **Enterprise** | $299/mo | 1,000 | 200,000 | Custom integration, SLA, dedicated support |

---

## 🔒 **Authentication Methods**

### **1. JWT Bearer Tokens**
```bash
# Login to get tokens
POST /v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}

# Use in requests
Authorization: Bearer <access_token>
```

### **2. API Keys**
```bash
# Create API key
POST /v1/auth/api-keys
{
  "name": "My App Key",
  "scopes": ["panchang", "festivals"],
  "expires_in_days": 365
}

# Use in requests  
X-API-Key: bk_live_abc123...
```

---

## 📊 **Sample API Responses**

### **Complete Panchang Response (50+ Parameters)**
```json
{
  "tithi": 12.456,
  "tithi_name": "Dwadashi",
  "nakshatra": "Pushya",
  "nakshatra_lord": "Saturn",
  "yoga": 15.678,
  "yoga_name": "Dhruva", 
  "karana": 6.234,
  "karana_name": "Kaulava",
  "sunrise": "2025-01-01T06:45:23.000Z",
  "sunset": "2025-01-01T17:30:45.000Z",
  "solar_noon": "2025-01-01T12:08:04.000Z",
  "day_length": 10.756,
  "moonrise": "2025-01-01T23:15:30.000Z",
  "moonset": "2025-01-01T11:45:20.000Z",
  "moon_phase": "Waxing Gibbous",
  "moon_illumination": 87.5,
  "rahu_kaal": {
    "start": "2025-01-01T15:00:00.000Z",
    "end": "2025-01-01T16:30:00.000Z"
  },
  "graha_positions": {
    "Sun": {
      "longitude": 280.123,
      "latitude": 0.0,
      "rashi": "Capricorn",
      "nakshatra": "Shravana"
    },
    "Moon": {
      "longitude": 45.678,
      "latitude": 2.5,
      "rashi": "Taurus", 
      "nakshatra": "Rohini"
    }
  },
  "ayanamsha": 24.1234,
  "calculation_time_ms": 45,
  "location": {
    "latitude": 28.6139,
    "longitude": 77.2090,
    "elevation": 0.0
  }
}
```

---

## 🛠️ **Development & Deployment**

### **📋 Quick Start**
```bash
# 1. Install dependencies
pip install fastapi uvicorn sqlalchemy asyncpg redis bcrypt 'passlib[bcrypt]' python-jose[cryptography]

# 2. Start server
python start_auth_api.py

# 3. Access services
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/v1/health
```

### **🏥 Health Monitoring**
```bash
curl http://localhost:8000/v1/health
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "database_connected": true,
  "ephemeris_loaded": true
}
```

---

**Built with ❤️ for the global Vedic astronomy community.** 