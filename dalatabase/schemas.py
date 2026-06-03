# schemas.py - Pydantic models for request/response validation
from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional, List, Dict
from uuid import UUID


# User schemas
class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Profile schemas
class ProfileCreate(BaseModel):
    profile_name: str
    birth_date: date
    birth_time: time
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "UTC"


class ProfileResponse(ProfileCreate):
    profile_id: int
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Chart request
class ChartRequest(BaseModel):
    profile_id: int
    house_system: str = "Placidus"


# Planet position response
class PlanetPosition(BaseModel):
    name: str
    sign: str
    degrees: float
    minutes: float
    is_retrograde: bool = False


class ChartResponse(BaseModel):
    chart_id: int
    profile_id: int
    planets: List[PlanetPosition]
    houses: Dict[int, str]  # house number -> sign
    aspects: List[Dict]
    calculation_date: datetime


# Numerology
class NumerologyResponse(BaseModel):
    life_path: int
    expression: int
    soul_urge: int
    reading: str
