#!/usr/bin/env python3
"""
Test script to verify Supabase API connection
Using the REST API instead of direct database connection
"""

import os
from supabase import create_client, Client

# Use environment variables for security
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url-here')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'your-supabase-anon-key-here')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def test_supabase_connection():
    """Test the Supabase API connection"""
    print("🔍 Testing Supabase API connection...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        print("✅ Supabase client created successfully")
        
        # Test a simple query
        print("🔍 Testing database query...")
        response = supabase.table('users').select('*').limit(1).execute()
        print("✅ Database query successful!")
        print(f"   Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_table_creation():
    """Test creating tables via API"""
    print("\n🔍 Testing table creation...")
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Test inserting a user
        user_data = {
            "username": "test_user_api",
            "password_hash": "test_hash",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        response = supabase.table('users').insert(user_data).execute()
        print("✅ User insertion successful!")
        print(f"   Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Supabase API Connection Test")
    print("=" * 40)
    
    # Test basic connection
    if test_supabase_connection():
        print("\n✅ Supabase API connection is working!")
        
        # Test table operations
        test_table_creation()
    else:
        print("\n❌ Supabase API connection failed!")
        print("Please check your API keys and project URL.") 