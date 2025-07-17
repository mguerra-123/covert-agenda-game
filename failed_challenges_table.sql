-- Create failed_challenges table for tracking failed challenges
CREATE TABLE IF NOT EXISTS failed_challenges (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(game_id, user_id, challenge_id)
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_failed_challenges_game_user ON failed_challenges(game_id, user_id);
CREATE INDEX IF NOT EXISTS idx_failed_challenges_user ON failed_challenges(user_id);
CREATE INDEX IF NOT EXISTS idx_failed_challenges_challenge ON failed_challenges(challenge_id);

-- Enable Row Level Security (RLS)
ALTER TABLE failed_challenges ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (you can restrict this later for security)
CREATE POLICY "Allow all operations on failed_challenges" ON failed_challenges
    FOR ALL USING (true); 