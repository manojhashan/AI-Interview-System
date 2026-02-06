import requests

BASE_URL = "http://localhost:5000"

def test_login_security():
    # 1. Test Non-Existent User
    print("--- Test 1: Non-Existent User ---")
    data_fake = {
        "username": "fake_user_12345@example.com",
        "password": "randompassword"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/token", data=data_fake)
        if res.status_code == 200:
            print("❌ SECURITY FAIL: Logged in with fake user!")
            print(res.json())
        elif res.status_code == 401:
            print("✅ PASS: Correctly rejected fake user (401).")
        else:
            print(f"ℹ️ Response: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Existing User (if we know one) with WRONG password
    # We'll use the one we just registered if possible, or try a sample one from screenshot
    # Sample from screenshot: pdht20@gmail.com
    print("\n--- Test 2: Existing User + Wrong Password ---")
    data_wrong_pass = {
        "username": "pdht20@gmail.com", 
        "password": "definitely_wrong_password"
    }
    try:
        res = requests.post(f"{BASE_URL}/auth/token", data=data_wrong_pass)
        if res.status_code == 200:
            print("❌ SECURITY FAIL: Logged in with wrong password!")
            print(res.json())
        elif res.status_code == 401:
            print("✅ PASS: Correctly rejected wrong password (401).")
        else:
            print(f"ℹ️ Response: {res.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_security()
