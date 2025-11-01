"""Test Holland Casino sportswidget API"""
import requests
import json

base_url = "https://sportswidget.hollandcasino.nl"

# Test endpoints
endpoints = [
    '/config',
    '/configuration/init',
    '/health/status',
]

print("="*60)
print("🎰 TESTING HOLLAND CASINO API")
print("="*60)

for endpoint in endpoints:
    url = base_url + endpoint
    print(f"\nTesting: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json() if 'json' in response.headers.get('content-type', '') else response.text
            print(f"Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())[:10]}")
            print(f"Size: {len(str(data))} chars")
            
            # Save if interesting
            if isinstance(data, dict) and len(data) > 10:
                filename = f"data/holland_casino_{endpoint.replace('/', '_')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                print(f"💾 Saved to: {filename}")
    
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*60)
