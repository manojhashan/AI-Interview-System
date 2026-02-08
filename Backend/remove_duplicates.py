from database import SessionLocal
from models import InterviewResult
import hashlib

def get_content_hash(r):
    # Create a unique signature based on key content fields
    # We ignore ID and date (since date string might be same but time different if we stored time, but here we store date string)
    # Actually, if the User clicked save multiple times quickly, everything is likely identical except ID.
    content = f"{r.resume_id}|{r.job_role}|{r.scores_json}"
    return hashlib.md5(content.encode()).hexdigest()

def remove_duplicates():
    db = SessionLocal()
    try:
        results = db.query(InterviewResult).all()
        print(f"Total results before cleanup: {len(results)}")
        
        seen_hashes = set()
        duplicates = []
        
        # Determine duplicates (keep first one encountered)
        for r in results:
            h = get_content_hash(r)
            if h in seen_hashes:
                duplicates.append(r)
            else:
                seen_hashes.add(h)
                
        print(f"Found {len(duplicates)} duplicates. Removing...")
        
        for dup in duplicates:
            db.delete(dup)
            print(f"Deleted duplicate ID: {dup.id}")
            
        db.commit()
        print("Cleanup complete.")
        
        remaining = db.query(InterviewResult).all()
        print(f"Total results after cleanup: {len(remaining)}")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_duplicates()
