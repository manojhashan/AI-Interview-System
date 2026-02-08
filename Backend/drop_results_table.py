from database import engine, Base
from models import InterviewResult
from sqlalchemy import text

def drop_results():
    print("Dropping interview_results table...")
    try:
        # Try dropping via metadata first
        InterviewResult.__table__.drop(engine)
        print("Table dropped via metadata.")
    except Exception as e:
        print(f"Metadata drop failed ({e}). Trying raw SQL...")
        try:
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS interview_results"))
                conn.commit()
            print("Table dropped via SQL.")
        except Exception as e2:
            print(f"Raw SQL drop failed: {e2}")

if __name__ == "__main__":
    drop_results()
