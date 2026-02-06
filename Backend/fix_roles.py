from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User

def fix_roles():
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.role == "Candidate").all()
        print(f"Found {len(users)} users with 'Candidate' role.")
        for user in users:
            print(f"Updating user {user.email} role to 'CANDIDATE'")
            user.role = "CANDIDATE"
        
        db.commit()
        print("✅ Roles updated successfully.")
    except Exception as e:
        print(f"❌ Error updating roles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_roles()
