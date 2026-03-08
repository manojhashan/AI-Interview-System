import os
from dotenv import load_dotenv

# Load exactly the file the user just edited
load_dotenv(".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")
print("API KEY:", api_key[:10] if api_key else None)

from google import genai
try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.0-flash-lite',
        contents='Say hello'
    )
    print("SUCCESS:", response.text)
except Exception as e:
    print("ERROR:", e)
