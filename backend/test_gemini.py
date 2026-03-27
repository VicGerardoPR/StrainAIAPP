import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"API Key: {api_key[:5]}...")

if not api_key:
    print("NO API KEY FOUND")
    exit(1)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-flash-latest')
try:
    response = model.generate_content("Hello, respond with ONE WORD: SUCCESS")
    print("RESPONSE:", response.text)
except Exception as e:
    print("ERROR:", e)
