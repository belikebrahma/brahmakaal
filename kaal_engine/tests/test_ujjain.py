from datetime import datetime, timezone
from kaal_engine.kaal import Kaal

def test_mahashivaratri_2025():
    kaal = Kaal("data/de441.bsp")
    dt = datetime(2025, 2, 26, tzinfo=timezone.utc)
    result = kaal.get_panchang(23.1765, 75.7885, dt)
    assert 13.5 < result['tithi'] < 14.5  # Krishna Chaturdashi