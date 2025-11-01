import json

data = json.load(open('c:\\Users\\makem\\Desktop\\sport_ai_sync\\data\\unibet_test.json', encoding='utf-8'))

groups = data['group']['groups']

print(f"\n🎯 Found {len(groups)} groups:\n")

for i, g in enumerate(groups[:15]):
    name = g.get('name', g.get('englishName', 'No name'))
    path_id = g.get('pathTermId', 'No ID')
    event_count = len(g.get('events', []))
    
    print(f"{i+1:2}. {name:40} | Events: {event_count:3} | ID: {path_id}")
    
    # Check for football
    if 'foot' in name.lower() or 'voetbal' in name.lower():
        print(f"    ⚽ FOOTBALL GROUP FOUND!")
