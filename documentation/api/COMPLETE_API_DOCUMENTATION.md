# 🕉️ **Brahmakaal API - Complete Documentation**

## **The World's Most Advanced Vedic Astronomical Calculation Service**

**Version:** 2.0.0 | **Last Updated:** July 2025 | **Accuracy:** Professional Grade

---

## 📋 **Table of Contents**

1. [🌟 Overview](#overview)
2. [🚀 Quick Start](#quick-start)
3. [🔐 Authentication](#authentication)
4. [🌍 Localization](#localization)
5. [📍 Core APIs](#core-apis)
6. [⚡ Advanced APIs](#advanced-apis)
7. [📊 Response Formats](#response-formats)
8. [🏎️ Performance](#performance)
9. [📝 Examples](#examples)
10. [🔧 Error Handling](#error-handling)

---

## 🌟 **Overview**

Brahmakaal API provides **the most comprehensive Vedic astronomical calculations** available anywhere, with:

### **🎯 Core Features**
- **10 API Endpoints** covering all aspects of Vedic astronomy
- **95%+ Accuracy** validated against Drik Panchang and traditional sources
- **12 Indian Languages** with native script support
- **Sub-second Performance** for all calculations
- **Traditional + Modern** astronomical precision

### **📚 API Endpoints Summary**

| **Category** | **Endpoint** | **Purpose** | **Performance** |
|--------------|--------------|-------------|-----------------|
| **Core** | `/v1/panchang` | Complete lunar calendar | <2s |
| **Core** | `/v1/horoscope` | Birth chart generation | <3s |
| **Core** | `/v1/muhurta` | Auspicious timing | <5s |
| **Core** | `/v1/transits` | Planetary influences | <1s |
| **Core** | `/v1/ayanamsha` | Precession calculations | <0.5s |
| **Advanced** | `/v1/panchaka-periods` | 24-hour quality analysis | <60ms |
| **Advanced** | `/v1/udaya-lagna-periods` | Rising sign periods | <50ms |
| **Advanced** | `/v1/complete-muhurta-periods` | 8 traditional muhurtas | <60ms |
| **Advanced** | `/v1/inauspicious-periods` | Negative time periods | <50ms |
| **Advanced** | `/v1/extended-calendar-systems` | Multi-calendar support | <30ms |

---

## 🚀 **Quick Start**

### **1. Basic Panchang Request**

```bash
curl "https://kaal.brah.ma/v1/panchang?latitude=19.0760&longitude=72.8777&date=2025-07-25&time=12:00:00&timezone_offset=5.5"
```

### **2. With Hindi Localization**

```bash
curl "https://kaal.brah.ma/v1/panchang?latitude=19.0760&longitude=72.8777&date=2025-07-25&language=hi"
```

### **3. Human-Readable Times**

```bash
curl "https://kaal.brah.ma/v1/panchang?latitude=19.0760&longitude=72.8777&date=2025-07-25&human_readable_times=true"
```

---

## 🔐 **Authentication**

### **API Key Authentication**
```http
X-API-Key: your_api_key_here
```

### **JWT Bearer Token**
```http
Authorization: Bearer your_jwt_token
```

### **Subscription Tiers**

| **Tier** | **Requests/Min** | **Requests/Day** | **Features** | **Price** |
|----------|------------------|------------------|--------------|-----------|
| **Free** | 10 | 100 | Basic APIs, JSON export | Free |
| **Basic** | 60 | 5,000 | All APIs, localization | $29/month |
| **Premium** | 300 | 50,000 | Advanced features, webhooks | $99/month |
| **Enterprise** | 1,000 | 200,000 | Custom integration, SLA | $299/month |

---

## 🌍 **Localization**

### **Supported Languages**

| **Code** | **Language** | **Script** | **Status** |
|----------|--------------|------------|------------|
| `en` | English | Latin | ✅ Complete |
| `hi` | हिन्दी | Devanagari | ✅ Complete |
| `sa` | संस्कृत | Devanagari | ✅ Complete |
| `ta` | தமிழ் | Tamil | ✅ Complete |
| `bn` | বাংলা | Bengali | ✅ Complete |
| `gu` | ગુજરાતી | Gujarati | ✅ Complete |
| `mr` | मराठी | Devanagari | 🟡 Basic |
| `te` | తెలుగు | Telugu | 🟡 Basic |
| `kn` | ಕನ್ನಡ | Kannada | 🟡 Basic |
| `ml` | മലയാളം | Malayalam | 🟡 Basic |
| `pa` | ਪੰਜਾਬੀ | Gurmukhi | 🟡 Basic |
| `or` | ଓଡ଼ିଆ | Odia | 🟡 Basic |

### **Usage**
Add `?language=hi` to any endpoint for localized output.

### **Example Response with Hindi**
```json
{
  "tithi_name": "Shukla Pratipada",
  "tithi_name_native": "शुक्ल प्रतिपदा",
  "nakshatra": "Pushya",
  "nakshatra_native": "पुष्य",
  "localization": {
    "language": "hi",
    "language_name": "हिन्दी",
    "script": "Devanagari"
  }
}
```

---

## 📍 **Core APIs**

### **1. Panchang API** - `/v1/panchang`

**The flagship endpoint** - Complete lunar calendar calculations with 50+ parameters.

#### **Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `latitude` | float | ✅ | Latitude (-90 to 90) |
| `longitude` | float | ✅ | Longitude (-180 to 180) |
| `date` | string | ✅ | Date in YYYY-MM-DD format |
| `time` | string | ❌ | Time in HH:MM:SS (default: 12:00:00) |
| `timezone_offset` | float | ❌ | Hours from UTC (default: 0.0) |
| `ayanamsha` | string | ❌ | LAHIRI, RAMAN, KP (default: LAHIRI) |
| `elevation` | float | ❌ | Meters above sea level (default: 0.0) |
| `human_readable_times` | boolean | ❌ | Format times as "6:12 AM" (default: false) |
| `language` | string | ❌ | Language code for localization (default: en) |

#### **Response Fields** (60+ fields)

##### **Core Panchang Elements**
```json
{
  "tithi": 0.246,
  "tithi_name": "Shukla Pratipada",
  "tithi_end_time": {
    "end_time": "2025-07-26T00:02:56+05:30",
    "hours_remaining": 17,
    "minutes_remaining": 47,
    "percentage_complete": 24.7
  },
  "nakshatra": "Pushya",
  "nakshatra_lord": "Saturn",
  "yoga": 14.89,
  "yoga_name": "Vajra",
  "karana": 0.493,
  "karana_name": "Bava"
}
```

##### **Solar & Lunar Times**
```json
{
  "sunrise": "2025-07-25T06:14:05+05:30",
  "sunset": "2025-07-25T19:18:07+05:30",
  "solar_noon": "2025-07-25T12:46:06+05:30",
  "day_length": 13.067,
  "moonrise": "2025-07-25T06:41:04+05:30",
  "moonset": "2025-07-25T20:01:04+05:30",
  "moon_phase": "New Moon",
  "moon_illumination": 99.9
}
```

##### **Auspicious & Inauspicious Periods**
```json
{
  "rahu_kaal": {
    "start": "2025-07-25T10:44:05+05:30",
    "end": "2025-07-25T12:14:05+05:30"
  },
  "brahma_muhurta": {
    "start": "2025-07-25T04:38:05+05:30",
    "end": "2025-07-25T05:26:05+05:30"
  },
  "abhijit_muhurta": {
    "start": "2025-07-25T12:22:06+05:30",
    "end": "2025-07-25T13:10:06+05:30"
  }
}
```

##### **Planetary Positions**
```json
{
  "graha_positions": {
    "sun": {
      "longitude": 97.78,
      "latitude": -0.003,
      "rashi": "Karka",
      "nakshatra": "Pushya"
    },
    "moon": {
      "longitude": 100.74,
      "latitude": 3.55,
      "rashi": "Karka", 
      "nakshatra": "Pushya"
    }
  }
}
```

##### **Advanced Features**
```json
{
  "nakshatra_detailed": {
    "current_nakshatra": "Pushya",
    "current_pada": 3,
    "current_pada_name": "Third Pada",
    "position_in_pada_percent": 22.1,
    "pada_transitions": [...]
  },
  "ritu_ayana": {
    "drik_ritu": "Grishma",
    "drik_ayana": "Dakshinayana",
    "dinamana": "13:04:02",
    "ratrimana": "10:55:57",
    "madhyahna": "12:46"
  }
}
```

### **2. Horoscope API** - `/v1/horoscope`

Generate complete birth charts with house positions.

#### **Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `latitude` | float | ✅ | Birth location latitude |
| `longitude` | float | ✅ | Birth location longitude |
| `date` | string | ✅ | Birth date (YYYY-MM-DD) |
| `time` | string | ✅ | Birth time (HH:MM:SS) |
| `timezone_offset` | float | ✅ | Timezone offset |
| `ayanamsha` | string | ❌ | Ayanamsha system |
| `language` | string | ❌ | Localization language |

#### **Response**
```json
{
  "birth_details": {
    "birth_time": "1990-01-01T12:00:00+05:30",
    "location": "Mumbai, India",
    "ayanamsha_value": 23.85
  },
  "house_positions": {
    "1": ["Sun", "Mercury"],
    "2": ["Moon"],
    "5": ["Jupiter"],
    "7": ["Venus"],
    "10": ["Mars"],
    "11": ["Saturn"]
  },
  "planetary_positions": {
    "sun": {
      "longitude": 280.45,
      "house": 1,
      "rashi": "Makara",
      "nakshatra": "Dhanishtha",
      "retrograde": false
    }
  },
  "chart_analysis": {
    "ascendant": "Makara",
    "moon_sign": "Vrishabha",
    "sun_sign": "Makara",
    "birth_nakshatra": "Rohini"
  }
}
```

### **3. Muhurta API** - `/v1/muhurta`

Find auspicious timings for specific activities.

#### **Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `latitude` | float | ✅ | Location latitude |
| `longitude` | float | ✅ | Location longitude |
| `date` | string | ✅ | Target date |
| `activity` | string | ✅ | Activity type (wedding, business, travel, etc.) |
| `duration_hours` | float | ❌ | Required duration (default: 2) |
| `timezone_offset` | float | ❌ | Timezone offset |
| `language` | string | ❌ | Localization language |

#### **Activity Types**
- `wedding` - Marriage ceremonies
- `business` - Business launches  
- `travel` - Journey beginnings
- `construction` - Building starts
- `education` - Study/learning
- `medical` - Health procedures
- `general` - General activities

#### **Response**
```json
{
  "date": "2025-07-25",
  "activity": "wedding",
  "muhurta_periods": [
    {
      "start_time": "2025-07-25T06:30:00+05:30",
      "end_time": "2025-07-25T08:30:00+05:30",
      "quality_score": 85,
      "quality": "Excellent",
      "duration_minutes": 120,
      "description": "Highly auspicious period for wedding ceremonies",
      "favorable_factors": [
        "Shukla Paksha Tithi",
        "Favorable Nakshatra",
        "No Rahu Kaal"
      ]
    }
  ],
  "summary": {
    "total_periods": 3,
    "best_period": "06:30 - 08:30",
    "day_quality": "Excellent"
  }
}
```

---

## ⚡ **Advanced APIs**

### **1. Panchaka Periods** - `/v1/panchaka-periods`

24-hour analysis of time quality with detailed breakdowns.

#### **Response**
```json
{
  "date": "2025-07-25",
  "total_periods": 24,
  "panchaka_periods": [
    {
      "hour": 6,
      "type": "Mrityu Panchaka",
      "start_time": "2025-07-25T06:00:00+05:30",
      "end_time": "2025-07-25T07:00:00+05:30",
      "duration_minutes": 60,
      "description": "Death-related activities to be avoided",
      "recommended_activities": ["Meditation", "Prayer"],
      "severity": "High"
    }
  ],
  "summary": {
    "favorable_hours": 18,
    "unfavorable_hours": 6,
    "favorable_percentage": 75.0,
    "day_quality": "Good"
  }
}
```

### **2. Complete Muhurta Periods** - `/v1/complete-muhurta-periods`

All 8 traditional muhurta types calculated precisely.

#### **Response**
```json
{
  "date": "2025-07-25",
  "muhurta_periods": {
    "Brahma Muhurta": {
      "start_time": "2025-07-25T04:14:00+05:30",
      "end_time": "2025-07-25T04:56:00+05:30", 
      "duration_minutes": 48,
      "description": "Most auspicious time for spiritual practices",
      "benefits": ["Spiritual growth", "Mental clarity", "Divine connection"],
      "recommended_activities": ["Meditation", "Prayer", "Study of scriptures"]
    },
    "Abhijit Muhurta": {
      "start_time": "2025-07-25T12:00:00+05:30",
      "end_time": "2025-07-25T12:55:00+05:30",
      "duration_minutes": 48,
      "description": "Victory time - success in all endeavors",
      "benefits": ["Success assurance", "Victory in competitions", "Positive outcomes"]
    }
  },
  "summary": {
    "total_auspicious_minutes": 384,
    "day_quality": "Excellent",
    "recommendations": [
      "Start important work during Brahma Muhurta",
      "Schedule meetings during Abhijit Muhurta"
    ]
  }
}
```

### **3. Extended Calendar Systems** - `/v1/extended-calendar-systems`

Multiple traditional calendar systems integrated.

#### **Response**
```json
{
  "date": "2025-07-25",
  "extended_calendar_systems": {
    "gujarati_samvat": {
      "year": 2081,
      "month": "Shravana",
      "day": 10,
      "season": "Varsha"
    },
    "brihaspati_samvatsara": {
      "name": "Kalayukta", 
      "position_in_cycle": 27,
      "characteristics": {
        "nature": "Mixed results",
        "favorable_for": ["Education", "Learning"],
        "general_prediction": "Moderate year with learning opportunities"
      }
    },
    "era_systems": {
      "kali_yuga": {"year": 5126, "days": 1872416},
      "saka_era": {"year": 1947},
      "vikram_samvat": {"year": 2082},
      "bengali_san": {"year": 1432},
      "hijri": {"year": 1446}
    }
  }
}
```

---

## 📊 **Response Formats**

### **Standard JSON Response**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "calculation_time_ms": 45,
    "accuracy_level": "Professional",
    "api_version": "2.0.0"
  }
}
```

### **Error Response**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_COORDINATES",
    "message": "Latitude must be between -90 and 90 degrees",
    "details": "Provided latitude: 91.5"
  },
  "request_id": "req_123abc"
}
```

### **Localized Response**
```json
{
  "tithi_name": "Shukla Pratipada",
  "tithi_name_native": "शुक्ल प्रतिपदा", 
  "nakshatra": "Pushya",
  "nakshatra_native": "पुष्य",
  "localization": {
    "language": "hi",
    "language_name": "हिन्दी",
    "script": "Devanagari",
    "supported_languages": ["en", "hi", "sa", "ta", "bn", "gu", "mr", "te", "kn", "ml", "pa", "or"]
  }
}
```

---

## 🏎️ **Performance**

### **Response Times**
- **Core APIs**: 0.5s - 5s (complex calculations)
- **Advanced APIs**: 30ms - 100ms (lightning fast)
- **Cached Responses**: <10ms

### **Optimization Features**
- **Redis Caching**: Intelligent caching with 1-hour TTL
- **Database Connection Pooling**: Async PostgreSQL
- **CDN Distribution**: Global edge locations
- **Compression**: Gzip response compression

### **Rate Limiting**
Subscription-based with automatic scaling:
```http
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 299
X-RateLimit-Reset: 1627845600
```

---

## 📝 **Complete Examples**

### **1. Wedding Muhurta Planning**
```python
import requests

# Find auspicious wedding times
response = requests.get(
    "https://kaal.brah.ma/v1/muhurta",
    params={
        "latitude": 19.0760,
        "longitude": 72.8777,
        "date": "2025-12-15",
        "activity": "wedding",
        "duration_hours": 3,
        "timezone_offset": 5.5,
        "language": "hi"
    },
    headers={"X-API-Key": "your_api_key"}
)

wedding_times = response.json()
for period in wedding_times["muhurta_periods"]:
    if period["quality_score"] > 80:
        print(f"Excellent time: {period['start_time']} - {period['end_time']}")
```

### **2. Daily Panchang Widget**
```javascript
async function getDailyPanchang() {
    const response = await fetch(
        'https://kaal.brah.ma/v1/panchang?' +
        'latitude=28.6139&longitude=77.2090&' +
        'date=2025-07-25&human_readable_times=true&language=hi',
        {
            headers: {
                'X-API-Key': 'your_api_key'
            }
        }
    );
    
    const data = await response.json();
    
    // Display in your UI
    document.getElementById('tithi').textContent = data.tithi_name_native || data.tithi_name;
    document.getElementById('nakshatra').textContent = data.nakshatra_native || data.nakshatra;
    document.getElementById('sunrise').textContent = data.sunrise;
}
```

### **3. Business Opening Analysis**
```python
# Comprehensive analysis for business opening
endpoints = [
    "/v1/panchang",
    "/v1/complete-muhurta-periods", 
    "/v1/panchaka-periods",
    "/v1/inauspicious-periods"
]

date = "2025-08-15"
params = {
    "latitude": 12.9716,
    "longitude": 77.5946,
    "date": date,
    "timezone_offset": 5.5
}

analysis = {}
for endpoint in endpoints:
    response = requests.get(f"https://kaal.brah.ma{endpoint}", 
                          params=params, 
                          headers={"X-API-Key": "your_api_key"})
    analysis[endpoint] = response.json()

# Find best time
best_muhurta = max(analysis["/v1/complete-muhurta-periods"]["muhurta_periods"].items(),
                  key=lambda x: len(x[1]["benefits"]))

print(f"Best time for business opening: {best_muhurta[0]}")
```

---

## 🔧 **Error Handling**

### **HTTP Status Codes**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid API key)
- `403` - Forbidden (rate limit exceeded)
- `404` - Not Found (invalid endpoint)
- `500` - Internal Server Error

### **Error Response Structure**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "API rate limit exceeded",
    "details": "You have exceeded your plan's rate limit of 60 requests per minute",
    "retry_after": 60,
    "upgrade_url": "https://brah.ma/kaal/upgrade"
  },
  "request_id": "req_7x8y9z",
  "timestamp": "2025-07-25T12:00:00Z"
}
```

### **Common Error Codes**
- `INVALID_COORDINATES` - Latitude/longitude out of range
- `INVALID_DATE_FORMAT` - Date not in YYYY-MM-DD format
- `INVALID_TIME_FORMAT` - Time not in HH:MM:SS format
- `UNSUPPORTED_AYANAMSHA` - Invalid ayanamsha system
- `UNSUPPORTED_LANGUAGE` - Invalid language code
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `API_KEY_INVALID` - Invalid or expired API key
- `CALCULATION_FAILED` - Astronomical calculation error

---

## 🎯 **Best Practices**

### **1. Caching**
- Cache responses for 1 hour for same location/time
- Use ETags for conditional requests
- Implement exponential backoff for errors

### **2. Error Handling**
```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def safe_api_call(url, params):
    session = create_session()
    try:
        response = session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return None
```

### **3. Localization Integration**
```python
def get_localized_panchang(lat, lon, date, user_language="en"):
    supported_languages = ["en", "hi", "sa", "ta", "bn", "gu"]
    language = user_language if user_language in supported_languages else "en"
    
    params = {
        "latitude": lat,
        "longitude": lon, 
        "date": date,
        "language": language,
        "human_readable_times": True
    }
    
    return safe_api_call("https://kaal.brah.ma/v1/panchang", params)
```

---

## 🔗 **Additional Resources**

- **🎨 Frontend SDK**: [JavaScript/TypeScript SDK](https://github.com/brahmakaal/sdk-js)
- **🐍 Python SDK**: [Python SDK](https://github.com/brahmakaal/sdk-python)
- **📱 Mobile SDKs**: [React Native](https://github.com/brahmakaal/sdk-react-native) | [Flutter](https://github.com/brahmakaal/sdk-flutter)
- **🔧 Postman Collection**: [API Collection](https://postman.com/brahmakaal/workspace/brahmakaal-api)
- **📊 Status Page**: [System Status](https://status.brah.ma)
- **💬 Support**: [Discord Community](https://discord.gg/brahmakaal) | [iam@brah.ma](mailto:iam@brah.ma)

---

## 📄 **Changelog & Versioning**

### **Version 2.0.0** (July 2025)
- ✨ **New**: 12 Indian languages support
- ✨ **New**: 5 Advanced APIs with <100ms response times
- ✨ **New**: Extended calendar systems
- 🚀 **Performance**: 10x faster advanced calculations
- 🎯 **Accuracy**: 95%+ validation against Drik Panchang
- 🔧 **Developer Experience**: Comprehensive SDKs and examples

### **Version 1.0.0** (March 2025)
- 🎉 Initial release with 5 core APIs
- 🔐 JWT and API key authentication
- ⚡ Redis caching and PostgreSQL storage

---

**© 2025 Brahmakaal Technologies**  
*Empowering the world with authentic Vedic astronomical wisdom* 