# 🕉️ **Brahmakaal Enterprise API - Complete Documentation**

**Version 1.0.0** | **Production Ready** | **July 2025**
**NEW**: Phase 4 Personalized APIs - **In Development**

## 🎯 **Executive Summary**

Brahmakaal Enterprise API is a **world-class Vedic astronomy calculation service** featuring comprehensive panchang calculations, festival calendars, muhurta analysis, and ayanamsha comparisons. Built with modern async architecture, enterprise security, and professional-grade infrastructure.

**🌟 NEW**: Phase 4 introduces **personalized astrology APIs** with natal chart integration, transit analysis, and AI-powered recommendations.

### **🏆 Key Achievements**
- **✅ Complete Authentication System** with JWT + API Keys
- **✅ PostgreSQL Database** with SSL connectivity and connection pooling  
- **✅ 27 Production Endpoints** across 7 functional modules
- **✅ Subscription-Based Rate Limiting** (Free → Enterprise tiers)
- **✅ Professional Documentation** with OpenAPI/Swagger integration
- **✅ Enterprise Security** with CORS, middleware stack, and input validation
- **✅ Analytics & Usage Tracking** for billing and performance monitoring
- **🆕 Phase 4 Development Started**: Personalized astrology features in development

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

## 🌟 **Phase 4: Festival Calendar & Validation (Complete) + Personalized APIs (Implemented)**

### **Available Personalized Endpoints**
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/v1/panchang/personalized` | Personalized panchang with birth chart integration | ✅ Implemented |
| POST | `/v1/muhurta/personalized` | Personalized muhurta with birth chart integration | ✅ Implemented |

### **Planned Endpoints (Not Yet Available)**
| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/v1/users/preferences` | Set user preferences | 📋 Planned |
| GET | `/v1/users/preferences` | Get user preferences | 📋 Planned |
| POST | `/v1/recommendations/daily` | AI daily recommendations | 📋 Planned |

### **👤 User Profile & Preferences Management**
```bash
# Store user birth data and astrological preferences
POST /v1/users/preferences
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30:00",
  "birth_latitude": 28.6139,
  "birth_longitude": 77.2090,
  "birth_timezone": "Asia/Kolkata",
  "birth_location_name": "New Delhi, India",
  "privacy_settings": {
    "allow_data_analysis": true,
    "share_anonymized_insights": false
  }
}

# Retrieve user astrological profile
GET /v1/users/preferences
```

### **🌟 Personalized Daily Panchang**
```bash
# Personalized panchang with birth chart integration
POST /v1/panchang/personalized
{
  "user_profile_id": "uuid-or-birth-details",
  "target_date": "2025-07-15",
  "include_transit_analysis": true,
  "recommendation_depth": "detailed"
}

# Response includes:
# - Standard panchang data
# - Personalized favorable/unfavorable periods
# - Daily guidance based on natal chart
# - Recommended and avoided activities
# - Transit highlights affecting the user
```

### **🔮 Natal Chart Generation**
```bash
# Complete birth chart generation with insights
POST /v1/horoscope/natal-chart
{
  "birth_date": "1990-01-15",
  "birth_time": "14:30:00",
  "birth_latitude": 28.6139,
  "birth_longitude": 77.2090,
  "ayanamsha": "LAHIRI",
  "include_insights": true
}

# Returns:
# - Ascendant, Moon sign, Sun sign
# - Planetary positions in signs, houses, nakshatras
# - Key personality insights and life themes
# - Planetary strengths and aspects
# - Traditional yogas and their effects
```

### **🌍 Daily Transit Analysis**
```bash
# Planetary transit analysis against natal chart
POST /v1/transits/daily
{
  "user_profile_id": "uuid-here",
  "analysis_date": "2025-07-15",
  "include_predictions": true,
  "transit_types": ["beneficial", "challenging", "neutral"]
}

# Returns:
# - Current planetary positions vs natal chart
# - Active transit aspects and their effects
# - Timeline of upcoming transits
# - Life area impacts and recommendations
```

### **⏰ Personalized Muhurta Timing**
```bash
# Personalized auspicious timing recommendations
POST /v1/muhurta/personalized
{
  "user_profile_id": "uuid-here",
  "activity_type": "MARRIAGE",
  "start_date": "2025-08-01",
  "end_date": "2025-08-31",
  "duration_minutes": 180,
  "custom_preferences": {
    "avoid_saturday": true,
    "prefer_morning": true
  }
}

# Returns muhurta times optimized for individual birth chart
```

### **🤖 AI-Powered Daily Recommendations**
```bash
# Machine learning-powered personalized insights
POST /v1/recommendations/daily
{
  "user_profile_id": "uuid-here",
  "recommendation_date": "2025-07-15",
  "categories": ["general", "career", "relationships", "health"],
  "detail_level": "comprehensive"
}

# Returns:
# - AI-generated daily guidance
# - Personalized activity recommendations
# - Timing suggestions based on current transits
# - Learning insights from user behavior
```

