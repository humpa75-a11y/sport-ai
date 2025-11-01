import json

with open('data/massive_training_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"\n📊 DATA CHECK:")
print(f"   Totaal wedstrijden: {len(data)}")
print(f"   Eredivisie: {len([m for m in data if 'eredivisie' in m['competition']])}")
print(f"   Eerste Divisie: {len([m for m in data if 'eerste_divisie' in m['competition']])}")
