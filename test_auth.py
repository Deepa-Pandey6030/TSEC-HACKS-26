"""
Quick test script for auth system
Run after backend is running
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_signup():
    print("\n--- Testing Signup ---")
    data = {
        "name": "Test User",
        "email": f"test{hash('test')%10000}@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/signup", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    return result.get("token") if result.get("success") else None

def test_login(email, password):
    print("\n--- Testing Login ---")
    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/login", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    return result.get("token") if result.get("success") else None

def test_check_session(token):
    print("\n--- Testing Check Session ---")
    data = {"session_token": token}
    response = requests.post(f"{BASE_URL}/check-session", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    return result.get("valid")

def test_logout(token):
    print("\n--- Testing Logout ---")
    data = {"session_token": token}
    response = requests.post(f"{BASE_URL}/logout", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    try:
        # Test signup
        token = test_signup()
        
        if token:
            # Test check session
            is_valid = test_check_session(token)
            
            if is_valid:
                # Test logout
                test_logout(token)
                
                # Check session after logout
                test_check_session(token)
            
            print("\n✅ Auth system working!")
        else:
            print("\n❌ Signup failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running on localhost:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")
