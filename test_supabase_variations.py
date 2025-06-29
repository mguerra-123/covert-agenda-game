#!/usr/bin/env python3
"""
Test different Supabase connection variations
"""

import subprocess
import re

def test_hostname(hostname, description):
    """Test if a hostname can be resolved"""
    print(f"🔍 Testing {description}: {hostname}")
    try:
        result = subprocess.run(['nslookup', hostname, '8.8.8.8'], 
                              capture_output=True, text=True, timeout=10)
        if 'No answer' in result.stdout or 'not found' in result.stdout:
            print(f"❌ {hostname} - Cannot be resolved")
            return False
        else:
            print(f"✅ {hostname} - Resolves successfully")
            return True
    except Exception as e:
        print(f"❌ {hostname} - Error: {e}")
        return False

def test_connection_string(uri, description):
    """Test a connection string"""
    print(f"\n🔌 Testing connection: {description}")
    print(f"URI: {uri}")
    
    # Test hostname resolution first
    match = re.search(r'@([^:]+):', uri)
    if match:
        hostname = match.group(1)
        if test_hostname(hostname, f"Hostname for {description}"):
            print("✅ Hostname resolves - connection might work")
        else:
            print("❌ Hostname doesn't resolve - connection will fail")
    else:
        print("⚠️  Could not extract hostname from URI")

if __name__ == "__main__":
    print("🚀 Supabase Connection String Variations Test")
    print("=" * 60)
    
    # Your current connection string
    current_uri = "postgresql://postgres:KrFP!fP8f.!yVu&@db.vqlmpgnzuhttzssuppkw.supabase.co:5432/postgres"
    
    # Test current connection string
    test_connection_string(current_uri, "Current Direct Connection")
    
    # Test possible variations
    print("\n🔍 Testing possible hostname variations:")
    
    # Test with different possible project IDs
    possible_hostnames = [
        "db.vqlmpgnzuhttzssuppkw.supabase.co",
        "vqlmpgnzuhttzssuppkw.supabase.co", 
        "db.vqlmpgnzuhttzssuppkw.supabase.com",
        "vqlmpgnzuhttzssuppkw.supabase.com",
        "db.vqlmpgnzuhttzssuppkw.supabase.net",
        "vqlmpgnzuhttzssuppkw.supabase.net"
    ]
    
    for hostname in possible_hostnames:
        test_hostname(hostname, f"Variation: {hostname}")
    
    print("\n📋 Recommendations:")
    print("1. Double-check the project ID in your Supabase dashboard")
    print("2. Try copying the connection string again from Settings > Database")
    print("3. Check if there are any typos in the project ID")
    print("4. Try creating a new Supabase project in a different region")
    
    print("\n🔧 Next steps:")
    print("1. Go to your Supabase dashboard")
    print("2. Go to Settings > Database")
    print("3. Copy the Direct Connection URI again")
    print("4. Make sure you're copying the URI (not Connection pooling)")
    print("5. Verify the project ID matches exactly") 