from database import engine
from sqlalchemy import text, inspect

def reset_tables():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    # Order matters due to Foreign Keys
    tables_to_drop = ["education", "experience", "projects", "skills", "certificates", "resume"]
    
    with engine.connect() as conn:
        print("--- Dropping Tables (CASCADE) ---")
        for table in tables_to_drop:
            if table in existing_tables:
                print(f"Dropping {table}...")
                conn.execute(text(f"DROP TABLE {table} CASCADE"))
        conn.commit()
    print("✅ Tables dropped. Please restart 'main.py' to recreate them.")

if __name__ == "__main__":
    reset_tables()
