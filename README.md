# Brahmakaal

Brahmakaal is a Python/FastAPI service for Vedic astronomy and calendar calculations. It combines a local astronomical calculation engine with REST APIs for Panchang, Muhurta, Hindu festivals, Ayanamsha comparisons, personalized astrology, authentication, usage analytics, and webhooks.

> Current repository status: feature-rich API code is present, but this local checkout is **not fully green yet**. See [Pending Task Sheet](PENDING_TASKS.md) for the verified blockers and next work.

---

## 1. What this project does

Brahmakaal provides programmatic access to traditional Indian/Vedic time calculations:

- **Panchang**: Tithi, Nakshatra, Yoga, Karana, Vara, sunrise/sunset, moonrise/moonset, Rahu Kaal, Gulika Kaal, Yamaganda, Brahma Muhurta, Abhijit Muhurta, planetary positions, traditional years, Tarabala/Chandrabala, Shool/Nivas, Panchaka, Ritu/Ayana.
- **Muhurta**: Auspicious timing search for marriage, business, travel, education, property, and general activities.
- **Festival Calendar**: Hindu festival calculations with regional/category filters and export support.
- **Ayanamsha**: Comparison across Lahiri, Raman, Krishnamurti, Yukteshwar, Surya Siddhanta, Fagan-Bradley, DeLuce, Pushya Paksha, Galactic Center, and True Citra.
- **Personalized astrology APIs**: Natal chart, daily transit analysis, personalized Panchang, and personalized Muhurta are partially implemented.
- **Enterprise API layer**: JWT auth, API keys, subscription tiers, rate limiting, analytics, usage logs, and webhook endpoint management.

---

## 2. Repository layout

```text
brahmakaal/
├── kaal_engine/
│   ├── kaal.py                    # Main astronomical/Vedic calculation engine
│   ├── cli.py                     # Command-line interface entry point
│   ├── config.py                  # Environment-driven settings
│   ├── api/
│   │   ├── app.py                 # Full FastAPI app with DB/auth/rate limits
│   │   ├── app_no_db.py           # Intended no-DB test app; currently needs fixes
│   │   ├── models.py              # Pydantic request/response models
│   │   └── routes/                # API route modules
│   ├── auth/                      # JWT, API key, middleware, rate limiter, DB models
│   ├── core/                      # Ayanamsha, muhurta, festivals, enhanced systems
│   ├── db/                        # SQLAlchemy async database setup and models
│   ├── geo/                       # Geographic/micro-adjustment helpers
│   ├── localization/              # Language/localization helpers
│   ├── services/                  # Email and webhook services
│   ├── cache/                     # Redis backend
│   └── performance/               # Performance helpers/monitoring
├── tests/                         # API, integration, performance, and accuracy tests
├── documentation/                 # Extended project and API documentation
├── oldtests/                      # Legacy tests kept for reference
├── start_api.py                   # Full API launcher
├── start_simple_api.py            # No-DB launcher, pending dependency override fixes
├── run_tests.py                   # Test runner script
├── Dockerfile                     # Container build
├── docker-compose.yml             # App + PostgreSQL local stack
├── requirements.txt               # Runtime/test dependencies
└── PENDING_TASKS.md               # Current work sheet and blockers
```

---

## 3. Runtime architecture

```text
Client / API consumer
        │
        ▼
FastAPI app (kaal_engine.api.app)
        │
        ├── Middleware: CORS, auth context, rate limiting, request logging, usage tracking
        ├── Route modules: health, auth, panchang, muhurta, festivals, ayanamsha,
        │                 horoscope, transits, analytics, webhooks
        ├── PostgreSQL: users, subscriptions, API keys, usage logs, calculation records
        ├── Redis/memory cache: optional caching layer
        └── Kaal engine: astronomical calculations using Skyfield/SPICE ephemeris
```

The calculation path depends on a JPL SPICE ephemeris file. By default the code expects `de421.bsp` through `EPHEMERIS_FILE_PATH`.

---

## 4. Main technologies

- **Language**: Python 3.11 recommended
- **API framework**: FastAPI + Uvicorn
- **Data validation**: Pydantic v2
- **Astronomy**: Skyfield, Astropy, SpiceyPy, PyEphem
- **Database**: PostgreSQL with SQLAlchemy async + asyncpg
- **Auth/security**: JWT, Passlib/BCrypt, API key hashing, middleware rate limiting
- **Cache**: Redis-ready; cache is disabled in the current full app startup path unless configured
- **Testing**: Pytest, pytest-asyncio, pytest-cov, HTTPX
- **Deployment**: Docker, docker-compose, Procfile, Railway, Render, Choreo config files

---

## 5. Setup

### 5.1 Create an isolated Python environment

Use a fresh virtual environment. The global Python environment on this machine currently has incompatible packages; do not rely on it.

