#!/usr/bin/env python3
"""
Test script to verify Supabase API connection
Using the REST API instead of direct database connection
"""

from supabase.client import create_client, Client
import os

# Your Supabase configuration
SUPABASE_URL = "https://vqlmpgnzuhttzssuppkw.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxbG1wZ256dWh0dHpzc3VwcGt3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExODcyNjYsImV4cCI6MjA2Njc2MzI2Nn0.XoRv990NNt4q-VkGE6cZ8m3WJu6pHKXLjHC_OZMTzRI"

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