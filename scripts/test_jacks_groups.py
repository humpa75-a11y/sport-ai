"""Quick test to find Jacks.nl football group structure"""
import requests
import json

base_url = "https://eu1.offering-api.kambicdn.com/offering/v2018/jvh"

# Try group.json like Unibet
url = f"{base_url}/group.json"
params = {
    'lang': 'nl_NL',
    'market': 'NL'
}

response = requests.get(url, params=params, timeout=10)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Keys: {list(data.keys())}")
    
    # Save it
    with open('data/jacks_group_structure.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Find football
    if 'groups' in data:
        groups = data['groups']
        print(f"\nFound {len(groups)} groups:")
        for g in groups:
            name = g.get('name', '')
            gid = g.get('id', '')
            if 'voetbal' in name.lower() or 'football' in name.lower():
                print(f"  ⚽ FOOTBALL: {name} (ID: {gid})")
            else:
                print(f"  - {name}")
else:
    print(f"Error: {response.text[:200]}")
