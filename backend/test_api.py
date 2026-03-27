import requests
import base64

url = "http://localhost:8000/extract"
files = {'file': open('/Users/victorg/Documents/StrainAIAPP/frontend/test_report.png', 'rb')}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, files=files)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.json())
except Exception as e:
    print("ERROR:", e)
