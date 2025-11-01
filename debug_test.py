"""
Debug test - laat exacte error zien
"""
import requests
import json

API_URL = "http://127.0.0.1:5000"

print("\n🔍 DEBUG TEST - FC Eindhoven vs Helmond Sport")

payload = {
    "home_team": "FC Eindhoven",
    "away_team": "Helmond Sport",
    "speelronde": 10
}

try:
    response = requests.post(f"{API_URL}/api/predict", json=payload, timeout=10)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"\n❌ Error: {e}")
