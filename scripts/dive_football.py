import json

data = json.load(open('c:\\Users\\makem\\Desktop\\sport_ai_sync\\data\\unibet_test.json', encoding='utf-8'))

groups = data['group']['groups']

# Find football
for g in groups:
    if 'voetbal' in g.get('name', '').lower() or 'football' in g.get('name', '').lower():
        print(f"\n⚽ FOOTBALL GROUP: {g.get('name')}")
        print(f"   ID: {g.get('id')}")
        print(f"   Path: {g.get('path', [])}")
        
        # Check for sub-groups
        if 'groups' in g:
            print(f"\n   📂 Sub-groups ({len(g['groups'])}):")
            for i, sg in enumerate(g['groups'][:10]):
                name = sg.get('name', sg.get('englishName'))
                event_count = len(sg.get('events', []))
                print(f"   {i+1}. {name:35} | Events: {event_count:3}")
                
                # Show sample event if any
                if event_count > 0:
                    event = sg['events'][0]
                    event_name = event.get('event', {}).get('name', 'No name')
                    print(f"      Sample: {event_name}")
        
        # Check if the group itself has events
        if 'events' in g and len(g['events']) > 0:
            print(f"\n   🎯 Direct events: {len(g['events'])}")
            for i, event in enumerate(g['events'][:3]):
                event_name = event.get('event', {}).get('name', 'No name')
                print(f"   {i+1}. {event_name}")
        
        break
