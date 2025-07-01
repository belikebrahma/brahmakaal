"""
API Routes for Brahmakaal Enterprise API
Collection of all API endpoints including authentication and analytics
"""

from . import health, panchang, ayanamsha, festivals, muhurta, auth, analytics

__all__ = [
    "health",
    "panchang", 
    "ayanamsha",
    "festivals",
    "muhurta",
    "auth",
    "analytics"
] 