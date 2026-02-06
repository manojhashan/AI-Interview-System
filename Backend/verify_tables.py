from database import engine
from sqlalchemy import inspect, text

def list_tables():
    inspector = inspect(engine)
    print(f"Connected to: {engine.url}")
    print("\n--- Tables in Database ---")
    tables = inspector.get_table_names()
    if not tables:
        print("Existing tables: (None)")
    tables = inspector.get_table_names()
    target_tables = ["resume", "education", "skills", "projects", "experience", "certificates"]
    if not tables:
        print("Existing tables: (None)")
    else:
        for table in tables:
            if table in target_tables:
                print(f"\n--- Table: {table} ---")
                print("  Columns:")
                for col in inspector.get_columns(table):
                    print(f"    - {col['name']} ({col['type']})")
                
                # Check foreign keys
                print("  Foreign Keys:")
                for fk in inspector.get_foreign_keys(table):
                    print(f"    - {fk}")

    # Double check schemas just in case
    print("\n--- Schemas ---")
    schemas = inspector.get_schema_names()
    print(schemas)

if __name__ == "__main__":
    import sys
    with open("tables_list.txt", "w") as f:
        sys.stdout = f
        list_tables()
