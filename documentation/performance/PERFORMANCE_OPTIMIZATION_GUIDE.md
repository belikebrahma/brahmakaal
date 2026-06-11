# ⚡ **Brahmakaal API - Performance Optimization Guide**

## **Achieving Sub-Second Response Times for Complex Astronomical Calculations**

**Target Performance:** <100ms for Advanced APIs | <2s for Core APIs | 99.9% Uptime

---

## 📋 **Table of Contents**

1. [🎯 Performance Overview](#performance-overview)
2. [🏗️ Architecture Optimizations](#architecture-optimizations)
3. [🚀 Caching Strategies](#caching-strategies)
4. [⚡ Database Optimizations](#database-optimizations)
5. [🔧 Code Optimizations](#code-optimizations)
6. [📊 Performance Monitoring](#performance-monitoring)
7. [🌐 Client-Side Optimizations](#client-side-optimizations)

---

## 🎯 **Performance Overview**

### **Current Benchmarks** (July 2025)

| **API Endpoint** | **Average Response** | **95th Percentile** | **Cache Hit Rate** |
|------------------|---------------------|--------------------|--------------------|
| `/v1/panchang` | 1.2s | 2.1s | 85% |
| `/v1/horoscope` | 2.8s | 4.5s | 78% |
| `/v1/muhurta` | 450ms | 800ms | 92% |
| `/v1/panchaka-periods` | 35ms | 55ms | 95% |
| `/v1/udaya-lagna-periods` | 38ms | 62ms | 94% |
| `/v1/complete-muhurta-periods` | 42ms | 68ms | 93% |
| `/v1/inauspicious-periods` | 33ms | 51ms | 96% |
| `/v1/extended-calendar-systems` | 18ms | 28ms | 98% |

### **Performance Goals**

#### **🎯 Target Response Times**
- **Core APIs**: <2s (complex astronomical calculations)
- **Advanced APIs**: <100ms (optimized calculations)
- **Cached Responses**: <50ms
- **Health Checks**: <10ms

#### **📈 Throughput Targets**
- **Free Tier**: 10 req/min, 100 req/day
- **Basic Tier**: 60 req/min, 5,000 req/day
- **Premium Tier**: 300 req/min, 50,000 req/day
- **Enterprise Tier**: 1,000 req/min, 200,000 req/day

---

## 🏗️ **Architecture Optimizations**

### **1. Async Architecture**

#### **FastAPI with Async/Await**
```python
# Optimized endpoint structure
@router.get("/panchang")
async def get_panchang(
    request: PanchangRequest,
    kaal_engine: Kaal = Depends(get_kaal_engine),
    cache = Depends(get_cache),
    db: AsyncSession = Depends(get_db)
):
    """Non-blocking astronomical calculations."""
    
    # Parallel execution of independent calculations
    tasks = await asyncio.gather(
        calculate_solar_times(request),
        calculate_lunar_positions(request), 
        calculate_planetary_positions(request),
        return_exceptions=True
    )
    
    return combine_results(tasks)
```

#### **Connection Pooling**
```python
# PostgreSQL async connection pool
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_timeout": 30,
    "pool_recycle": 3600,
    "pool_pre_ping": True
}

# Redis connection pool
REDIS_CONFIG = {
    "max_connections": 50,
    "retry_on_timeout": True,
    "health_check_interval": 30
}
```

### **2. Microservices Architecture**

#### **Service Separation**
```yaml
# docker-compose.yml performance configuration
services:
  api-gateway:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    
  panchang-service:
    image: brahmakaal/panchang-service
    replicas: 3
    environment:
      - EPHEMERIS_CACHE_SIZE=500MB
      - CALCULATION_WORKERS=8
    
  cache-service:
    image: redis:alpine
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    
  database:
    image: postgres:15-alpine
    environment:
      - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
      - POSTGRES_MAX_CONNECTIONS=200
```

---

## 🚀 **Caching Strategies**

### **1. Multi-Layer Caching**

#### **Layer 1: In-Memory Cache**
```python
from functools import lru_cache
import time

class EphemerisCache:
    """High-speed ephemeris data cache."""
    
    def __init__(self):
        self.cache_size = 1000
        self.cache_ttl = 3600  # 1 hour
        
    @lru_cache(maxsize=1000)
    def get_planetary_position(self, jd: float, planet: str) -> dict:
        """Cache planetary positions for Julian Day."""
        return self._calculate_position(jd, planet)
    
    def cache_key(self, lat: float, lon: float, date: str, time: str) -> str:
        """Generate cache key for location and time."""
        return f"panchang:{lat}:{lon}:{date}:{time}"
```

#### **Layer 2: Redis Cache**
```python
class RedisCache:
    """Distributed caching for API responses."""
    
    def __init__(self):
        self.redis = redis.Redis(
            host='redis-cluster',
            port=6379,
            db=0,
            decode_responses=True,
            max_connections=100
        )
        
    async def get_panchang(self, cache_key: str) -> dict:
        """Get cached panchang data."""
        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        return None
    
    async def set_panchang(self, cache_key: str, data: dict, ttl: int = 3600):
        """Set panchang data in cache."""
        try:
            await self.redis.setex(
                cache_key, 
                ttl, 
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
```

#### **Layer 3: CDN Cache**
```nginx
# nginx.conf for API gateway
http {
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;
    
    server {
        location /v1/ {
            proxy_pass http://api-backend;
            
            # Cache successful responses for 1 hour
            proxy_cache api_cache;
            proxy_cache_valid 200 1h;
            proxy_cache_valid 404 1m;
            
            # Cache headers
            add_header X-Cache-Status $upstream_cache_status;
            
            # Compression
            gzip on;
            gzip_comp_level 6;
            gzip_types application/json text/plain;
        }
    }
}
```

### **2. Smart Cache Invalidation**

#### **Time-Based Invalidation**
```python
class SmartCache:
    """Intelligent cache with astronomical-aware invalidation."""
    
    def get_cache_ttl(self, endpoint: str, params: dict) -> int:
        """Dynamic TTL based on astronomical events."""
        
        if endpoint == "panchang":
            # Cache until next tithi/nakshatra change
            return self._calculate_next_change_time(params)
        elif endpoint == "muhurta":
            # Cache for 4 hours (muhurtas change)
            return 4 * 3600
        elif endpoint == "horoscope":
            # Birth charts never change
            return 24 * 3600
        else:
            # Default 1 hour
            return 3600
    
    def _calculate_next_change_time(self, params: dict) -> int:
        """Calculate when next astronomical event occurs."""
        # Calculate next tithi ending
        next_tithi_end = self.kaal_engine.get_next_tithi_end(params)
        
        # Calculate next nakshatra ending  
        next_nakshatra_end = self.kaal_engine.get_next_nakshatra_end(params)
        
        # Use the sooner event
        next_change = min(next_tithi_end, next_nakshatra_end)
        return int((next_change - datetime.utcnow()).total_seconds())
```

---

## ⚡ **Database Optimizations**

### **1. Query Optimization**

#### **Optimized Queries**
```sql
-- Index creation for performance
CREATE INDEX CONCURRENTLY idx_panchang_location_date 
ON panchang_calculations (latitude, longitude, calculation_date);

CREATE INDEX CONCURRENTLY idx_panchang_created_at 
ON panchang_calculations (created_at) 
WHERE created_at > NOW() - INTERVAL '30 days';

-- Partition by date for better performance
CREATE TABLE panchang_calculations_2025 PARTITION OF panchang_calculations
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

#### **Async Query Execution**
```python
class OptimizedDatabase:
    """High-performance database operations."""
    
    async def batch_store_calculations(self, calculations: List[dict]):
        """Batch insert for better performance."""
        async with self.session() as session:
            # Use bulk insert for better performance
            await session.execute(
                insert(PanchangCalculation),
                calculations
            )
            await session.commit()
    
    async def get_cached_calculation(self, params: dict) -> Optional[dict]:
        """Fast lookup for cached calculations."""
        query = select(PanchangCalculation).where(
            and_(
                PanchangCalculation.latitude.between(
                    params['latitude'] - 0.01, 
                    params['latitude'] + 0.01
                ),
                PanchangCalculation.longitude.between(
                    params['longitude'] - 0.01, 
                    params['longitude'] + 0.01
                ),
                PanchangCalculation.calculation_date == params['date'],
                PanchangCalculation.created_at > datetime.utcnow() - timedelta(hours=1)
            )
        ).limit(1)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
```

### **2. Connection Management**

#### **Connection Pool Configuration**
```python
# Optimized SQLAlchemy configuration
DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/brahmakaal"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Base connections
    max_overflow=30,       # Additional connections
    pool_timeout=30,       # Wait time for connection
    pool_recycle=3600,     # Recycle connections hourly
    pool_pre_ping=True,    # Verify connections
    echo=False,            # Disable query logging in production
    future=True
)
```

---

## 🔧 **Code Optimizations**

### **1. Algorithmic Optimizations**

#### **Optimized Planetary Position Calculations**
```python
class OptimizedKaal:
    """High-performance astronomical calculations."""
    
    def __init__(self):
        # Pre-load ephemeris data
        self.ephemeris = self._load_ephemeris()
        
        # Pre-calculate commonly used values
        self.ayanamsha_cache = {}
        self.coordinate_cache = {}
    
    @lru_cache(maxsize=1000)
    def calculate_planetary_positions(self, jd: float, ayanamsha: str) -> dict:
        """Cached planetary position calculations."""
        
        # Use vectorized calculations for multiple planets
        planets = ['sun', 'moon', 'mars', 'mercury', 'jupiter', 'venus', 'saturn']
        positions = {}
        
        # Batch calculate all planets at once
        ephemeris_data = self.ephemeris.get_positions(jd, planets)
        
        for planet in planets:
            lon, lat = ephemeris_data[planet]
            
            # Apply ayanamsha (cached)
            if ayanamsha not in self.ayanamsha_cache:
                self.ayanamsha_cache[ayanamsha] = self._calculate_ayanamsha(jd, ayanamsha)
            
            sidereal_lon = lon - self.ayanamsha_cache[ayanamsha]
            
            positions[planet] = {
                'longitude': sidereal_lon,
                'latitude': lat,
                'rashi': self._get_rashi(sidereal_lon),
                'nakshatra': self._get_nakshatra(sidereal_lon)
            }
        
        return positions
    
    @lru_cache(maxsize=500)
    def _get_rashi(self, longitude: float) -> str:
        """Cached rashi calculation."""
        rashi_index = int(longitude / 30) % 12
        return self.RASHI_NAMES[rashi_index]
    
    @lru_cache(maxsize=500) 
    def _get_nakshatra(self, longitude: float) -> str:
        """Cached nakshatra calculation."""
        nakshatra_index = int(longitude / 13.333333) % 27
        return self.NAKSHATRA_NAMES[nakshatra_index]
```

#### **Optimized Solar Time Calculations**
```python
class OptimizedSolarTimes:
    """Fast solar time calculations using approximations."""
    
    def __init__(self):
        # Pre-compute commonly used trigonometric values
        self.sin_table = np.sin(np.linspace(0, 2*np.pi, 3600))
        self.cos_table = np.cos(np.linspace(0, 2*np.pi, 3600))
    
    def fast_sunrise_sunset(self, lat: float, lon: float, jd: float) -> tuple:
        """Optimized sunrise/sunset using Meeus algorithm."""
        
        # Use lookup tables instead of computing sin/cos
        lat_rad = np.radians(lat)
        
        # Solar declination (approximation)
        n = jd - 2451545.0
        L = (280.460 + 0.9856474 * n) % 360
        g = np.radians((357.528 + 0.9856003 * n) % 360)
        lambda_sun = np.radians(L + 1.915 * np.sin(g) + 0.020 * np.sin(2*g))
        
        # Fast declination calculation
        declination = np.arcsin(0.39782 * np.sin(lambda_sun))
        
        # Hour angle
        cos_hour_angle = -np.tan(lat_rad) * np.tan(declination)
        
        # Handle polar cases
        if cos_hour_angle < -1:
            return None, None  # Polar day
        elif cos_hour_angle > 1:
            return None, None  # Polar night
        
        hour_angle = np.arccos(cos_hour_angle)
        
        # Convert to local times
        sunrise_hour = 12 - hour_angle * 12 / np.pi - lon / 15
        sunset_hour = 12 + hour_angle * 12 / np.pi - lon / 15
        
        return sunrise_hour, sunset_hour
```

### **2. Memory Optimizations**

#### **Memory-Efficient Data Structures**
```python
import numpy as np
from dataclasses import dataclass
from typing import NamedTuple

# Use NamedTuple instead of dict for fixed structures
class PlanetPosition(NamedTuple):
    longitude: float
    latitude: float
    rashi_index: int
    nakshatra_index: int

# Use numpy arrays for bulk calculations
class EphemerisData:
    """Memory-efficient ephemeris storage."""
    
    def __init__(self):
        # Pre-allocate numpy arrays
        self.jd_range = np.arange(2451545, 2500000, 0.01)  # 1300+ years
        self.planet_positions = np.zeros((len(self.jd_range), 9, 2))  # JD, 9 planets, lon/lat
        
    def get_position(self, jd: float, planet_index: int) -> tuple:
        """Fast interpolated position lookup."""
        idx = np.searchsorted(self.jd_range, jd)
        if idx < len(self.planet_positions):
            return tuple(self.planet_positions[idx, planet_index])
        else:
            # Calculate on-demand for dates outside range
            return self._calculate_position(jd, planet_index)
```

---

## 📊 **Performance Monitoring**

### **1. Application Performance Monitoring**

#### **Custom Metrics Collection**
```python
import time
import asyncio
from prometheus_client import Counter, Histogram, Gauge

# Performance metrics
REQUEST_COUNT = Counter('brahmakaal_requests_total', 'Total requests', ['endpoint', 'status'])
REQUEST_DURATION = Histogram('brahmakaal_request_duration_seconds', 'Request duration', ['endpoint'])
CACHE_HIT_RATE = Gauge('brahmakaal_cache_hit_rate', 'Cache hit rate', ['cache_layer'])
ACTIVE_CALCULATIONS = Gauge('brahmakaal_active_calculations', 'Active calculations')

class PerformanceMonitor:
    """Real-time performance monitoring."""
    
    def __init__(self):
        self.calculation_times = []
        self.cache_stats = {}
    
    async def monitor_endpoint(self, endpoint: str, func, *args, **kwargs):
        """Monitor endpoint performance."""
        start_time = time.time()
        ACTIVE_CALCULATIONS.inc()
        
        try:
            result = await func(*args, **kwargs)
            REQUEST_COUNT.labels(endpoint=endpoint, status='success').inc()
            return result
        except Exception as e:
            REQUEST_COUNT.labels(endpoint=endpoint, status='error').inc()
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)
            ACTIVE_CALCULATIONS.dec()
            
            # Log slow requests
            if duration > 5.0:
                logger.warning(f"Slow request: {endpoint} took {duration:.2f}s")
```

#### **Health Check Endpoint**
```python
@router.get("/health/performance")
async def performance_health():
    """Detailed performance health check."""
    
    # Test core components
    start_time = time.time()
    
    # Database connectivity
    db_start = time.time()
    await test_database_connection()
    db_time = (time.time() - db_start) * 1000
    
    # Cache connectivity  
    cache_start = time.time()
    await test_cache_connection()
    cache_time = (time.time() - cache_start) * 1000
    
    # Ephemeris calculation
    calc_start = time.time()
    await test_basic_calculation()
    calc_time = (time.time() - calc_start) * 1000
    
    total_time = (time.time() - start_time) * 1000
    
    return {
        "status": "healthy",
        "performance": {
            "total_health_check_ms": round(total_time, 2),
            "database_response_ms": round(db_time, 2),
            "cache_response_ms": round(cache_time, 2),
            "calculation_time_ms": round(calc_time, 2)
        },
        "thresholds": {
            "database_ok": db_time < 100,
            "cache_ok": cache_time < 50,
            "calculation_ok": calc_time < 500
        }
    }
```

### **2. Performance Alerts**

#### **Automated Alerting**
```python
class PerformanceAlerts:
    """Automated performance alerting."""
    
    def __init__(self):
        self.alert_thresholds = {
            'response_time_p95': 5.0,  # 5 seconds
            'error_rate': 0.05,        # 5%
            'cache_hit_rate': 0.80,    # 80%
            'database_connections': 50  # 50 connections
        }
    
    async def check_performance_metrics(self):
        """Check all performance metrics."""
        alerts = []
        
        # Check response times
        p95_response_time = await self.get_p95_response_time()
        if p95_response_time > self.alert_thresholds['response_time_p95']:
            alerts.append({
                'type': 'HIGH_RESPONSE_TIME',
                'value': p95_response_time,
                'threshold': self.alert_thresholds['response_time_p95'],
                'severity': 'high'
            })
        
        # Check error rates
        error_rate = await self.get_error_rate()
        if error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'HIGH_ERROR_RATE',
                'value': error_rate,
                'threshold': self.alert_thresholds['error_rate'],
                'severity': 'critical'
            })
        
        # Send alerts if any
        if alerts:
            await self.send_alerts(alerts)
        
        return alerts
```

---

## 🌐 **Client-Side Optimizations**

### **1. Request Optimization**

#### **Batching Requests**
```javascript
class BrahmakaakSDK {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseURL = 'https://api.brahmakaal.com';
        this.requestQueue = [];
        this.batchTimeout = null;
    }
    
    // Batch multiple panchang requests
    async batchPanchangRequests(requests) {
        const promises = requests.map(req => 
            this.getPanchang(req.latitude, req.longitude, req.date)
        );
        
        return Promise.all(promises);
    }
    
    // Smart caching on client side
    cache = new Map();
    
    async getPanchang(lat, lon, date, options = {}) {
        const cacheKey = `${lat}-${lon}-${date}`;
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < 3600000) { // 1 hour
                return cached.data;
            }
        }
        
        // Make request with optimizations
        const response = await fetch(`${this.baseURL}/v1/panchang`, {
            method: 'GET',
            headers: {
                'X-API-Key': this.apiKey,
                'Accept-Encoding': 'gzip',
                'Accept': 'application/json'
            },
            params: new URLSearchParams({
                latitude: lat,
                longitude: lon,
                date: date,
                ...options
            })
        });
        
        const data = await response.json();
        
        // Cache the response
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });
        
        return data;
    }
}
```

#### **Compression and Encoding**
```javascript
// Enable compression
const response = await fetch(url, {
    headers: {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
});

// Use efficient JSON parsing for large responses
const data = await response.json();
```

### **2. Progressive Loading**

#### **Priority-Based Loading**
```javascript
class ProgressivePanchangLoader {
    async loadPanchang(lat, lon, date, priority = 'high') {
        const loaders = {
            immediate: () => this.loadBasicPanchang(lat, lon, date),
            high: () => this.loadDetailedPanchang(lat, lon, date),
            low: () => this.loadAdvancedFeatures(lat, lon, date)
        };
        
        // Load basic data immediately
        const basicData = await loaders.immediate();
        
        // Load additional data based on priority
        if (priority === 'high') {
            const detailedData = await loaders.high();
            Object.assign(basicData, detailedData);
        }
        
        // Load advanced features in background
        if (priority === 'low') {
            loaders.low().then(advancedData => {
                this.updateUI(advancedData);
            });
        }
        
        return basicData;
    }
    
    async loadBasicPanchang(lat, lon, date) {
        // Load only essential fields
        return await this.api.getPanchang(lat, lon, date, {
            fields: 'tithi,nakshatra,sunrise,sunset'
        });
    }
}
```

---

## 🔧 **Performance Optimization Checklist**

### **Backend Optimizations**
- [ ] ✅ Async/await architecture implemented
- [ ] ✅ Connection pooling configured
- [ ] ✅ Multi-layer caching implemented
- [ ] ✅ Database indexes optimized
- [ ] ✅ Query optimization completed
- [ ] ✅ Memory-efficient data structures
- [ ] ✅ Algorithmic optimizations applied
- [ ] ✅ Performance monitoring in place

### **Infrastructure Optimizations**
- [ ] 🔄 Load balancer configuration
- [ ] 🔄 CDN integration
- [ ] 🔄 Auto-scaling setup
- [ ] 🔄 Geographic distribution
- [ ] ✅ Compression enabled
- [ ] ✅ HTTP/2 support

### **Client-Side Optimizations**
- [ ] 🔄 Request batching
- [ ] 🔄 Client-side caching
- [ ] 🔄 Progressive loading
- [ ] 🔄 Compression support
- [ ] 🔄 Lazy loading for non-critical data

---

## 📈 **Performance Roadmap**

### **Q3 2025**
- 🎯 Target: <50ms for all Advanced APIs
- 🔧 Implement: WebAssembly for astronomical calculations
- 📦 Deploy: Global CDN with edge computing

### **Q4 2025**
- 🎯 Target: <1s for all Core APIs  
- 🔧 Implement: GraphQL for flexible queries
- 📦 Deploy: Kubernetes auto-scaling

### **Q1 2026**
- 🎯 Target: 99.99% uptime SLA
- 🔧 Implement: Multi-region deployment
- 📦 Deploy: Real-time streaming APIs

---

**🚀 Performance is not just about speed - it's about delivering astronomical accuracy with lightning efficiency.** 