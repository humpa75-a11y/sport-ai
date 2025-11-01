"""
Test ALLE relevante Kambi endpoints
"""

import requests
import json

base = "https://eu1.offering-api.kambicdn.com/offering/v2018/ubnl"

endpoints_to_try = [
    # Highlight - featured matches
    {
        'path': '/group/highlight.json',
        'params': {
            'lang': 'nl_NL',
            'market': 'NL',
            'client_id': '2',
            'channel_id': '1',
            'depth': '0'
        }
    },
    # List view - all matches
    {
        'path': '/listView/football/all/matches.json',
        'params': {
            'lang': 'nl_NL',
            'market': 'NL',
            'client_id': '2',
            'channel_id': '1'
        }
    },
    # Betoffer - specific football group
    {
        'path': '/betoffer/group/1000093190.json',  # Football group ID
        'params': {
            'lang': 'nl_NL',
            'market': 'NL'
        }
    },
]

for i, endpoint in enumerate(endpoints_to_try, 1):
    url = f"{base}{endpoint['path']}"
    print(f"\n{'='*70}")
    print(f"Test #{i}: {endpoint['path']}")
    print(f"{'='*70}")
    
    try:
        response = requests.get(url, params=endpoint['params'], timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Count events
            def count_events(obj, depth=0):
                if depth > 10:
                    return 0
                count = 0
                if isinstance(obj, dict):
                    if 'events' in obj and isinstance(obj['events'], list):
                        count += len(obj['events'])
                    for value in obj.values():
                        count += count_events(value, depth+1)
                elif isinstance(obj, list):
                    for item in obj:
                        count += count_events(item, depth+1)
                return count
            
            total_events = count_events(data)
            
            print(f"✅ SUCCESS!")
            print(f"Keys: {list(data.keys())}")
            print(f"Total events found: {total_events}")
            
            if total_events > 0:
                # Save this one!
                filename = f"c:\\Users\\makem\\Desktop\\sport_ai_sync\\data\\unibet_working_endpoint_{i}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"💾 Saved to: {filename}")
                print(f"\n🎉 FOUND WORKING ENDPOINT WITH {total_events} EVENTS!")
                break
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text[:200])
    
    except Exception as e:
        print(f"❌ Exception: {e}")

print(f"\n{'='*70}")
print("Test complete!")
