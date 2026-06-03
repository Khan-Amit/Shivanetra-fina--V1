# app/engine.py
import datetime
import math
import swisseph as swe
from typing import Dict, Any, Tuple

# =====================================================================
# 1. SETUP & CONFIGURATION
# =====================================================================
# Set ephemeris path (optional – uses internal if not set)
# swe.set_ephe_path('/app/ephe')  # uncomment if you upload ephemeris files

# Force Sidereal Zodiac using Lahiri Ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

# Static Translation Data Arrays
RASI_NAMES = [
    "Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)",
    "Karka (Cancer)", "Simha (Leo)", "Kanya (Virgo)",
    "Tula (Libra)", "Vrischika (Scorpio)", "Dhanu (Sagittarius)",
    "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"
]

PLANET_MAP: Dict[str, int] = {
    "Surya (Sun)": swe.SUN,
    "Chandra (Moon)": swe.MOON,
    "Mangala (Mars)": swe.MARS,
    "Budha (Mercury)": swe.MERCURY,
    "Guru (Jupiter)": swe.JUPITER,
    "Shukra (Venus)": swe.VENUS,
    "Shani (Saturn)": swe.SATURN,
    "Rahu (North Node)": swe.MEAN_NODE
}

# =====================================================================
# 2. HELPER FUNCTIONS
# =====================================================================
def get_rasi_and_degree(absolute_longitude: float) -> Tuple[int, float]:
    """Converts 0-360 longitude to Rasi index and degree within that Rasi."""
    normalized = absolute_longitude % 360
    rasi_idx = int(normalized // 30)
    degree_in_rasi = normalized % 30
    return rasi_idx, degree_in_rasi

def calculate_house_number(planet_rasi: int, lagna_rasi: int) -> int:
    """Equal house system: house = (planet_rasi - lagna_rasi) + 1."""
    house = (planet_rasi - lagna_rasi) + 1
    if house <= 0:
        house += 12
    return house

# =====================================================================
# 3. MAIN CALCULATION ENGINE
# =====================================================================
def generate_natal_chart(
    year: int,
    month: int,
    day: int,
    hour_24: float,
    minute: int,
    lat: float,
    lon: float,
    timezone_hours: float = 5.5   # default IST, override as needed
) -> Tuple[float, Dict[str, Any]]:
    """
    Returns: (ayanamsha, chart_data)
    chart_data contains:
        "Lagna (Ascendant)": {absolute_lon, rasi_idx, rasi_name, degrees, house}
        "Surya (Sun)": {...},
        "Chandra (Moon)": {...},
        ...
        "Ketu (South Node)": {...}
    """
    # Convert local time to UTC
    local_dt = datetime.datetime(year, month, day, int(hour_24), minute)
    tz_offset = datetime.timedelta(hours=timezone_hours)
    utc_dt = local_dt - tz_offset

    # Julian Day for UTC
    utc_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, utc_decimal)

    # Ayanamsha for this date
    ayanamsha = swe.get_ayanamsa_ex(jd_ut, swe.FLG_SIDEREAL)

    # Lagna (Ascendant) and house cusps
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, ord('B'), swe.FLG_SIDEREAL)
    lagna_absolute = ascmc[0]
    lagna_rasi_idx, lagna_deg = get_rasi_and_degree(lagna_absolute)

    chart_data = {
        "Lagna (Ascendant)": {
            "absolute_lon": lagna_absolute,
            "rasi_idx": lagna_rasi_idx,
            "rasi_name": RASI_NAMES[lagna_rasi_idx],
            "degrees": lagna_deg,
            "house": 1
        }
    }

    # Planets
    for name, code in PLANET_MAP.items():
        res, _ = swe.calc_ut(jd_ut, code, swe.FLG_SIDEREAL)
        abs_lon = res[0]
        rasi_idx, deg = get_rasi_and_degree(abs_lon)
        house_num = calculate_house_number(rasi_idx, lagna_rasi_idx)

        chart_data[name] = {
            "absolute_lon": abs_lon,
            "rasi_idx": rasi_idx,
            "rasi_name": RASI_NAMES[rasi_idx],
            "degrees": deg,
            "house": house_num
        }

    # Ketu (South Node) – opposite Rahu
    rahu_lon = chart_data["Rahu (North Node)"]["absolute_lon"]
    ketu_lon = (rahu_lon + 180.0) % 360
    ketu_rasi_idx, ketu_deg = get_rasi_and_degree(ketu_lon)
    ketu_house = calculate_house_number(ketu_rasi_idx, lagna_rasi_idx)

    chart_data["Ketu (South Node)"] = {
        "absolute_lon": ketu_lon,
        "rasi_idx": ketu_rasi_idx,
        "rasi_name": RASI_NAMES[ketu_rasi_idx],
        "degrees": ketu_deg,
        "house": ketu_house
    }

    return ayanamsha, chart_data
