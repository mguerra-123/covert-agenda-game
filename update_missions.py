#!/usr/bin/env python3

import os
from supabase.client import create_client, Client

def update_missions():
    """Update the database with missions from Missions.txt"""
    
    # Initialize Supabase client
    SUPABASE_URL = os.environ.get('SUPABASE_URL', 'your-supabase-url-here')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'your-anon-key-here')
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    
    # Read all challenges from Missions.txt
    with open('Missions.txt', 'r') as f:
        challenges = [line.strip() for line in f if line.strip()]
    
    print(f"Found {len(challenges)} challenges in Missions.txt")
    
    try:
        # Clear existing challenges
        print("Clearing existing challenges...")
        supabase.table('challenges').delete().neq('id', 0).execute()
        
        # Insert new challenges
        print("Inserting new challenges...")
        for i, challenge in enumerate(challenges):
            supabase.table('challenges').insert({
                'description': challenge
            }).execute()
            
            if (i + 1) % 50 == 0:
                print(f"Inserted {i + 1} challenges...")
        
        print(f"Successfully updated database with {len(challenges)} challenges!")
        
    except Exception as e:
        print(f"Error updating database: {e}")

if __name__ == "__main__":
    update_missions() 