import pytest
from fastapi.testclient import TestClient
from main import app, registration_otp_storage

client = TestClient(app)

def test_signup_otp_flow():
    # Clear storage
    registration_otp_storage.clear()
    
    # Send signup request
    response = client.post(
        "/auth/signup",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "password": "strongpassword123"
        }
    )
    
    # Should ask for OTP
    assert response.status_code == 200
    assert response.json() == {"message": "OTP sent to your email address", "require_otp": True}
    
    # OTP should be in storage
    assert "testuser@example.com" in registration_otp_storage
    stored_data = registration_otp_storage["testuser@example.com"]
    otp = stored_data["otp"]
    
    # Verify OTP
    verify_response = client.post(
        "/auth/verify-signup-otp",
        json={
            "email": "testuser@example.com",
            "otp": otp
        }
    )
    
    # Should succeed and return token
    assert verify_response.status_code == 200
    json_data = verify_response.json()
    assert "access_token" in json_data
    assert json_data["user_id"].startswith("U")
    assert "testuser@example.com" not in registration_otp_storage
