from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
print("--- RESUME Table Columns ---")
for col in inspector.get_columns("resume"):
    print(f"- {col['name']}")
