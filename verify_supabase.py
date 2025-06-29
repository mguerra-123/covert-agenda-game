#!/usr/bin/env python3
"""
Verify Supabase connection string format
"""

import re

def verify_connection_string(uri):
    """Verify the format of a Supabase connection string"""
    print("🔍 Verifying connection string format...")
    
    # Expected pattern for Supabase PostgreSQL
    pattern = r'postgresql://postgres:([^@]+)@([^:]+):(\d+)/postgres'
    match = re.match(pattern, uri)
    
    if match:
        password = match.group(1)
        hostname = match.group(2)
        port = match.group(3)
        
        print(f"✅ Format is correct!")
        print(f"   Hostname: {hostname}")
        print(f"   Port: {port}")
        print(f"   Password length: {len(password)} characters")
        
        # Check hostname format
        if hostname.startswith('db.') and hostname.endswith('.supabase.co'):
            print(f"✅ Hostname format looks correct")
        else:
            print(f"⚠️  Hostname format might be incorrect")
            print(f"   Expected: db.[project-id].supabase.co")
            print(f"   Got: {hostname}")
            
        return True
    else:
        print("❌ Connection string format is incorrect")
        print("   Expected: postgresql://postgres:[password]@[hostname]:[port]/postgres")
        return False

def test_hostname_resolution(hostname):
    """Test if a hostname can be resolved"""
    import subprocess
    try:
        result = subprocess.run(['nslookup', hostname], 
                              capture_output=True, text=True, timeout=10)
        if 'No answer' in result.stdout or 'not found' in result.stdout:
            return False
        return True
    except:
        return False

if __name__ == "__main__":
    # Your connection string
    uri = "postgresql://postgres:YH0mrQ4SnRMPCVVQ@db.hzbgujgfbhghihaibjwj.supabase.co:5432/postgres"
    
    print("🚀 Supabase Connection String Verification")
    print("=" * 50)
    
    # Verify format
    if verify_connection_string(uri):
        # Extract hostname
        hostname = "db.hzbgujgfbhghihaibjwj.supabase.co"
        
        print(f"\n🌐 Testing hostname resolution...")
        if test_hostname_resolution(hostname):
            print(f"✅ Hostname {hostname} resolves successfully")
        else:
            print(f"❌ Hostname {hostname} cannot be resolved")
            print("\n🔧 Possible solutions:")
            print("1. Wait a few more minutes for Supabase project to finish setting up")
            print("2. Check your Supabase dashboard for the correct connection string")
            print("3. Make sure you're copying the URI from Settings > Database")
            print("4. Try creating a new Supabase project in a different region")
    
    print("\n📋 Next steps:")
    print("1. Go to your Supabase dashboard")
    print("2. Check if your project shows 'Active' status")
    print("3. Go to Settings > Database")
    print("4. Copy the URI connection string again")
    print("5. Run this script again with the new URI") 