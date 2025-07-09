# Brahmakaal API Documentation (Phase 1-4)
**Complete API Reference for Frontend Development**

## Base URL
- **Production**: `https://your-api-domain.com`
- **Local Development**: `http://localhost:8000`

## Authentication
All API endpoints require authentication using Bearer tokens:
```
Authorization: Bearer YOUR_API_TOKEN
```

## API Endpoints Overview

### 1. Health & Status
#### `/v1/health` - Health Check
- **Method**: GET
- **Auth**: Not required
- **Description**: Check API service status
- **Response**:
```json
{
  "status": "healthy",
  "version": "4.0.0",
  "uptime_seconds": 3600,
  "database_connected": true,
  "cache_connected": true,
  "ephemeris_loaded": true,
  "timestamp": "2025-07-09T12:00:00Z"
}
```

### 2. Authentication Endpoints

#### `/v1/auth/register` - User Registration
- **Method**: POST
- **Request**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "securePassword123",
  "full_name": "Full Name"
}
```
- **Response**:
```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-07-09T12:00:00Z"
}
```

#### `/v1/auth/login` - User Login
- **Method**: POST
- **Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```
- **Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here"
}
```

#### `/v1/auth/api-keys` - Manage API Keys
- **GET**: List user's API keys
- **POST**: Create new API key
- **DELETE**: Delete API key

### 3. Panchang (Lunar Calendar) Endpoints

#### `/v1/panchang` - Basic Panchang Calculation
- **Methods**: GET, POST
- **Parameters**:
  - `latitude`: float (-90 to 90)
  - `longitude`: float (-180 to 180)
  - `date`: string (YYYY-MM-DD, optional - defaults to today)
  - `time`: string (HH:MM:SS, optional - defaults to 12:00:00)
  - `elevation`: float (meters, optional - defaults to 0)
  - `ayanamsha`: string (LAHIRI, RAMAN, KRISHNAMURTI, etc.)
  - `timezone_offset`: float (-12 to 12)

- **Example Request**:
```bash
GET /v1/panchang?latitude=28.6139&longitude=77.209&date=2025-07-09&time=12:00:00&timezone_offset=5.5
```

- **Response** (60+ parameters):
```json
{
  "tithi": 29.584,
  "tithi_name": "Krishna Chaturdashi",
  "tithi_end_time": {
    "end_time": "2025-07-09T14:30:00+05:30",
    "hours_remaining": 2,
    "minutes_remaining": 30,
    "percentage_complete": 75.5
  },
  "nakshatra": "Ashwini",
  "nakshatra_lord": "Ketu",
  "nakshatra_end_time": {
    "end_time": "2025-07-09T18:45:00+05:30",
    "hours_remaining": 6,
    "minutes_remaining": 45,
    "percentage_complete": 45.2
  },
  "yoga": 26.625,
  "yoga_name": "Vaidhriti",
  "karana": 59.168,
  "karana_name": "Balava",
  "sunrise": "2025-07-09T05:34:00+05:30",
  "sunset": "2025-07-09T19:16:00+05:30",
  "solar_noon": "2025-07-09T12:25:00+05:30",
  "day_length": 13.7,
  "moonrise": "2025-07-09T03:15:00+05:30",
  "moonset": "2025-07-09T17:45:00+05:30",
  "moon_phase": "Waning Crescent",
  "moon_illumination": 15.3,
  "rahu_kaal": {
    "start": "2025-07-09T13:30:00+05:30",
    "end": "2025-07-09T15:00:00+05:30"
  },
  "gulika_kaal": {
    "start": "2025-07-09T10:30:00+05:30",
    "end": "2025-07-09T12:00:00+05:30"
  },
  "brahma_muhurta": {
    "start": "2025-07-09T04:30:00+05:30",
    "end": "2025-07-09T05:18:00+05:30"
  },
  "graha_positions": {
    "sun": {
      "longitude": 107.23,
      "latitude": 0.0,
      "rashi": "Cancer",
      "nakshatra": "Pushya"
    },
    "moon": {
      "longitude": 15.67,
      "latitude": -2.45,
      "rashi": "Aries",
      "nakshatra": "Ashwini"
    }
  },
  "traditional_years": {
    "vikram_samvat": 2082,
    "shaka_samvat": 1947,
    "kali_yuga": 5127,
    "bengali_san": 1432,
    "tamil_year": "Rakshasa"
  },
  "tarabala": {
    "tarabala": "Sampat",
    "tarabala_number": 2,
    "tarabala_result": "Favorable",
    "chandrabala": "Good",
    "chandrabala_points": 4
  },
  "shool_data": {
    "shool_direction": "East",
    "shool_deity": "Indra",
    "nivas": "Palace",
    "favorable_direction": "North"
  },
  "panchaka": {
    "panchaka_type": "Agni Panchaka",
    "panchaka_description": "Fire element dominant",
    "favorable_activities": ["Spiritual practices", "Fire ceremonies"],
    "activities_to_avoid": ["Construction work"]
  },
  "ayanamsha": 24.12,
  "sidereal_time": 8.45,
  "season": "Monsoon",
  "calculation_time_ms": 45,
  "location": {
    "latitude": 28.6139,
    "longitude": 77.209,
    "elevation": 0
  },
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

#### `/v1/panchang/personalized` - Personalized Panchang
- **Method**: POST
- **Description**: Panchang with birth chart integration and personalized insights
- **Request**:
```json
{
  "birth_data": {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "birth_timezone": "Asia/Kolkata",
    "birth_location_name": "New Delhi, India"
  },
  "target_date": "2025-07-09",
  "target_time": "12:00:00",
  "location_latitude": 28.6139,
  "location_longitude": 77.2090,
  "ayanamsha": "LAHIRI",
  "include_transit_analysis": true,
  "recommendation_depth": "standard"
}
```

- **Response**: Includes standard panchang + personalized insights:
```json
{
  "basic_panchang": { /* Standard panchang response */ },
  "personalized_insights": {
    "favorable_periods": [
      {
        "start_time": "06:00",
        "end_time": "08:00",
        "activity_type": "meditation",
        "strength": "high",
        "reason": "Moon transiting favorable nakshatra",
        "transit_influence": "Jupiter trine natal Moon"
      }
    ],
    "unfavorable_periods": [
      {
        "start_time": "13:30",
        "end_time": "15:00",
        "activity_type": "important_decisions",
        "strength": "high",
        "reason": "Rahu Kaal period"
      }
    ],
    "daily_guidance": "Good day for spiritual practices and learning. Avoid major decisions during Rahu Kaal.",
    "recommended_activities": ["Study", "Meditation", "Creative work"],
    "avoid_activities": ["Legal matters", "Important meetings"],
    "energy_level": "medium",
    "emotional_state": "balanced"
  },
  "transit_highlights": [
    {
      "transit_type": "trine",
      "transiting_planet": "Jupiter",
      "natal_planet": "Moon",
      "aspect_type": "trine",
      "impact": "beneficial",
      "duration": "3 days"
    }
  ],
  "birth_chart_summary": {
    "ascendant_sign": "Virgo",
    "moon_sign": "Taurus",
    "sun_sign": "Taurus"
  },
  "calculation_time_ms": 120,
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

### 4. Muhurta (Auspicious Timing) Endpoints

#### `/v1/muhurta` - Find Auspicious Times
- **Method**: POST
- **Description**: Find optimal times for specific activities
- **Request**:
```json
{
  "muhurta_type": "business",
  "latitude": 28.6139,
  "longitude": 77.209,
  "start_date": "2025-07-09T00:00:00Z",
  "end_date": "2025-07-12T23:59:59Z",
  "duration_minutes": 120,
  "min_quality": "good",
  "max_results": 10
}
```

- **Response**:
```json
{
  "request_summary": {
    "muhurta_type": "business",
    "search_period": "4 days",
    "location": "28.6139°N, 77.209°E"
  },
  "results": [
    {
      "datetime": "2025-07-10T10:30:00+05:30",
      "quality": "excellent",
      "score": 87.5,
      "description": "Excellent business muhurta during Pushya nakshatra with strong Mercury",
      "factors": {
        "tithi": {
          "tithi_number": 2,
          "tithi_name": "Shukla Dvitiya",
          "favorable": true
        },
        "nakshatra": {
          "nakshatra": "Pushya",
          "favorable": true
        },
        "planetary_analysis": {
          "mercury": {
            "strength": 85.0,
            "impact": 15
          }
        }
      },
      "recommendations": ["Ideal for new business ventures", "Good for signing contracts"],
      "warnings": []
    }
  ],
  "total_found": 15,
  "calculation_time_ms": 2500,
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

#### `/v1/muhurta/personalized` - Personalized Muhurta
- **Method**: POST
- **Description**: Personalized auspicious timing based on birth chart
- **Request**: Similar to standard muhurta + birth_data
- **Response**: Includes personalized scoring and recommendations

#### `/v1/muhurta/types` - Available Muhurta Types
- **Method**: GET
- **Response**:
```json
{
  "marriage": {
    "name": "Marriage",
    "description": "Wedding ceremonies with comprehensive traditional rules",
    "typical_duration": "2-4 hours",
    "key_factors": ["tithi", "nakshatra", "vara", "guru_chandal_check"]
  },
  "business": {
    "name": "Business",
    "description": "New venture launches, shop openings, important meetings",
    "typical_duration": "1-2 hours"
  },
  "travel": {
    "name": "Travel",
    "description": "Journey commencement, pilgrimage start"
  },
  "education": {
    "name": "Education",
    "description": "Study initiation, exam scheduling"
  },
  "property": {
    "name": "Property",
    "description": "Real estate transactions, house warming"
  },
  "general": {
    "name": "General",
    "description": "Multi-purpose auspicious timings"
  }
}
```

### 5. Horoscope/Natal Chart Endpoints

#### `/v1/horoscope/natal-chart` - Generate Birth Chart
- **Method**: POST
- **Request**:
```json
{
  "birth_data": {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "birth_timezone": "Asia/Kolkata",
    "birth_location_name": "New Delhi, India"
  },
  "ayanamsha": "LAHIRI",
  "include_insights": true,
  "include_yogas": true
}
```

- **Response**:
```json
{
  "birth_details": { /* Birth data used */ },
  "chart_data": {
    "house_positions": {
      "1": ["Mars"],
      "2": ["Venus", "Mercury"],
      "10": ["Sun"]
    }
  },
  "planetary_positions": {
    "sun": {
      "sign": "Taurus",
      "degree": 23.45,
      "house": 10,
      "nakshatra": "Mrigashira",
      "dignity": "neutral",
      "retrograde": false
    },
    "moon": {
      "sign": "Cancer",
      "degree": 15.23,
      "house": 12,
      "nakshatra": "Pushya",
      "dignity": "exalted",
      "retrograde": false
    }
  },
  "house_cusps": [67.23, 98.45, 129.67],
  "ascendant": {
    "sign": "Leo",
    "degree": 12.34,
    "house": 1,
    "nakshatra": "Magha"
  },
  "key_insights": {
    "personality_traits": ["Leadership qualities", "Creative nature"],
    "strengths": ["Strong communication", "Artistic abilities"],
    "challenges": ["Emotional sensitivity", "Perfectionist tendencies"],
    "life_purpose": "Creative expression and helping others"
  },
  "planetary_yogas": [
    {
      "name": "Gaja Kesari Yoga",
      "strength": "strong",
      "description": "Moon and Jupiter in mutual kendras",
      "effects": ["Wisdom", "Prosperity", "Fame"]
    }
  ],
  "planetary_strengths": {
    "sun": 75.5,
    "moon": 85.2,
    "mercury": 68.3
  },
  "calculation_time_ms": 156,
  "ayanamsha_used": "LAHIRI",
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

### 6. Transit Analysis Endpoints

#### `/v1/transits/daily` - Daily Transit Analysis
- **Method**: POST
- **Description**: Analyze daily planetary transits against birth chart
- **Request**:
```json
{
  "birth_data": {
    "birth_date": "1990-05-15",
    "birth_time": "14:30:00",
    "birth_latitude": 28.6139,
    "birth_longitude": 77.2090,
    "birth_timezone": "Asia/Kolkata"
  },
  "analysis_date": "2025-07-09",
  "ayanamsha": "LAHIRI",
  "include_predictions": true,
  "transit_types": ["all"]
}
```

- **Response**:
```json
{
  "analysis_date": "2025-07-09",
  "birth_chart_reference": {
    "ascendant": "Leo",
    "moon_sign": "Cancer",
    "sun_sign": "Taurus"
  },
  "active_transits": [
    {
      "transiting_planet": "Jupiter",
      "aspect_type": "trine",
      "natal_planet": "Moon",
      "exactness": "exact",
      "peak_date": "2025-07-09",
      "duration_days": 5,
      "impact_rating": "highly beneficial",
      "life_areas": ["emotions", "family", "home"],
      "recommendations": ["Good time for family decisions", "Favorable for property matters"]
    }
  ],
  "daily_summary": "Favorable day with supportive Jupiter transit to natal Moon. Good for emotional matters and family decisions.",
  "key_influences": [
    "Jupiter trine Moon: Emotional stability and wisdom",
    "Venus in 7th house: Relationship harmony"
  ],
  "timing_recommendations": {
    "best_times": {
      "important_decisions": "10:00-12:00",
      "meetings": "14:00-16:00",
      "creative_work": "06:00-08:00"
    },
    "avoid_times": {
      "conflicts": "13:30-15:00",
      "major_purchases": "18:00-20:00"
    }
  },
  "calculation_time_ms": 89,
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

### 7. Festival Calendar Endpoints

#### `/v1/festivals` - Hindu Festival Calendar
- **Methods**: GET, POST
- **Parameters**:
  - `year`: int (1900-2100)
  - `month`: int (1-12, optional)
  - `regions`: string (comma-separated)
  - `categories`: string (comma-separated)
  - `export_format`: string (json, ical, csv)

- **Example**:
```bash
GET /v1/festivals?year=2025&month=7&regions=all_india&categories=major,religious&export_format=json
```

- **Response**:
```json
{
  "request_summary": {
    "year": 2025,
    "month": 7,
    "regions": ["all_india"],
    "categories": ["major", "religious"]
  },
  "festivals": [
    {
      "name": "Guru Purnima",
      "english_name": "Full Moon of the Guru",
      "date": "2025-07-13",
      "category": "religious",
      "regions": ["all_india"],
      "description": "Day to honor spiritual teachers and gurus",
      "alternative_names": ["Vyasa Purnima"],
      "duration_days": 1,
      "observance_time": "full_day"
    }
  ],
  "total_festivals": 8,
  "export_url": null,
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

#### `/v1/festivals/regions` - Available Regions
- **Method**: GET
- **Response**: List of supported regions

#### `/v1/festivals/categories` - Festival Categories
- **Method**: GET
- **Response**: List of festival categories

### 8. Ayanamsha Comparison Endpoints

#### `/v1/ayanamsha/compare` - Compare Ayanamsha Systems
- **Method**: POST
- **Request**:
```json
{
  "date": "2025-07-09",
  "systems": ["LAHIRI", "RAMAN", "KRISHNAMURTI"]
}
```

- **Response**:
```json
{
  "date": "2025-07-09",
  "julian_day": 2460500.5,
  "ayanamsha_values": {
    "LAHIRI": 24.1234,
    "RAMAN": 22.5678,
    "KRISHNAMURTI": 23.8901
  },
  "differences_from_lahiri": {
    "RAMAN": -1.5556,
    "KRISHNAMURTI": -0.2333
  },
  "systems_info": {
    "LAHIRI": "Government of India standard",
    "RAMAN": "B.V. Raman's system"
  },
  "request_timestamp": "2025-07-09T12:00:00Z"
}
```

#### `/v1/ayanamsha/systems` - Available Systems
- **Method**: GET
- **Response**: List of supported ayanamsha systems

### 9. Analytics Endpoints (Admin/Premium)

#### `/v1/analytics/dashboard` - Usage Dashboard
- **Method**: GET
- **Auth**: Admin or Premium subscription
- **Response**: Usage statistics and insights

#### `/v1/analytics/usage` - Personal Usage Stats
- **Method**: GET
- **Response**: User's API usage statistics

### 10. Webhook Management (Premium+)

#### `/v1/webhooks/endpoints` - Manage Webhooks
- **GET**: List webhook endpoints
- **POST**: Create webhook endpoint
- **DELETE**: Remove webhook endpoint

### Error Responses

All endpoints return errors in this format:
```json
{
  "error": "ValidationError",
  "message": "Invalid latitude value",
  "details": {
    "field": "latitude",
    "value": 91.0,
    "constraint": "must be between -90 and 90"
  },
  "timestamp": "2025-07-09T12:00:00Z",
  "request_id": "req_123456"
}
```

### Rate Limits

| Subscription Tier | Requests/Minute | Requests/Day | Requests/Month |
|------------------|-----------------|--------------|----------------|
| Free             | 10              | 1,000        | 10,000         |
| Basic            | 60              | 10,000       | 100,000        |
| Premium          | 300             | 50,000       | 500,000        |
| Enterprise       | 1,000           | 200,000      | 2,000,000      |

### Response Times

- **Panchang**: 50-100ms
- **Muhurta**: 1-3 seconds
- **Horoscope**: 30-150ms  
- **Transits**: 60-120ms
- **Festivals**: 20-50ms

### Important Notes for Frontend

1. **Timezone Handling**: All datetime responses include proper timezone information (+05:30 for IST)
2. **Date Format**: Use ISO 8601 format (YYYY-MM-DD) for dates
3. **Time Format**: Use HH:MM:SS format for times
4. **Error Handling**: Always check for error responses and handle appropriately
5. **Caching**: Responses include cache headers for optimization
6. **Pagination**: Large result sets include pagination parameters
7. **Rate Limiting**: Monitor rate limit headers in responses

### SDK Examples

```javascript
// JavaScript example
const response = await fetch('/v1/panchang', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  params: {
    latitude: 28.6139,
    longitude: 77.209,
    date: '2025-07-09',
    timezone_offset: 5.5
  }
});

const panchang = await response.json();
console.log('Sunrise:', panchang.sunrise);
```

```python
# Python example
import requests

headers = {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
}

params = {
    'latitude': 28.6139,
    'longitude': 77.209,
    'date': '2025-07-09',
    'timezone_offset': 5.5
}

response = requests.get('https://api.brahmakaal.com/v1/panchang', 
                       headers=headers, params=params)
panchang = response.json()
print(f"Sunrise: {panchang['sunrise']}")
```

This comprehensive API documentation covers all Phase 1-4 endpoints with detailed examples for frontend integration. 