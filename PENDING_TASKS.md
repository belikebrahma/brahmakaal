# Brahmakaal Pending Task Sheet

**Last reviewed:** 2026-06-11  
**Scope:** Current local checkout at `/Users/popli/Documents/Code/Brahma/brahma/brahmakaal`  

---

## ✅ Completed (All Done)

| ID | Task | Evidence |
|---|---|---|
| T-001 | Dependency fix (FastAPI/Starlette/AnyIO) | `.venv` works, 88 tests pass |
| T-002 | Ephemeris file (`de421.bsp`) | Downloaded from JPL NAIF |
| T-004 | Full API startup with DB | Docker PostgreSQL, health=healthy |
| **T-007** | **Festival Calendar Engine (Phases 4-6)** | **154 rules, 86% DP coverage (131/152), 88 tests, evening-start flag, validation framework** |
| T-013 | CLI naming alignment | Added `brahmakaal` alias, `kaal` already works |
| **T-014** | **ASGI test client (no live server needed)** | conftest.py uses `ASGITransport`, test_basic_setup.py checks static routes |
| **T-015** | **Repo hygiene** | `.gitignore` updated (DS_Store, .bsp, .venv, oldtests, secrets), setup.py fixed |
| **T-006** | **Documentation accuracy** | `API_REFERENCE.md` fixed (personalized endpoints: some implemented, some planned), `INDEX.md` version updated, `FEATURE_STATUS.md` festival status corrected from 60%→86% |
| T-016 | Festival validation dataset | 3-year DP reference data (424 entries), 152 unique festivals |
| T-017 | Localization | Engine works (12 languages), translation files need population (skeleton) |

---

## ⏳ Remaining Work (4 actionable items)

| ID | Priority | Task | Why | Effort |
|---|---|---|---|---|
| T-003 | **P0** | **Remove hardcoded secrets from source** and rotate | SMTP password, JWT secret, DB URL, webhook secret exposed in `config.py` (defaults), `render.yaml`, `railway.json`, `.choreo.yaml` — all in git history | ~5min |
| T-005 | P1 | Fix no-DB mode | `app_no_db.py` still imports routes that call `get_db()` — needs dependency overrides to work without DB | ~15min |
| T-011 | P2 | Redis cache enablement | `redis_enabled=False` by default, falls back to memory. Need to set `REDIS_ENABLED=true` in env or configure Redis URL | ~5min |
| T-012 | P2 | Email/webhook testing | Code exists but untested. Need sandbox SMTP + webhook delivery tests | ~30min |

### 📋 Future / Not Yet Started (requires product decision)

| ID | Priority | Task | Blocked by |
|---|---|---|---|
| T-008 | P1 | Stripes billing / subscription | Product decision |
| T-009 | P1 | CI pipeline (GitHub Actions) | T-003, T-014 baseline |
| T-010 | P1 | Alembic migrations | Product decision |
| T-018 | P3 | Performance benchmarks | Need baseline test suite |

---

## Summary

```
✅ 88/88 tests pass  (83 fast + 5 basic setup)
✅ 154 festival rules (86% DP coverage)
✅ ASGI test client (no server needed)
✅ .gitignore cleaned, CLI aliases added
✅ Docs corrected (API_REFERENCE, INDEX, FEATURE_STATUS)
⚠️ 4 items remaining: secrets (P0), no-DB mode (P1), Redis (P2), email tests (P2)
```
