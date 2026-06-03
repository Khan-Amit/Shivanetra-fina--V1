# init_db.py - Initialize database tables and load zodiac traits
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base, engine
from . import models
import os

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")
    
    # Check if zodiac_traits already has data
    Session = sessionmaker(bind=engine)
    db = Session()
    
    if db.query(models.ZodiacTrait).count() == 0:
        print("Loading zodiac traits data...")
        traits_data = [
            ("Aries", "Fire", "Cardinal", "Mars", ["Courageous", "Determined", "Confident"], ["Impatient", "Moody", "Short-tempered"]),
            ("Taurus", "Earth", "Fixed", "Venus", ["Reliable", "Patient", "Practical"], ["Stubborn", "Possessive", "Lazy"]),
            ("Gemini", "Air", "Mutable", "Mercury", ["Adaptable", "Curious", "Lively"], ["Nervous", "Inconsistent", "Gossipy"]),
            ("Cancer", "Water", "Cardinal", "Moon", ["Loyal", "Emotional", "Intuitive"], ["Moody", "Clingy", "Oversensitive"]),
            ("Leo", "Fire", "Fixed", "Sun", ["Generous", "Creative", "Warm"], ["Arrogant", "Dramatic", "Stubborn"]),
            ("Virgo", "Earth", "Mutable", "Mercury", ["Analytical", "Hardworking", "Helpful"], ["Critical", "Worrier", "Perfectionist"]),
            ("Libra", "Air", "Cardinal", "Venus", ["Diplomatic", "Charming", "Fair"], ["Indecisive", "Self-pitying", "Avoids conflict"]),
            ("Scorpio", "Water", "Fixed", "Pluto", ["Passionate", "Resourceful", "Brave"], ["Jealous", "Secretive", "Manipulative"]),
            ("Sagittarius", "Fire", "Mutable", "Jupiter", ["Optimistic", "Adventurous", "Honest"], ["Reckless", "Tactless", "Restless"]),
            ("Capricorn", "Earth", "Cardinal", "Saturn", ["Disciplined", "Responsible", "Ambitious"], ["Pessimistic", "Stingy", "Cold"]),
            ("Aquarius", "Air", "Fixed", "Uranus", ["Original", "Humanitarian", "Intelligent"], ["Detached", "Unpredictable", "Rebellious"]),
            ("Pisces", "Water", "Mutable", "Neptune", ["Compassionate", "Artistic", "Intuitive"], ["Escapist", "Overly trusting", "Lazy"])
        ]
        for t in traits_data:
            trait = models.ZodiacTrait(
                sign_name=t[0],
                element=t[1],
                modality=t[2],
                ruling_planet=t[3],
                traits_good=t[4],
                traits_bad=t[5]
            )
            db.add(trait)
        db.commit()
        print("✅ Zodiac traits loaded")
    else:
        print("Zodiac traits already exist, skipping")
    
    db.close()
    print("✅ Database initialization complete")

if __name__ == "__main__":
    init_db()
