import requests
import json

BASE_URL = "https://ui-flask-homesec.onrender.com"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test an endpoint and return status code and response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        
        return response.status_code, response.text
    except Exception as e:
        return f"ERROR: {str(e)}", ""

def print_result(endpoint, method, status_code, response):
    """Print formatted test result"""
    print(f"🔍 {method} {endpoint}")
    print(f"   Status: {status_code}")
    if response:
        try:
            json_response = json.loads(response)
            print(f"   Response: {json.dumps(json_response, indent=2)}")
        except:
            print(f"   Response: {response[:200]}...")
    print("-" * 50)

def main():
    print("🚀 Testing All Endpoints")
    print("=" * 50)
    
    # Test data
    test_login_data = {
        "email": "test@gmail.com",
        "password": "12345678",
        "device_id" :"12345678"
    }
    
    test_user_data = {
        "email": "newemail@test.com",
        "phone": "+1234567890"
    }
    
    test_password_data = {
        "currentPassword": "admin123",
        "newPassword": "newpassword123"
    }
    
    test_reset_data = {
        "email": "admin@test.com"
    }
    
    # 1. Health Check (Public)
    print("\n📋 1. HEALTH CHECK")
    status, response = test_endpoint("GET", "/api/health")
    print_result("/api/health", "GET", status, response)
    
    # 2. Authentication (Public)
    print("\n📋 2. AUTHENTICATION")
    status, response = test_endpoint("POST", "/api/auth/login", test_login_data)
    print_result("/api/auth/login", "POST", status, response)
    
    # 3. User Management (Protected - will likely fail without auth)
    print("\n📋 3. USER MANAGEMENT")
    status, response = test_endpoint("GET", "/api/users/me")
    print_result("/api/users/me", "GET", status, response)
    
    status, response = test_endpoint("PUT", "/api/users/email", {"email": "new@test.com"})
    print_result("/api/users/email", "PUT", status, response)
    
    status, response = test_endpoint("PUT", "/api/users/phone", {"phone": "+1234567890"})
    print_result("/api/users/phone", "PUT", status, response)
    
    status, response = test_endpoint("PUT", "/api/users/password", test_password_data)
    print_result("/api/users/password", "PUT", status, response)
    
    # 4. Device Management (Protected)
    print("\n📋 4. DEVICE MANAGEMENT")
    status, response = test_endpoint("GET", "/api/devices/me")
    print_result("/api/devices/me", "GET", status, response)
    
    status, response = test_endpoint("GET", "/api/devices/status")
    print_result("/api/devices/status", "GET", status, response)
    
    # 5. Alerts (Protected)
    print("\n📋 5. ALERTS")
    status, response = test_endpoint("GET", "/api/alerts")
    print_result("/api/alerts", "GET", status, response)
    
    status, response = test_endpoint("GET", "/api/sse/alerts")
    print_result("/api/sse/alerts", "GET", status, response)
    
    # 6. Password Resets (Public)
    print("\n📋 6. PASSWORD RESETS")
    status, response = test_endpoint("POST", "/api/password-resets/request", test_reset_data)
    print_result("/api/password-resets/request", "POST", status, response)
    
    status, response = test_endpoint("POST", "/api/password-resets/reset", {"token": "test", "password": "newpass"})
    print_result("/api/password-resets/reset", "POST", status, response)
    
    # 7. Logout (Public)
    print("\n📋 7. LOGOUT")
    status, response = test_endpoint("POST", "/api/auth/logout")
    print_result("/api/auth/logout", "POST", status, response)
    
    print("\n✅ Endpoint testing complete!")

if __name__ == "__main__":
    main() 