import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"Loaded API Key: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment variables.")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash')

print("Attempting to generate content...")
try:
    start_time = time.time()
    response = model.generate_content("Say 'Hello' if you find this message.")
    end_time = time.time()
    print(f"✅ Success! Response: {response.text}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
except Exception as e:
    print(f"❌ Error: {e}")
