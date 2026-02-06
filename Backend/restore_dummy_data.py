import requests
from database import SessionLocal
from models import User

def restore_data():
    # 1. Get a user
    db = SessionLocal()
    user = db.query(User).first()
    db.close()

    if not user:
        print("❌ No users found. Please sign up first.")
        return

    print(f"👉 Restoring Dummy Data for User: {user.email}")
    
    # Payload matching the original "Software Engineer" mock
    payload = {
        "id": "new",
        "resumeTitle": "Software Engineer II",
        "skills": ["React", "TypeScript", "Node.js", "Python", "AWS", "Docker"],
        "education": ["BSc Computer Science, University of Colombo (2018-2022)"],
        "projects": [
            "E-Commerce Platform: Built a full-stack marketplace using MERN stack.",
            "AI Chatbot: Implemented a RAG-based chatbot using OpenAI and Pinecone."
        ],
        "experience": [
            {
                "job_role": "Senior Software Engineer",
                "startYear": "2023",
                "endYear": "Present"
            },
            {
                "job_role": "Software Engineer Intern",
                "startYear": "2022",
                "endYear": "2023"
            }
        ],
        "certificates": ["AWS Certified Solutions Architect", "Meta Frontend Developer"]
    }

    url = f"http://localhost:5000/api/resumes?user_id={user.user_id}"
    
    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("✅ Dummy Resume Restored! Please refresh the frontend.")
        else:
            print(f"❌ Failed to restore: {res.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    restore_data()
