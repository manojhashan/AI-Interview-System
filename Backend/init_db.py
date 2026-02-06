from database import engine
from models import Base, User, Resume, Education, Experience, Project, Skill, Certificate

print("--- Initializing Database ---")
try:
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
except Exception as e:
    print(f"❌ Error creating tables: {e}")