```bash
cd /Users/popli/Documents/Code/Brahma/brahma/brahmakaal
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If dependency resolution installs incompatible FastAPI/Starlette/AnyIO versions, pin compatible versions before running tests, for example:

```bash
pip install "fastapi==0.104.1" "starlette>=0.27.0,<0.28.0" "anyio>=3.7.1,<4.0.0"
```

### 5.2 Add the ephemeris file

The engine needs a SPICE kernel file:

```bash
# Put the file at the configured path, for example:
cp /path/to/de421.bsp ./de421.bsp

# Or point the app to another location:
export EPHEMERIS_FILE_PATH=/absolute/path/to/de421.bsp
```

Current `.gitignore` excludes `data/`, so ephemeris files should be provided by deployment artifacts, object storage, or local setup rather than committed directly.

### 5.3 Configure environment variables

Minimum variables for a full API run:

```bash
export ENVIRONMENT=development
export HOST=0.0.0.0
export PORT=8000
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/brahmakaal
export JWT_SECRET_KEY=replace-with-a-secure-random-value
export EPHEMERIS_FILE_PATH=de421.bsp
export REDIS_ENABLED=false
```

Optional variables include `REDIS_URL`, SMTP settings, webhook settings, CORS settings, and Stripe keys.

> Security note: several deployment/config files in this checkout contain hardcoded secrets. Rotate those credentials and move secrets to environment variables or managed secret stores before any production use.

---

## 6. Running the API

### Full API with PostgreSQL

```bash
# Start PostgreSQL separately or use docker-compose.
python start_api.py
```

Docs and health endpoints:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Health: <http://localhost:8000/v1/health>
- Status: <http://localhost:8000/v1/status>

### Docker Compose

```bash
docker compose up --build
```

This starts the API and a local PostgreSQL container. Make sure `EPHEMERIS_FILE_PATH` resolves inside the container.

### No-DB mode

```bash
python start_simple_api.py
```

No-DB mode is intended for testing core calculations, but route dependency overrides still need cleanup. See [Pending Task Sheet](PENDING_TASKS.md).

---

## 7. API endpoint map

All versioned endpoints use the `/v1` prefix. The current source defines about 45 route handlers.

### System

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Service information |
| GET | `/v1/health` | Health check with DB/cache/ephemeris status |
| GET | `/v1/status` | Detailed service configuration/status |

### Authentication and users

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/auth/register` | Create user |
| POST | `/v1/auth/login` | Login and receive tokens |
| POST | `/v1/auth/refresh` | Refresh token |
| GET | `/v1/auth/me` | Current user profile |
| GET | `/v1/auth/subscription` | Current subscription |
| POST | `/v1/auth/api-keys` | Create API key |
| GET | `/v1/auth/api-keys` | List API keys |
| DELETE | `/v1/auth/api-keys/{key_id}` | Delete API key |
| POST | `/v1/auth/subscription/upgrade` | Placeholder subscription upgrade |
| GET | `/v1/auth/admin/users` | Admin user listing |
| POST | `/v1/auth/admin/users/{user_id}/deactivate` | Admin deactivate user |
| POST | `/v1/auth/admin/users/{user_id}/activate` | Admin activate user |

### Panchang and advanced calendar systems

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/panchang` | Full Panchang calculation |
| GET | `/v1/panchang` | Query-string Panchang calculation |
| POST | `/v1/panchang/personalized` | Personalized Panchang using birth data |
| GET | `/v1/panchaka-periods` | Enhanced hourly Panchaka periods |
| GET | `/v1/udaya-lagna-periods` | Rising sign periods through the day |
| GET | `/v1/complete-muhurta-periods` | 8 traditional daily Muhurta periods |
| GET | `/v1/inauspicious-periods` | Dur Muhurtam, Varjyam, Aadal Yoga, Ganda Moola |
| GET | `/v1/extended-calendar-systems` | Gujarati Samvat, Gate/Pravishte, Brihaspati cycle, multiple eras |
| GET | `/v1/languages` | Supported localization languages |

### Muhurta

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/muhurta` | Auspicious timing search |
| GET | `/v1/muhurta/types` | Available Muhurta types |
| POST | `/v1/muhurta/personalized` | Birth-chart-aware Muhurta search |

### Festivals

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/festivals` | Festival calendar by year/month/regions/categories |
| GET | `/v1/festivals` | Query-string festival calendar |
| GET | `/v1/festivals/regions` | Supported regions |
| GET | `/v1/festivals/categories` | Supported categories |

### Ayanamsha

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/ayanamsha` | Compare supported Ayanamsha systems |
| GET | `/v1/ayanamsha/systems` | Descriptions of supported systems |

