#!/usr/bin/env python3
"""
Test script to verify Supabase database connection
Run this after setting up your Supabase project
"""

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Test configuration
app = Flask(__name__)

# Your actual Supabase URL (Direct Connection)
SUPABASE_URL = "postgresql://postgres:KrFP!fP8f.!yVu&@db.vqlmpgnzuhttzssuppkw.supabase.co:5432/postgres"

app.config['SQLALCHEMY_DATABASE_URI'] = SUPABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Test models (simplified versions)
class TestUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TestGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def test_connection():
    """Test the database connection and create tables"""
    try:
        print("🔌 Testing Supabase connection...")
        
        with app.app_context():
            # Create tables
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Test inserting data
            test_user = TestUser(username="test_user")
            test_game = TestGame(name="test_game")
            
            db.session.add(test_user)
            db.session.add(test_game)
            db.session.commit()
            print("✅ Data inserted successfully!")
            
            # Test querying data
            users = TestUser.query.all()
            games = TestGame.query.all()
            print(f"✅ Query successful! Found {len(users)} users and {len(games)} games")
            
            # Clean up test data
            db.session.delete(test_user)
            db.session.delete(test_game)
            db.session.commit()
            print("✅ Test data cleaned up!")
            
        print("🎉 Database connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test FAILED: {e}")
        return False

if __name__ == "__main__":
    test_connection() 