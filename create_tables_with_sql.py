#!/usr/bin/env python3
"""
Create database tables using Supabase REST API with SQL execution
"""

import os
import requests
import json

# Your Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url-here')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'your-service-key-here')

def execute_sql_via_rest(sql):
    """Execute SQL via Supabase REST API"""
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Use the rpc endpoint to execute SQL
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    data = {
        'sql': sql
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_tables_with_sql():
    """Create all tables using SQL commands"""
    print("🚀 Creating database tables with SQL via REST API...")
    
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
        
        # Players table
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
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"🔧 Creating table {i}...")
        success = execute_sql_via_rest(sql)
        if success:
            print(f"✅ Table {i} created successfully")
        else:
            print(f"❌ Failed to create table {i}")
    
    # Insert sample challenges
    print("\n📝 Inserting sample challenges...")
    challenges_sql = """
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
    """
    
    success = execute_sql_via_rest(challenges_sql)
    if success:
        print("✅ Sample challenges inserted successfully")
    else:
        print("❌ Failed to insert sample challenges")

if __name__ == "__main__":
    print("🚀 Covert Agenda - SQL Table Creation via REST API")
    print("=" * 55)
    
    create_tables_with_sql()
    
    print("\n📋 Next Steps:")
    print("1. Run: python3 test_supabase_api.py to test the connection")
    print("2. If this didn't work, you'll need to create tables manually in Supabase SQL Editor") 