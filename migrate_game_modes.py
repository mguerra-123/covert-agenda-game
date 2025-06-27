#!/usr/bin/env python3
"""
Migration script to add game mode columns to existing database
"""

import sqlite3
import os

def migrate_database():
    """Add new columns to the game table for game modes"""
    
    # Check if database exists
    if not os.path.exists('instance/game.db'):
        print("Database not found at instance/game.db")
        return
    
    # Connect to database
    conn = sqlite3.connect('instance/game.db')
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(game)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print("Current columns in game table:", columns)
        
        # Add new columns if they don't exist
        if 'game_mode' not in columns:
            print("Adding game_mode column...")
            cursor.execute("ALTER TABLE game ADD COLUMN game_mode TEXT DEFAULT 'open_ended'")
        
        if 'game_duration' not in columns:
            print("Adding game_duration column...")
            cursor.execute("ALTER TABLE game ADD COLUMN game_duration INTEGER")
        
        if 'challenges_to_win' not in columns:
            print("Adding challenges_to_win column...")
            cursor.execute("ALTER TABLE game ADD COLUMN challenges_to_win INTEGER")
        
        # Commit changes
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(game)")
        new_columns = [column[1] for column in cursor.fetchall()]
        print("Updated columns in game table:", new_columns)
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database() 