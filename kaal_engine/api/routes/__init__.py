"""
API Routes for Brahmakaal Enterprise API
Collection of all API endpoints including authentication and analytics
PHASE 4: Now includes personalized astrology endpoints
"""

from . import health, panchang, ayanamsha, festivals, muhurta, auth, analytics
# PHASE 4: Personalized astrology routes
from . import horoscope, transits

__all__ = [
    "health",
    "panchang", 
    "ayanamsha",
    "festivals",
    "muhurta",
    "auth",
    "analytics",
    # PHASE 4: Personalized endpoints
    "horoscope",
    "transits"
] 