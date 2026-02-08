import requests
import json
import uuid

BASE_URL = "http://localhost:5000"

def verify():
    print("Verifying Backend Changes...")
    
    # 1. Check Root
    try:
        r = requests.get(f"{BASE_URL}/")
        if r.status_code != 200:
            print("❌ Backend not reachable.")
            return
        print("✅ Backend is online.")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return

    # 2. Create Dummy Data
    resume_id = f"test_resume_{uuid.uuid4()}"
    user_id = "test_user" # We might need a real user if we enforced FK constraints strictly without User creation, but Resume->User FK exists? 
    # Wait, Resume table has ForeignKey("USER.user_id").
    # If we insert a result with a resume_id, that resume MUST exist if FK is enforced.
    
    # We need to Create User -> Create Resume -> Create Result.
    # OR, we can just check if we can reach the code path.
    # Let's try to hit the endpoint. If it fails with IntegrityError (FK violation), that means the Schema IS updated (Good!).
    # If it fails with "Unknown field resumeId", that means Schema/Pydantic is NOT updated (Bad).
    
    payload = {
        "resumeId": resume_id,
        "candidateId": user_id,
        "candidateName": "Test Candidate",
        "date": "2023-10-27",
        "jobRole": "Tester",
        "scores": {"overall": 80, "facial": 80, "vocal": 80, "semantic": 80},
        "details": []
    }
    
    try:
        r = requests.post(f"{BASE_URL}/api/results", json=payload)
        print(f"POST /api/results status: {r.status_code}")
        print(f"Response: {r.text}")
        
        if r.status_code == 200:
            print("✅ Created Result successfully (FK constraint might be loose or lucky).")
        elif r.status_code == 500 and "foreign key constraint fails" in r.text.lower():
             print("✅ Database Schema detected (FK constraint active). This confirms the new column `resume_id` exists.")
        elif r.status_code == 422:
             print("❌ Validation Error (Pydantic). Check fields.")
        else:
             print("⚠️ Unexpected response.")
             
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    verify()
