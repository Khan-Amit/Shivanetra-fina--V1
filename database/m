# database/models.py - SQLAlchemy ORM models
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Time, JSON, ForeignKey, Text, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(150))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    profiles = relationship("UserProfile", back_populates="user", cascade="all, delete-orphan")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    profile_id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    profile_name = Column(String(100), nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_time = Column(Time, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="profiles")
    charts = relationship("NatalChart", back_populates="profile", cascade="all, delete-orphan")
    numerologies = relationship("NumerologyReading", back_populates="profile", cascade="all, delete-orphan")

class CelestialCache(Base):
    __tablename__ = "celestial_cache"
    
    id = Column(Integer, primary_key=True)
    body_id = Column(Integer, nullable=False)
    julian_day = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    latitude = Column(Float)
    distance = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NatalChart(Base):
    __tablename__ = "natal_charts"
    
    chart_id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    house_system = Column(String(20), default="Placidus")
    raw_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profile = relationship("UserProfile", back_populates="charts")

class NumerologyReading(Base):
    __tablename__ = "numerology_readings"
    
    reading_id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.profile_id"), nullable=False)
    life_path = Column(Integer)
    expression_num = Column(Integer)
    soul_urge_num = Column(Integer)
    reading_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    profile = relationship("UserProfile", back_populates="numerologies")

class ZodiacTrait(Base):
    __tablename__ = "zodiac_traits"
    
    sign_id = Column(Integer, primary_key=True)
    sign_name = Column(String(20), unique=True, nullable=False)
    element = Column(String(10))
    modality = Column(String(15))
    ruling_planet = Column(String(20))
    traits_good = Column(ARRAY(String))
    traits_bad = Column(ARRAY(String))
    daily_template = Column(Text)
