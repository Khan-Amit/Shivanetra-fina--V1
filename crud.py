from sqlalchemy.orm import Session
from . import models, schemas
import json
from datetime import datetime

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        password_hash=user.password_hash,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_profile(db: Session, profile: schemas.ProfileCreate, user_id: str):
    db_profile = models.UserProfile(
        user_id=user_id,
        profile_name=profile.profile_name,
        birth_date=profile.birth_date,
        birth_time=profile.birth_time,
        latitude=profile.latitude,
        longitude=profile.longitude,
        timezone=profile.timezone
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_profile(db: Session, profile_id: int):
    return db.query(models.UserProfile).filter(models.UserProfile.profile_id == profile_id).first()

def save_natal_chart(db: Session, profile_id: int, chart_data: dict, house_system: str = "Placidus"):
    db_chart = models.NatalChart(
        profile_id=profile_id,
        house_system=house_system,
        raw_data=json.dumps(chart_data)
    )
    db.add(db_chart)
    db.commit()
    db.refresh(db_chart)
    return db_chart

def get_latest_chart(db: Session, profile_id: int):
    return db.query(models.NatalChart).filter(
        models.NatalChart.profile_id == profile_id
    ).order_by(models.NatalChart.created_at.desc()).first()

def get_cached_planet(db: Session, body_id: int, julian_day: float):
    return db.query(models.CelestialCache).filter(
        models.CelestialCache.body_id == body_id,
        models.CelestialCache.julian_day == julian_day
    ).first()

def save_numerology(db: Session, profile_id: int, life_path: int, expression: int, soul_urge: int, text: str):
    db_num = models.NumerologyReading(
        profile_id=profile_id,
        life_path=life_path,
        expression_num=expression,
        soul_urge_num=soul_urge,
        reading_text=text
    )
    db.add(db_num)
    db.commit()
    return db_num
