from database import engine
from sqlalchemy import text

def fix_schema():
    with engine.connect() as connection:
        # Enable auto-commit for the transaction
        connection.execution_options(isolation_level="AUTOCOMMIT")
        
        try:
            print("Attempting to alter 'role' column type to VARCHAR(50)...")
            connection.execute(text('ALTER TABLE "USER" ALTER COLUMN role TYPE VARCHAR(50);'))
            print("Successfully altered 'role' column.")
        except Exception as e:
            print(f"Error altering role: {e}")

        try:
            print("Attempting to alter 'user_id' column type to VARCHAR(50)...")
            connection.execute(text('ALTER TABLE "USER" ALTER COLUMN user_id TYPE VARCHAR(50);'))
            print("Successfully altered 'user_id' column.")
        except Exception as e:
            print(f"Error altering user_id: {e}")

if __name__ == "__main__":
    fix_schema()
