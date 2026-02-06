import sys
import os
import site

print("--- Python Environment Info ---")
print(f"Executable: {sys.executable}")
print(f"Version: {sys.version}")
print(f"CWD: {os.getcwd()}")
print(f"\n--- Sys Path ---")
for p in sys.path:
    print(p)

print("\n--- Site Packages ---")
print(f"User Base: {site.getuserbase()}")
print(f"User Site: {site.getusersitepackages()}")

print("\n--- Attempting Imports ---")
try:
    import sqlalchemy
    print(f"✅ SQLAlchemy found at: {sqlalchemy.__file__}")
except ImportError as e:
    print(f"❌ SQLAlchemy NOT found: {e}")

try:
    import passlib
    print(f"✅ passlib found at: {passlib.__file__}")
except ImportError as e:
    print(f"❌ passlib NOT found: {e}")

try:
    import jose
    print(f"✅ python-jose found at: {jose.__file__}")
except ImportError as e:
    print(f"❌ python-jose NOT found: {e}")
