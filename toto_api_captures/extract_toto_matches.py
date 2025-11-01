import json
import csv
import os

# Pad naar Toto skeleton capture
SKELETON_PATH = os.path.join(os.path.dirname(__file__), '..', 'toto_api_captures', 'capture_1_skeleton.json')
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), '..', 'toto_api_captures', 'toto_matches_extracted.json')
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), '..', 'toto_api_captures', 'toto_matches_extracted.csv')

def extract_matches():
    with open(SKELETON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    matches = []
    # Doorloop alle routes en items
    for entry in data:
        items = entry.get('items', [])
        for item in items:
            # Zoek event lists
            if item.get('type') in ['StandardEventList', 'TimebandedEventList', 'MarketsForEvent', 'HighlightEventList']:
                # Probeer events te vinden
                event_groups = item.get('eventGroups', [])
                for group in event_groups:
                    # Soms nested eventGroups
                    if 'eventGroups' in group:
                        for sub_group in group['eventGroups']:
                            events = sub_group.get('events', 0)
                            matches.append({
                                'route': entry.get('route'),
                                'subRoute': entry.get('subRoute', ''),
                                'type': item.get('type'),
                                'events_count': events
                            })
                    elif 'events' in group:
                        events = group.get('events', 0)
                        matches.append({
                            'route': entry.get('route'),
                            'subRoute': entry.get('subRoute', ''),
                            'type': item.get('type'),
                            'events_count': events
                        })
    # Opslaan als JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    # Opslaan als CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['route', 'subRoute', 'type', 'events_count'])
        writer.writeheader()
        for match in matches:
            writer.writerow(match)
    print(f"✅ Toto matches geëxtraheerd: {len(matches)} entries → {OUTPUT_JSON}, {OUTPUT_CSV}")

if __name__ == '__main__':
    extract_matches()
