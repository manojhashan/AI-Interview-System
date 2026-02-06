from database import SessionLocal
from models import InterviewResult, User
import json

def check_results():
    db = SessionLocal()
    try:
        results = db.query(InterviewResult).all()
        print(f"Total Results found: {len(results)}")
        for r in results:
            print(f"ID: {r.id}, Candidate: {r.candidate_name} ({r.candidate_id}), Role: {r.job_role}, Date: {r.date}")
            print(f"Scores: {r.scores_json[:50]}...") # Print first 50 chars
            print("-" * 20)
            
        if len(results) == 0:
            print("No results found in the 'interview_results' table.")
            
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_results()
