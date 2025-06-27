#!/usr/bin/env python3
"""
Challenge Game Startup Script
This script helps you start the Challenge Game application.
"""

import os
import sys
import subprocess
import webbrowser
import time

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 
        'flask_wtf', 'werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing dependencies. Installing...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Dependencies installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies.")
            print("Please run: pip install -r requirements.txt")
            return False
    else:
        print("✅ All dependencies are installed.")
    return True

def start_application():
    """Start the Flask application."""
    print("\n🚀 Starting Challenge Game...")
    print("=" * 50)
    
    # Check if port 5000 is available
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        
        if result == 0:
            print("⚠️  Port 5000 is already in use.")
            print("The application might already be running.")
            print("Try opening: http://localhost:5000")
            return
    except:
        pass
    
    try:
        # Start the Flask app
        print("Starting Flask application...")
        print("The game will be available at: http://localhost:5000")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 50)
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open('http://localhost:5000')
            except:
                pass
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\n👋 Game server stopped. Thanks for playing!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("Please check that all files are in the correct location.")

def main():
    """Main function."""
    print("🎮 Challenge Game - Startup Script")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start the application
    start_application()

if __name__ == "__main__":
    main() 