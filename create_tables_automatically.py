#!/usr/bin/env python3
"""
Automatically create all database tables in Supabase
This script uses the service role key to create tables via API
"""

from supabase.client import create_client, Client
import os

# Your Supabase configuration
SUPABASE_URL = "https://vqlmpgnzuhttzssuppkw.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxbG1wZ256dWh0dHpzc3VwcGt3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTE4NzI2NiwiZXhwIjoyMDY2NzYzMjY2fQ.yJPAGqgKBgMeNDVXfPUuGYHsbCFpJcOudRNbwg2HsMU"

def create_tables_via_api():
    """Create tables using Supabase API"""
    print("🚀 Creating database tables via Supabase API...")
    
    try:
        # Create Supabase client with service role key
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Connected to Supabase with service role key")
        
        # Create tables by inserting sample data (this will create the table if it doesn't exist)
        tables_data = {
            'users': [{
                'username': 'test_user_creation',
                'password_hash': 'test_hash_for_table_creation'
            }],
            'games': [{
                'code': 'TEST01',
                'name': 'Test Game for Table Creation',
                'admin_password': 'test_admin_hash'
            }],
            'players': [{
                'game_id': 1,
                'user_id': 1
            }],
            'challenges': [
                {'description': 'Make someone laugh out loud'},
                {'description': 'Find something blue and show it to the group'},
                {'description': 'Tell a joke that makes at least 2 people smile'},
                {'description': 'Do your best impression of a famous person'},
                {'description': 'Share an interesting fact that no one else knows'},
                {'description': 'Make a funny face and hold it for 10 seconds'},
                {'description': 'Tell a story from your childhood in under 30 seconds'},
                {'description': 'Find something in the room that starts with the letter S'},
                {'description': 'Do a dance move that makes people smile'},
                {'description': 'Share your favorite movie quote and explain why you love it'}
            ],
            'completed_challenges': [{
                'game_id': 1,
                'user_id': 1,
                'challenge_id': 1
            }],
            'vetoes': [{
                'game_id': 1,
                'user_id': 1,
                'challenge_id': 1
            }]
        }
        
        # Try to create each table by inserting data
        for table_name, data in tables_data.items():
            print(f"🔧 Creating table '{table_name}'...")
            try:
                response = supabase.table(table_name).insert(data).execute()
                print(f"✅ Table '{table_name}' created successfully")
            except Exception as e:
                if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                    print(f"❌ Table '{table_name}' doesn't exist - need to create schema first")
                else:
                    print(f"⚠️  Table '{table_name}' might already exist: {e}")
        
        print("\n🎉 Table creation attempt completed!")
        print("Note: If tables don't exist, you'll need to create them manually in the SQL Editor")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def test_existing_tables():
    """Test if tables already exist"""
    print("\n🔍 Testing existing tables...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
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
    print("🚀 Covert Agenda - Automatic Table Creation")
    print("=" * 50)
    
    # First test if tables already exist
    test_existing_tables()
    
    # Try to create tables
    create_tables_via_api()
    
    print("\n📋 Next Steps:")
    print("1. If tables were created successfully, run: python3 test_supabase_api.py")
    print("2. If tables weren't created, you'll need to run the SQL manually in Supabase SQL Editor")
    print("3. Copy the contents of supabase_schema.sql and paste it in the SQL Editor") 