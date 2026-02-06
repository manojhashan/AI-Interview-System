from database import engine, SessionLocal
from sqlalchemy import text
import sys

def test_connection():
    try:
        print("Testing database connection...")
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        print("✅ Connection Successful!")
        for row in result:
            print(f"Result: {row[0]}")
        db.close()
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
