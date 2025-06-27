#!/usr/bin/env python3
"""
Migration script to add max_vetos column to Game table and fix failed missions.
Run this script to update your database schema.
"""

import sqlite3
import os

def migrate_database():
    db_path = 'instance/game.db'
    
    # Ensure the instance directory exists
    os.makedirs('instance', exist_ok=True)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Check if max_vetos column exists in game table
    cursor.execute("PRAGMA table_info(game)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'max_vetos' not in columns:
        print("Adding max_vetos column to game table...")
        cursor.execute("ALTER TABLE game ADD COLUMN max_vetos INTEGER DEFAULT 3")
        print("✓ Added max_vetos column to game table")
    else:
        print("✓ max_vetos column already exists in game table")
    
    # Check if is_failed column exists in player_challenge table
    cursor.execute("PRAGMA table_info(player_challenge)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_failed' not in columns:
        print("Adding is_failed column to player_challenge table...")
        cursor.execute("ALTER TABLE player_challenge ADD COLUMN is_failed BOOLEAN DEFAULT 0")
        print("✓ Added is_failed column to player_challenge table")
    else:
        print("✓ is_failed column already exists in player_challenge table")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\nMigration completed successfully!")
    print("Your database is now up to date.")

if __name__ == "__main__":
    migrate_database() 