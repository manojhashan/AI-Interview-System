import requests
import json

def test_generate_questions():
    url = "http://127.0.0.1:5000/api/generate-questions"
    payload = {
        "resume": {
            "skills": ["Python", "Flask"],
            "experience": "2 years"
        },
        "jobRole": "Backend Developer"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate_questions()