### Personalized astrology

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/horoscope/natal-chart` | Birth chart with houses, dignities, yogas, insights |
| POST | `/v1/transits/daily` | Daily transit analysis against natal chart |

Planned but not implemented as routes yet: `/v1/users/preferences`, `/v1/recommendations/daily`.

### Analytics and webhooks

| Method | Path | Purpose |
|---|---|---|
| GET | `/v1/analytics/my-usage` | Authenticated user usage stats |
| GET | `/v1/analytics/subscription-info` | Subscription/rate-limit information |
| GET | `/v1/analytics/admin/dashboard` | Admin dashboard metrics |
| GET | `/v1/analytics/admin/users/{user_id}/analytics` | Admin user analytics |
| GET | `/v1/analytics/admin/endpoints/{endpoint_path}` | Admin endpoint analytics |
| POST | `/v1/webhooks/endpoints` | Register webhook endpoint |
| GET | `/v1/webhooks/endpoints` | List webhook endpoints |
| PUT | `/v1/webhooks/endpoints/{endpoint_id}` | Update webhook endpoint |
| DELETE | `/v1/webhooks/endpoints/{endpoint_id}` | Delete webhook endpoint |
| POST | `/v1/webhooks/test/{endpoint_id}` | Send webhook test |
| GET | `/v1/webhooks/events` | List webhook event types/history |

---

## 8. Request examples

### Panchang

```bash
curl -X POST http://localhost:8000/v1/panchang \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 28.6139,
    "longitude": 77.2090,
    "date": "2025-01-01",
    "time": "12:00:00",
    "timezone_offset": 5.5,
    "ayanamsha": "LAHIRI",
    "human_readable_times": true
  }'
```

### Muhurta

```bash
curl -X POST http://localhost:8000/v1/muhurta \
  -H "Content-Type: application/json" \
  -d '{
    "muhurta_type": "marriage",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "start_date": "2025-02-01T00:00:00Z",
    "end_date": "2025-02-28T23:59:59Z",
    "duration_minutes": 120,
    "min_quality": "good",
    "max_results": 10
  }'
```

### Festivals

```bash
curl "http://localhost:8000/v1/festivals?year=2025&regions=all_india&categories=major"
```

### Natal chart

```bash
curl -X POST http://localhost:8000/v1/horoscope/natal-chart \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

## 9. CLI usage

`setup.py` registers the console command as `kaal`:

```bash
pip install -e .
kaal panchang --lat 28.6139 --lon 77.2090 --date 2025-01-01 --time 12:00:00 --ephemeris de421.bsp
kaal ayanamsha --date 2025-01-01 --reference LAHIRI --ephemeris de421.bsp
kaal planets --lat 28.6139 --lon 77.2090 --date 2025-01-01 --aspects --ephemeris de421.bsp
kaal muhurta --type marriage --lat 28.6139 --lon 77.2090 --start-date 2025-02-01 --end-date 2025-02-28 --ephemeris de421.bsp
kaal festivals --year 2025 --regions all_india --categories major --ephemeris de421.bsp
```

---

## 10. Testing

Standard test commands:

```bash
pytest -q
python run_tests.py --type quick
python run_tests.py --type accuracy
python run_tests.py --type performance
python run_tests.py --coverage
```

Current verification from this checkout:

- `pytest -q` fails during import because the active global environment has incompatible FastAPI/Starlette/AnyIO versions.
- No `.bsp` ephemeris file is currently present in the repository checkout.
- Full API startup requires a reachable PostgreSQL database and working ephemeris file.

See [Pending Task Sheet](PENDING_TASKS.md) for the exact blockers and recommended order.

---

## 11. Documentation

Useful docs in this repo:

- [`documentation/INDEX.md`](documentation/INDEX.md) - documentation navigation
- [`documentation/API_REFERENCE.md`](documentation/API_REFERENCE.md) - API details
- [`documentation/ARCHITECTURE.md`](documentation/ARCHITECTURE.md) - system architecture notes
- [`documentation/FEATURE_STATUS.md`](documentation/FEATURE_STATUS.md) - feature status and roadmap
- [`documentation/FUTURE_ROADMAP.md`](documentation/FUTURE_ROADMAP.md) - future work
- [`documentation/QUICK_START.md`](documentation/QUICK_START.md) - quick start guide
- [`tests/README.md`](tests/README.md) - test suite guide
- [`PENDING_TASKS.md`](PENDING_TASKS.md) - current task sheet

Some legacy docs under `Old-Documentation/` and `oldtests/` may be historically useful but should not be treated as current truth without verification.

---

## 12. Production readiness checklist

Before production deployment:

1. Use a clean virtualenv/container with locked dependency versions.
2. Restore/provision the ephemeris file and set `EPHEMERIS_FILE_PATH`.
3. Move all secrets out of source-controlled config files and rotate exposed credentials.
4. Use managed PostgreSQL and Redis with SSL/TLS where appropriate.
5. Run migrations/table creation against the production DB intentionally.
6. Validate auth, rate limits, analytics, webhooks, and email in staging.
7. Run `pytest`, integration tests, and representative API smoke tests.
8. Confirm OpenAPI docs match implemented endpoints.
9. Configure CORS and TrustedHostMiddleware with real production domains.
10. Add monitoring, logs, backups, and alerting.

---

## 13. Current pending work

The highest priority items are:

- Fix dependency compatibility and make tests import successfully.
- Provide/restore the SPICE ephemeris file.
- Remove and rotate hardcoded secrets.
- Fix no-DB mode or document it as unsupported.
- Align documentation with actual implemented endpoints.
- Complete/verify Phase 4 personalized features.

Full details are maintained in [`PENDING_TASKS.md`](PENDING_TASKS.md).
