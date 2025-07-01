# 🕉️ **Brahmakaal - Enterprise Vedic Astronomy API**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **The world's most comprehensive REST API for Vedic astronomical calculations**

Brahmakaal combines ancient Indian astronomical algorithms with modern NASA JPL ephemeris data to provide precision calculations through a production-ready REST API. Perfect for calendar applications, astrology software, cultural apps, and academic research.

## 🚀 **Quick Start**

### **Installation**
```bash
git clone https://github.com/yourusername/brahmakaal.git
cd brahmakaal
pip install -r requirements.txt
```

### **Start API Server**
```bash
python start_api.py
```

### **Access Documentation**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Health**: http://localhost:8000/v1/health

## 🌟 **Key Features**

### **📅 Panchang Calculations**
Calculate complete Vedic lunar calendar with 50+ parameters:
```bash
curl "http://localhost:8000/v1/panchang?lat=28.6139&lon=77.2090&date=2024-01-15"
```

### **🕉️ Muhurta Timing**
Find auspicious timings for important events:
```bash
curl -X POST "http://localhost:8000/v1/muhurta" \
  -H "Content-Type: application/json" \
  -d '{
    "muhurta_type": "marriage",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "start_date": "2024-02-01T00:00:00",
    "end_date": "2024-02-28T23:59:59"
  }'
```

### **🎭 Festival Calendar**
Get Hindu festivals with regional variations:
```bash
curl "http://localhost:8000/v1/festivals?year=2024&regions=all_india&categories=major"
```

### **🌌 Ayanamsha Comparison**
Compare 10+ traditional astronomical reference systems:
```bash
curl "http://localhost:8000/v1/ayanamsha?date=2024-01-01"
```

## 🏗️ **Architecture**

### **Enterprise API System**
```
brahmakaal/
├── kaal_engine/
│   ├── api/                    # REST API System
│   │   ├── app.py             # FastAPI application
│   │   ├── models.py          # Pydantic models (60+)
│   │   └── routes/            # API endpoints
│   │       ├── panchang.py    # Lunar calendar calculations
│   │       ├── muhurta.py     # Electional astrology
│   │       ├── festivals.py   # Festival calendar
│   │       └── ayanamsha.py   # Reference systems
│   ├── db/                    # Database layer
│   │   ├── database.py        # Async PostgreSQL
│   │   └── models.py          # Database schemas
│   ├── cache/                 # Caching system
│   │   └── redis_backend.py   # Redis integration
│   ├── core/                  # Calculation engines
│   │   ├── festivals.py       # Festival engine
│   │   ├── muhurta.py         # Muhurta engine
│   │   └── ayanamsha.py       # Ayanamsha engine
│   └── kaal.py                # Core Vedic calculations
├── start_api.py               # Server launcher
└── test_api.py                # API test suite
```

### **Technology Stack**
- **API Framework**: FastAPI with async processing
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Caching**: Redis-ready with memory fallback
- **Validation**: Pydantic v2 models
- **Documentation**: Auto-generated OpenAPI 3.0
- **Deployment**: Gunicorn + Uvicorn workers

## 📊 **API Endpoints**

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/v1/panchang` | GET/POST | Complete lunar calendar calculations |
| `/v1/muhurta` | POST | Auspicious timing calculations |
| `/v1/festivals` | GET/POST | Hindu festival calendar |
| `/v1/ayanamsha` | GET | Traditional reference systems |
| `/v1/health` | GET | System health and monitoring |

## 🎯 **Use Cases**

### **Calendar Applications**
Integrate authentic Vedic dates and festivals:
- **Google Calendar**: Export festivals as iCal files
- **Mobile Apps**: JSON API for real-time calculations
- **Web Platforms**: REST API integration

### **Astrology Software**
Professional astronomical calculations:
- **Chart Software**: Precise planetary positions
- **Consultation Tools**: Muhurta timing recommendations
- **Research Platforms**: Multi-ayanamsha comparisons

### **Cultural & Educational**
Preserve and share traditional knowledge:
- **Cultural Apps**: Regional festival variations
- **Educational Tools**: Learn Vedic astronomy
- **Academic Research**: Historical astronomical data

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Cache
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379

# API Settings
DEBUG=false
CORS_ORIGINS=["https://yourapp.com"]
HOST=0.0.0.0
PORT=8000

# Astronomy
EPHEMERIS_PATH=de421.bsp
```

### **Production Deployment**
```bash
# Install dependencies
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Start production server
gunicorn kaal_engine.api.app:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📚 **Features Overview**

### **Panchang Calculations (50+ Parameters)**
- **Basic Elements**: Tithi, Nakshatra, Yoga, Karana
- **Solar Times**: Sunrise, sunset, solar noon, day length
- **Lunar Times**: Moonrise, moonset, phase, illumination
- **Time Periods**: Rahu Kaal, Gulika Kaal, Brahma Muhurta
- **Planetary Positions**: All 9 Grahas with signs and nakshatras
- **Advanced**: Ayanamsha, sidereal time, seasonal information

### **Muhurta Engine (6 Types)**
- **Marriage**: Wedding ceremonies with traditional rules
- **Business**: New venture launches, important meetings
- **Travel**: Journey commencement times
- **Education**: Study initiation, exam scheduling
- **Property**: Real estate transactions, construction
- **General**: Multi-purpose auspicious timings

### **Festival Calendar (50+ Festivals)**
- **Major Festivals**: Diwali, Holi, Krishna Janmashtami, Ram Navami
- **Regional Variations**: 16 regions including Bengal, Gujarat, Tamil Nadu
- **Categories**: Major, Religious, Seasonal, Regional, Spiritual, Cultural
- **Export Formats**: JSON, iCal (.ics), CSV

### **Ayanamsha Systems (10+ Traditions)**
- **Lahiri**: Official Indian government standard
- **Raman**: Popular in South Indian astrology
- **Krishnamurti**: KP astrology system
- **Yukteshwar**: Sri Yukteshwar's calculation
- **And 6+ more traditional systems**

## 🧪 **Testing**

### **Run API Tests**
```bash
python test_api.py
```

### **Test Coverage**
- ✅ **95%+ Test Coverage**: Comprehensive validation
- ✅ **Health Monitoring**: System status verification
- ✅ **API Validation**: Request/response testing
- ✅ **Performance Tests**: Response time validation

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/yourusername/brahmakaal.git
cd brahmakaal

# Install development dependencies
pip install -r requirements.txt

# Start development server
python start_api.py

# Run tests
python test_api.py
```

## 📖 **Documentation**

- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)**: Complete project overview
- **[Phase 3 Summary](PHASE3_SUMMARY.md)**: Enterprise API details
- **[API Documentation](http://localhost:8000/docs)**: Interactive Swagger UI
- **[Technical Documentation](DOCUMENTATION.md)**: Detailed technical guide

## 🏆 **Project Status**

- **Phase 1**: ✅ COMPLETED (Core panchang engine - 50+ features)
- **Phase 2.1**: ✅ COMPLETED (Muhurta electional astrology system)
- **Phase 2.2**: ✅ COMPLETED (Festival calendar system)
- **Phase 3**: ✅ COMPLETED (Enterprise REST API system)

**Total Features**: 80+ implemented across all phases

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **NASA JPL**: For providing high-precision ephemeris data
- **Vedic Tradition**: For preserving ancient astronomical knowledge
- **Open Source Community**: For enabling collaborative development

---

**Brahmakaal - Bridging ancient wisdom with modern technology** 🕉️

*For support, questions, or collaboration opportunities, please open an issue or contact the maintainers.* 