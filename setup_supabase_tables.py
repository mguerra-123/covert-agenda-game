#!/usr/bin/env python3
"""
Setup Supabase database tables for Covert Agenda game
"""

from supabase.client import create_client, Client
import os

# Your Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url-here')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'your-service-key-here')

def setup_database():
    """Create all necessary tables for the Covert Agenda game"""
    print("🚀 Setting up Supabase database tables...")
    
    try:
        # Create Supabase client with service role key for admin operations
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Supabase client created successfully")
        
        # SQL commands to create tables
        sql_commands = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Games table
            """
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
            """,
            
            # Players table (many-to-many relationship)
            """
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(game_id, user_id)
            );
            """,
            
            # Challenges table
            """
            CREATE TABLE IF NOT EXISTS challenges (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Completed challenges table
            """
            CREATE TABLE IF NOT EXISTS completed_challenges (
                id SERIAL PRIMARY KEY,
                game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                challenge_id INTEGER REFERENCES challenges(id),
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(game_id, user_id, challenge_id)
            );
            """,
            
            # Vetoes table
            """
            CREATE TABLE IF NOT EXISTS vetoes (
                id SERIAL PRIMARY KEY,
                game_id INTEGER REFERENCES games(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                challenge_id INTEGER REFERENCES challenges(id),
                vetoed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(game_id, user_id, challenge_id)
            );
            """
        ]
        
        # Execute each SQL command
        for i, sql in enumerate(sql_commands, 1):
            print(f"🔧 Creating table {i}...")
            try:
                # Use rpc to execute SQL
                response = supabase.rpc('exec_sql', {'sql': sql}).execute()
                print(f"✅ Table {i} created successfully")
            except Exception as e:
                print(f"⚠️  Table {i} might already exist or error: {e}")
        
        # Insert sample challenges
        print("\n📝 Inserting sample challenges...")
        sample_challenges = [
            "Make someone laugh out loud",
            "Find something blue and show it to the group",
            "Tell a joke that makes at least 2 people smile",
            "Do your best impression of a famous person",
            "Share an interesting fact that no one else knows",
            "Make a funny face and hold it for 10 seconds",
            "Tell a story from your childhood in under 30 seconds",
            "Find something in the room that starts with the letter 'S'",
            "Do a dance move that makes people smile",
            "Share your favorite movie quote and explain why you love it"
        ]
        
        for challenge in sample_challenges:
            try:
                supabase.table('challenges').insert({
                    'description': challenge
                }).execute()
                print(f"✅ Added challenge: {challenge[:30]}...")
            except Exception as e:
                print(f"⚠️  Challenge might already exist: {e}")
        
        print("\n🎉 Database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_tables():
    """Test that all tables were created successfully"""
    print("\n🔍 Testing table creation...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        # Test each table
        tables = ['users', 'games', 'players', 'challenges', 'completed_challenges', 'vetoes']
        
        for table in tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                print(f"❌ Table '{table}' error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table testing failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Covert Agenda - Supabase Database Setup")
    print("=" * 50)
    
    # Setup database
    if setup_database():
        # Test tables
        test_tables()
    else:
        print("❌ Database setup failed!") 