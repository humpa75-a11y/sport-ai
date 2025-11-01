"""
Quick test van Unibet Kambi API
"""

import requests
import json

url = "https://eu1.offering-api.kambicdn.com/offering/v2018/ubnl/group.json"
params = {
    'lang': 'nl_NL',
    'market': 'NL',
    'client_id': '2',
    'channel_id': '1',
    'includeLive': 'true'
}

print(f"Testing: {url}")
print(f"Params: {params}")

response = requests.get(url, params=params, timeout=10)

print(f"\nStatus: {response.status_code}")
print(f"Content-Type: {response.headers.get('Content-Type')}")

if response.status_code == 200:
    data = response.json()
    
    # Save
    with open('c:\\Users\\makem\\Desktop\\sport_ai_sync\\data\\unibet_test.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: data/unibet_test.json")
    print(f"\nData keys: {list(data.keys())}")
    
    # Check structure
    if 'events' in data:
        print(f"Events found: {len(data['events'])}")
    if 'group' in data:
        print(f"Group structure found")
        if 'groups' in data['group']:
            print(f"  Sub-groups: {len(data['group']['groups'])}")
        if 'events' in data['group']:
            print(f"  Events in group: {len(data['group']['events'])}")
    
    print("\n✅ SUCCESS - Data retrieved!")
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.text[:200])
