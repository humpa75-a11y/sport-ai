"""Quick debug to see what betoffers we get for an event"""
import json

with open('data/unibet_raw_20251015_050954.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data['events']
betoffers = {bo['id']: bo for bo in data['betOffers']}

# Take first event
first_event = events[0]
print(f"First event: {first_event['homeName']} vs {first_event['awayName']}")
print(f"Event ID: {first_event['id']}")
print()

# Find betoffers for this event
event_betoffers = [bo for bo in betoffers.values() if bo.get('eventId') == first_event['id']]
print(f"Found {len(event_betoffers)} betoffers for this event")
print()

# Show first few
for i, bo in enumerate(event_betoffers[:5]):
    criterion = bo.get('criterion', {}).get('label', '')
    print(f"{i+1}. {criterion}")
    print(f"   Type: {bo.get('betOfferType', {}).get('name', '')}")
    print(f"   Outcomes: {len(bo.get('outcomes', []))}")
    
    # Show outcomes
    for outcome in bo.get('outcomes', [])[:3]:
        label = outcome.get('label', '')
        odds = outcome.get('odds', 0) / 1000
        print(f"      - {label}: {odds:.2f}")
    print()
