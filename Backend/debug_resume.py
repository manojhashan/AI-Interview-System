import requests
from database import SessionLocal
from models import User

def debug_resume_flow():
    # 1. Get a test user
    db = SessionLocal()
    user = db.query(User).first()
    db.close()

    if not user:
        print("❌ No users found in DB. Cannot test.")
        return

    print(f"👉 Testing with User: {user.email} (ID: {user.user_id})")
    
    # 2. Payload matching ResumeData
    payload = {
        "id": "new",
        "resumeTitle": "Debug Resume 1",
        "skills": ["Python", "FastAPI"],
        "education": ["BSc CS"],
        "projects": ["AI Project"],
        "experience": [
            {
                "job_role": "Software Engineer",
                "startYear": "2020",
                "endYear": "2022"
            }
        ],
        "certificates": []
    }

    url = f"http://localhost:5000/api/resumes?user_id={user.user_id}"
    
    try:
        print(f"📡 Sending POST to {url}...")
        res = requests.post(url, json=payload)
        
        print(f"⬅️ Status Code: {res.status_code}")
        try:
            print(f"⬅️ Response: {res.json()}")
        except:
            print(f"⬅️ Raw Response: {res.text}")

        if res.status_code == 200:
            print("✅ Resume Saved Successfully!")
        else:
            print("❌ Save Failed.")

    except Exception as e:
        print(f"❌ Request Error: {e}")

if __name__ == "__main__":
    debug_resume_flow()
