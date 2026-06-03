-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users table
CREATE TABLE users (
    user_id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User profiles
CREATE TABLE user_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    profile_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    birth_time TIME NOT NULL,
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Celestial cache
CREATE TABLE celestial_cache (
    id SERIAL PRIMARY KEY,
    body_id INTEGER NOT NULL,
    julian_day DECIMAL(15,6) NOT NULL,
    longitude DECIMAL(10,6) NOT NULL,
    latitude DECIMAL(10,6),
    distance DECIMAL(15,6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_celestial_body_time ON celestial_cache(body_id, julian_day);

-- 4. Natal charts
CREATE TABLE natal_charts (
    chart_id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES user_profiles(profile_id) ON DELETE CASCADE,
    calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    house_system VARCHAR(20) DEFAULT 'Placidus',
    raw_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_chart_profile ON natal_charts(profile_id);

-- 5. Numerology readings
CREATE TABLE numerology_readings (
    reading_id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES user_profiles(profile_id) ON DELETE CASCADE,
    life_path INTEGER,
    expression_num INTEGER,
    soul_urge_num INTEGER,
    reading_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Zodiac traits
CREATE TABLE zodiac_traits (
    sign_id SERIAL PRIMARY KEY,
    sign_name VARCHAR(20) UNIQUE NOT NULL,
    element VARCHAR(10),
    modality VARCHAR(15),
    ruling_planet VARCHAR(20),
    traits_good TEXT[],
    traits_bad TEXT[],
    daily_template TEXT
);

INSERT INTO zodiac_traits (sign_name, element, modality, ruling_planet, traits_good, traits_bad) VALUES
('Aries', 'Fire', 'Cardinal', 'Mars', ARRAY['Courageous','Determined','Confident'], ARRAY['Impatient','Moody','Short-tempered']),
('Taurus', 'Earth', 'Fixed', 'Venus', ARRAY['Reliable','Patient','Practical'], ARRAY['Stubborn','Possessive','Lazy']),
('Gemini', 'Air', 'Mutable', 'Mercury', ARRAY['Adaptable','Curious','Lively'], ARRAY['Nervous','Inconsistent','Gossipy']),
('Cancer', 'Water', 'Cardinal', 'Moon', ARRAY['Loyal','Emotional','Intuitive'], ARRAY['Moody','Clingy','Oversensitive']),
('Leo', 'Fire', 'Fixed', 'Sun', ARRAY['Generous','Creative','Warm'], ARRAY['Arrogant','Dramatic','Stubborn']),
('Virgo', 'Earth', 'Mutable', 'Mercury', ARRAY['Analytical','Hardworking','Helpful'], ARRAY['Critical','Worrier','Perfectionist']),
('Libra', 'Air', 'Cardinal', 'Venus', ARRAY['Diplomatic','Charming','Fair'], ARRAY['Indecisive','Self-pitying','Avoids conflict']),
('Scorpio', 'Water', 'Fixed', 'Pluto', ARRAY['Passionate','Resourceful','Brave'], ARRAY['Jealous','Secretive','Manipulative']),
('Sagittarius', 'Fire', 'Mutable', 'Jupiter', ARRAY['Optimistic','Adventurous','Honest'], ARRAY['Reckless','Tactless','Restless']),
('Capricorn', 'Earth', 'Cardinal', 'Saturn', ARRAY['Disciplined','Responsible','Ambitious'], ARRAY['Pessimistic','Stingy','Cold']),
('Aquarius', 'Air', 'Fixed', 'Uranus', ARRAY['Original','Humanitarian','Intelligent'], ARRAY['Detached','Unpredictable','Rebellious']),
('Pisces', 'Water', 'Mutable', 'Neptune', ARRAY['Compassionate','Artistic','Intuitive'], ARRAY['Escapist','Overly trusting','Lazy']);
