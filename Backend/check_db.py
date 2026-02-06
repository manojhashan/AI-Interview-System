from database import engine
from sqlalchemy import inspect

try:
    inspector = inspect(engine)
    print("Tables:", inspector.get_table_names())
    print("--- RESUME COLUMNS ---")
    for col in inspector.get_columns("resume"):
        print(f"{col['name']} - {col['type']}")
except Exception as e:
    print("Error:", e)