### **📊 Enhanced User Analytics**
```bash
# Personalized usage analytics and engagement tracking
GET /v1/analytics/user-engagement?user_id={id}&days=30

# Returns:
# - Personalized API usage patterns
# - Feature adoption and preferences
# - Recommendation effectiveness metrics
# - User satisfaction and feedback data
```

---

## 💎 **Updated Subscription Tiers & Features**

| Tier | Price | Req/Min | Req/Day | Standard Features | **NEW: Personalized Features** |
|------|-------|---------|---------|-------------------|--------------------------------|
| **Free** | $0 | 10 | 100 | Basic APIs, JSON export | ❌ No personalized features |
| **Basic** | $29/mo | 60 | 5,000 | All APIs, iCal export | ❌ No personalized features |
| **Premium** | $99/mo | 300 | 50,000 | All formats, webhooks | ✅ **Basic personalized APIs** |
| **Enterprise** | $299/mo | 1,000 | 200,000 | Custom integration, SLA | ✅ **Full personalized suite + AI** |

### **🌟 New Personalized Features by Tier**

#### **Premium Tier Personalized Features**
- ✅ User profile storage and management
- ✅ Basic natal chart generation
- ✅ Personalized daily panchang (limited)
- ✅ Simple transit analysis

#### **Enterprise Tier Personalized Features**
- ✅ Complete natal chart with detailed insights
- ✅ Advanced personalized muhurta recommendations
- ✅ AI-powered daily recommendations
- ✅ Comprehensive transit analysis
- ✅ Personalized analytics and engagement tracking
- ✅ Priority support for personalized features

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

## 📊 **Sample Personalized API Responses**

### **Personalized Daily Panchang Response**
```json
{
  "basic_panchang": {
    "tithi": "Dwadashi",
    "nakshatra": "Pushya",
    "yoga": "Dhruva",
    "sunrise": "2025-07-15T06:45:23.000Z"
  },
  "personalized_insights": {
    "favorable_periods": [
      {
        "start": "06:00",
        "end": "08:30", 
        "activity": "meditation",
        "strength": "high",
        "reason": "jupiter_trine_natal_moon"
      }
    ],
    "unfavorable_periods": [
      {
        "start": "12:00",
        "end": "14:00",
        "reason": "mars_square_natal_sun",
        "severity": "medium"
      }
    ],
    "daily_guidance": "Strong lunar influence enhances your intuitive abilities today. Jupiter's beneficial aspect to your natal Moon brings emotional harmony and family blessings.",
    "recommended_activities": ["spiritual practices", "family time", "creative work"],
    "avoid_activities": ["major confrontations", "risky investments"]
  }
}
```

### **Natal Chart Response**
```json
{
  "chart_data": {
    "ascendant": {"sign": "Aries", "degree": 15.67},
    "planetary_positions": {
      "sun": {
        "sign": "Capricorn",
        "degree": 25.34,
        "house": 10,
        "nakshatra": "Dhanishta",
        "dignity": "neutral"
      },
      "moon": {
        "sign": "Cancer", 
        "degree": 12.89,
        "house": 4,
        "nakshatra": "Pushya",
        "dignity": "exalted"
      }
    }
  },
  "key_insights": {
    "personality_traits": ["ambitious", "intuitive", "leadership-oriented"],
    "life_themes": ["career achievement", "family focus", "spiritual growth"],
    "strengths": ["natural leadership", "emotional intelligence", "determination"],
    "challenges": ["work-life balance", "overthinking tendencies"]
  },
  "planetary_yogas": [
    {
      "name": "Chandra_Mangal_Yoga",
      "strength": "moderate",
      "effects": ["financial prosperity", "property acquisition"]
    }
  ]
}
```

---

## 🔒 **Enhanced Privacy & Security for Personalized Features**

### **Birth Data Protection**
- **🔐 End-to-End Encryption**: All birth data encrypted with user-specific keys
- **🗄️ Secure Storage**: Birth charts cached with advanced encryption
- **🔑 Access Control**: User-controlled data sharing permissions
- **🌍 GDPR Compliance**: Full European data protection compliance

### **AI & ML Security**
- **🤖 Model Protection**: AI recommendation algorithms secured against reverse engineering
- **📊 Anonymized Training**: AI models trained on anonymized data only
- **🎯 Bias Prevention**: Regular audits for algorithmic fairness
- **🛡️ Ethical Guidelines**: Transparent and responsible AI recommendations

---

**📋 See [PHASE4_PERSONALIZED_ROADMAP.md](PHASE4_PERSONALIZED_ROADMAP.md) for complete Phase 4 development details**

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