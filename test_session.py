#!/usr/bin/env python3
"""
Test script for Flask session management
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:10000"

def test_session_management():
    """Test session creation and validation"""
    print("🧪 Testing Flask Session Management...")
    
    # Test 1: Check session endpoint before login
    print("\n1. Testing session check before login...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/session")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Test login endpoint (this should create a session)
    print("\n2. Testing login endpoint...")
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "device_id": "test-device"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Check session endpoint after login attempt
    print("\n3. Testing session check after login...")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/session")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Session management test completed!")

if __name__ == "__main__":
    test_session_management() 