import json

d = json.load(open('data/jacks_group_structure.json'))
g = d['group']

print('Keys:', list(g.keys()))
print('Name:', g.get('name'))
print('ID:', g.get('id'))

groups = g.get('groups', [])
print(f'\nSub-groups: {len(groups)}')
for sg in groups[:15]:
    name = sg.get('name', '')
    gid = sg.get('id', '')
    if 'voetbal' in name.lower() or 'football' in name.lower():
        print(f"  ⚽ {name} (ID: {gid})")
    else:
        print(f"  - {name} (ID: {gid})")
