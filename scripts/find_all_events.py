import json

def find_events_recursive(group, path="", level=0):
    """Recursively find all events"""
    name = group.get('name', group.get('englishName', 'Unknown'))
    current_path = f"{path}/{name}" if path else name
    
    events = []
    
    # Check for events at this level
    if 'events' in group and len(group['events']) > 0:
        print(f"{'  '*level}🎯 {name}: {len(group['events'])} events")
        events.extend(group['events'])
    
    # Recurse into sub-groups
    if 'groups' in group:
        for sg in group['groups']:
            sub_events = find_events_recursive(sg, current_path, level+1)
            events.extend(sub_events)
    
    return events


data = json.load(open('c:\\Users\\makem\\Desktop\\sport_ai_sync\\data\\unibet_test.json', encoding='utf-8'))

groups = data['group']['groups']

# Find football
for g in groups:
    if 'voetbal' in g.get('name', '').lower():
        print(f"\n⚽ Scanning FOOTBALL structure...\n")
        all_events = find_events_recursive(g)
        
        print(f"\n{'='*60}")
        print(f"TOTAL EVENTS FOUND: {len(all_events)}")
        print(f"{'='*60}")
        
        if all_events:
            print(f"\n📋 Sample matches (first 10):\n")
            for i, event in enumerate(all_events[:10]):
                event_name = event.get('event', {}).get('name', 'No name')
                start = event.get('event', {}).get('start', 'No time')
                path = event.get('event', {}).get('path', [])
                league = path[0].get('name') if path else 'Unknown'
                
                print(f"{i+1:2}. {event_name:40} | {league:25} | {start[:16]}")
        
        break
