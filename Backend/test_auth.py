import requests
import json

BASE_URL = "http://localhost:5000"

def test_auth():
    # 1. Register
    print("Testing Registration...")
    signup_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "testuser_auth@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        if response.status_code == 200:
            print("✅ Registration Successful")
            print(f"Token: {response.json().get('access_token')[:20]}...")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️ User already exists (Skipping reg)...")
        else:
            print(f"❌ Registration Failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Login
    print("\nTesting Login...")
    login_data = {
        "username": "testuser_auth@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
        if response.status_code == 200:
            print("✅ Login Successful")
            print(f"Token: {response.json().get('access_token')[:20]}...")
        else:
            print(f"❌ Login Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_auth()
