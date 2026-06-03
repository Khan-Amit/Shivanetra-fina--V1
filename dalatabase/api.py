# api.py - FastAPI endpoints
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import crud, schemas, models, ephemeris_core
from .database import SessionLocal, engine
from datetime import datetime, date
import pytz
import json
import math

app = FastAPI(title="Shivanetra Astrology API", version="1.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Shivanetra API is running", "status": "active"}

@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/profiles/", response_model=schemas.ProfileResponse)
def create_profile(profile: schemas.ProfileCreate, user_id: str, db: Session = Depends(get_db)):
    return crud.create_profile(db, profile, user_id)

@app.post("/calculate-chart/", response_model=schemas.ChartResponse)
def calculate_chart(request: schemas.ChartRequest, db: Session = Depends(get_db)):
    # Get profile
    profile = crud.get_profile(db, request.profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Combine birth date and time into datetime
    dt = datetime.combine(profile.birth_date, profile.birth_time)
    
    # Convert to UTC if timezone is provided
    if profile.timezone and profile.timezone != "UTC":
        tz = pytz.timezone(profile.timezone)
        dt = tz.localize(dt).astimezone(pytz.UTC)
    
    # Calculate all planet longitudes
    planet_longitudes = ephemeris_core.get_all_planets_longitudes(db, dt)
    
    # Convert to zodiac signs and degrees/minutes
    planets_list = []
    for name, lon in planet_longitudes.items():
        sign = ephemeris_core.get_zodiac_sign(lon)
        degrees = lon % 30
        minutes = (degrees - int(degrees)) * 60
        planets_list.append({
            "name": name.capitalize(),
            "sign": sign,
            "degrees": round(degrees, 2),
            "minutes": round(minutes, 2),
            "is_retrograde": False  # would need additional API for retrograde
        })
    
    # Simple house calculation (mock: equal house system)
    # In production, use swe.houses()
    houses = {}
    ascendant = planet_longitudes.get("ascendant", planet_longitudes["sun"])
    for i in range(1, 13):
        house_deg = (ascendant + (i-1)*30) % 360
        houses[i] = ephemeris_core.get_zodiac_sign(house_deg)
    
    # Simple aspects (conjunction, opposition, trine, square, sextile)
    aspects = []
    planets_names = list(planet_longitudes.keys())
    for i, p1 in enumerate(planets_names):
        for p2 in planets_names[i+1:]:
            diff = abs(planet_longitudes[p1] - planet_longitudes[p2]) % 360
            diff = min(diff, 360 - diff)
            aspect_name = None
            orb = 6  # degrees orb
            if diff < orb:
                aspect_name = "conjunction"
            elif abs(diff - 180) < orb:
                aspect_name = "opposition"
            elif abs(diff - 120) < orb:
                aspect_name = "trine"
            elif abs(diff - 90) < orb:
                aspect_name = "square"
            elif abs(diff - 60) < orb:
                aspect_name = "sextile"
            if aspect_name:
                aspects.append({
                    "planet1": p1.capitalize(),
                    "planet2": p2.capitalize(),
                    "aspect": aspect_name,
                    "orb": round(diff, 2)
                })
    
    chart_data = {
        "planets": planets_list,
        "houses": houses,
        "aspects": aspects,
        "calculation_date": datetime.utcnow().isoformat()
    }
    
    # Save to database
    db_chart = crud.save_natal_chart(db, request.profile_id, chart_data, request.house_system)
    
    return schemas.ChartResponse(
        chart_id=db_chart.chart_id,
        profile_id=request.profile_id,
        planets=planets_list,
        houses=houses,
        aspects=aspects,
        calculation_date=db_chart.created_at
    )

@app.get("/profile-traits/{profile_id}")
def get_profile_traits(profile_id: int, db: Session = Depends(get_db)):
    """Get sun sign and traits for a profile."""
    profile = crud.get_profile(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Get latest chart
    chart = crud.get_latest_chart(db, profile_id)
    if not chart:
        raise HTTPException(status_code=404, detail="No chart calculated yet")
    
    chart_json = json.loads(chart.raw_data)
    sun_planet = next((p for p in chart_json["planets"] if p["name"] == "Sun"), None)
    if not sun_planet:
        raise HTTPException(status_code=500, detail="Sun not found in chart")
    
    sign_name = sun_planet["sign"]
    
    # Fetch traits from zodiac_traits table
    traits = db.query(models.ZodiacTrait).filter(models.ZodiacTrait.sign_name == sign_name).first()
    if not traits:
        traits = {"good": [], "bad": []}
    
    return {
        "profile_id": profile_id,
        "profile_name": profile.profile_name,
        "sun_sign": sign_name,
        "good_traits": traits.traits_good if traits else [],
        "bad_traits": traits.traits_bad if traits else [],
        "element": traits.element if traits else None,
        "ruling_planet": traits.ruling_planet if traits else None,
        "chart_id": chart.chart_id
    }
