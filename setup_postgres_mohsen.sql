-- PostgreSQL Setup for LifePatterns AI
------------------------------------------

-- Connect to database
\c lifepatterns_db;


-- Tables (using SERIAL instead of UUID)
------------------------------------------

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    settings JSON DEFAULT '{}'
);

-- Daily entries table
CREATE TABLE IF NOT EXISTS daily_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    entry_date DATE NOT NULL,
    journal_text TEXT,
    mood_rating INTEGER CHECK (mood_rating >= 1 AND mood_rating <= 10),
    energy_level INTEGER CHECK (energy_level >= 1 AND energy_level <= 10),
    sleep_hours DECIMAL(3,1),
    activities TEXT[],
    sentiment_score DECIMAL(3,2),
    sentiment_label VARCHAR(20),
    keywords TEXT[],
    emotions JSON DEFAULT '{}',
    topics TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, entry_date)
);

-- Patterns detected table
CREATE TABLE IF NOT EXISTS detected_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_name VARCHAR(100),
    description TEXT,
    confidence_score DECIMAL(3,2),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP,
    pattern_data JSON DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE
);

-- Recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pattern_id INTEGER REFERENCES detected_patterns(id),
    recommendation_text TEXT NOT NULL,
    category VARCHAR(50),
    expected_impact JSON DEFAULT '{}',
    confidence_score DECIMAL(3,2),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    accepted BOOLEAN,
    accepted_at TIMESTAMP,
    dismissed BOOLEAN DEFAULT FALSE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_entries_user_date ON daily_entries(user_id, entry_date);
CREATE INDEX IF NOT EXISTS idx_entries_date ON daily_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_patterns_user ON detected_patterns(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_recommendations_user ON recommendations(user_id, dismissed);

-- Manual updated_at function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_entries_updated_at ON daily_entries;
CREATE TRIGGER update_entries_updated_at BEFORE UPDATE ON daily_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- Sample data for testing
----------------------------------

-- Insert test user
INSERT INTO users (username, email) 
VALUES ('testuser', 'test@example.com')
ON CONFLICT (username) DO NOTHING;

-- Insert sample entry
INSERT INTO daily_entries (user_id, entry_date, journal_text, mood_rating, energy_level, sleep_hours, activities)
VALUES (
    1,
    CURRENT_DATE,
    'Today was a productive day. I exercised in the morning and felt great.',
    8,
    7,
    7.5,
    ARRAY['exercise', 'work', 'reading']
)
ON CONFLICT (user_id, entry_date) DO NOTHING;