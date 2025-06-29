-- Covert Agenda Database Schema
-- Run this in your Supabase SQL Editor

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Games table
CREATE TABLE IF NOT EXISTS games (
    id SERIAL PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    admin_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    winner_id INTEGER REFERENCES users(id),
    game_mode VARCHAR(20) DEFAULT 'open_ended',
    time_limit INTEGER,
    target_challenges INTEGER
);

-- Players table (many-to-many relationship)
CREATE TABLE IF NOT EXISTS players (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, user_id)
);

-- Challenges table
CREATE TABLE IF NOT EXISTS challenges (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Completed challenges table
CREATE TABLE IF NOT EXISTS completed_challenges (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    challenge_id INTEGER REFERENCES challenges(id),
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, user_id, challenge_id)
);

-- Vetoes table
CREATE TABLE IF NOT EXISTS vetoes (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    challenge_id INTEGER REFERENCES challenges(id),
    vetoed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, user_id, challenge_id)
);

-- Insert sample challenges
INSERT INTO challenges (description) VALUES
    ('Make someone laugh out loud'),
    ('Find something blue and show it to the group'),
    ('Tell a joke that makes at least 2 people smile'),
    ('Do your best impression of a famous person'),
    ('Share an interesting fact that no one else knows'),
    ('Make a funny face and hold it for 10 seconds'),
    ('Tell a story from your childhood in under 30 seconds'),
    ('Find something in the room that starts with the letter ''S'''),
    ('Do a dance move that makes people smile'),
    ('Share your favorite movie quote and explain why you love it')
ON CONFLICT DO NOTHING; 