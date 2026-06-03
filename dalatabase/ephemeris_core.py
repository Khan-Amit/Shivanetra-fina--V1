# ephemeris_core.py - Planetary position calculation with cache
import libephemeris as swe
from libephemeris.constants import CALC_NONE
from datetime import datetime
import pytz
import os
from sqlalchemy.orm import Session
from . import models

# Configure backend from environment
BACKEND = os.getenv("EPHEMERIS_BACKEND", "horizons")
swe.set_backend(BACKEND)

# Optional: offline ephemeris file
EPHEMERIS_FILE = os.getenv("EPHEMERIS_FILE_PATH", "")
if EPHEMERIS_FILE and BACKEND == "skyfield":
    swe.set_ephemeris_path(EPHEMERIS_FILE)

# Planet constants (libephemeris)
PLANETS = {
    "sun": swe.SE_SUN,
    "moon": swe.SE_MOON,
    "mercury": swe.SE_MERCURY,
    "venus": swe.SE_VENUS,
    "mars": swe.SE_MARS,
    "jupiter": swe.SE_JUPITER,
    "saturn": swe.SE_SATURN,
    "uranus": swe.SE_URANUS,
    "neptune": swe.SE_NEPTUNE,
    "pluto": swe.SE_PLUTO,
    "north_node": swe.SE_TRUE_NODE,
}


def julian_day(dt: datetime) -> float:
    """Convert datetime to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute/60.0 + dt.second/3600.0)


def get_planet_longitude_cached(db: Session, planet_const: int, dt: datetime) -> float:
    """
    Get planet longitude from cache or calculate and store it.
    """
    jd = julian_day(dt)

    # Check cache
    cached = db.query(models.CelestialCache).filter(
        models.CelestialCache.body_id == planet_const,
        models.CelestialCache.julian_day == jd
    ).first()
    if cached:
        return cached.longitude

    # Calculate from ephemeris
    pos, _ = swe.calc_ut(jd, planet_const, CALC_NONE)
    longitude = pos[0]

    # Store in cache
    cache_entry = models.CelestialCache(
        body_id=planet_const,
        julian_day=jd,
        longitude=longitude,
        latitude=pos[1] if len(pos) > 1 else None,
        distance=pos[2] if len(pos) > 2 else None
    )
    db.add(cache_entry)
    db.commit()

    return longitude


def get_all_planets_longitudes(db: Session, dt: datetime) -> dict:
    """Return dict of all planet longitudes."""
    result = {}
    for name, const in PLANETS.items():
        result[name] = get_planet_longitude_cached(db, const, dt)
    return result


def get_zodiac_sign(degrees: float) -> str:
    """Convert ecliptic longitude to zodiac sign name."""
    signs = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    idx = int(degrees // 30) % 12
    return signs[idx]
