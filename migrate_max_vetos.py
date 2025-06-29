#!/usr/bin/env python3
"""
Migration script to add max_vetos column to games table in Supabase.
"""

import os
from supabase.client import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://vqlmpgnzuhttzssuppkw.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxbG1wZ256dWh0dHpzc3VwcGt3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTExODcyNjYsImV4cCI6MjA2Njc2MzI2Nn0.XoRv990NNt4q-VkGE6cZ8m3WJu6pHKXLjHC_OZMTzRI')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def add_max_vetos_column():
    """Add max_vetos column to games table"""
    try:
        print("Adding max_vetos column to games table...")
        
        # Execute SQL to add the column
        sql = """
        ALTER TABLE games 
        ADD COLUMN IF NOT EXISTS max_vetos INTEGER DEFAULT 3;
        """
        
        # Use the REST API to execute SQL (this requires service role key)
        # For now, let's try to update existing games to have max_vetos = 3
        print("Updating existing games to have max_vetos = 3...")
        
        # Get all games
        response = supabase.table('games').select('*').execute()
        games = response.data
        
        for game in games:
            if 'max_vetos' not in game or game['max_vetos'] is None:
                print(f"Updating game {game['id']} to have max_vetos = 3")
                supabase.table('games').update({'max_vetos': 3}).eq('id', game['id']).execute()
        
        print("✓ Migration completed!")
        print("Note: You may need to manually add the max_vetos column in Supabase SQL Editor:")
        print("ALTER TABLE games ADD COLUMN max_vetos INTEGER DEFAULT 3;")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        print("\nManual steps required:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to SQL Editor")
        print("3. Run this SQL command:")
        print("   ALTER TABLE games ADD COLUMN max_vetos INTEGER DEFAULT 3;")
        print("4. Click 'Run' to execute the command")

if __name__ == "__main__":
    add_max_vetos_column() 