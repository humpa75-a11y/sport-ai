
import json
import csv
import os
import glob

# Zoek automatisch het nieuwste Unibet JSON bestand
SEARCH_PATTERNS = [
    'unibet_api_response.json',
    'data/unibet_*.json',
    'odds-portal-scraper/unibet_*.json'
]

OUTPUT_JSON = 'unibet_matches_extracted.json'
OUTPUT_CSV = 'unibet_matches_extracted.csv'

def find_latest_unibet_file():
    candidates = []
    for pattern in SEARCH_PATTERNS:
        for path in glob.glob(pattern):
            candidates.append(path)
    if not candidates:
        return None
    # Sorteer op laatste wijziging
    candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return candidates[0]

def extract_unibet_matches(data):
    matches = []
    try:
        sections = data.get('layout', {}).get('sections', [])
        for section in sections:
            for widget in section.get('widgets', []):
                if 'matches' in widget:
                    for group in widget['matches'].get('groups', []):
                        for subgroup in group.get('subGroups', []):
                            for event_obj in subgroup.get('events', []):
                                event = event_obj.get('event', {})
                                bet_offers = event_obj.get('betOffers', [])
                                main_offer = event_obj.get('mainBetOffer', {})
                                offer = main_offer if main_offer else (bet_offers[0] if bet_offers else None)
                                if not offer:
                                    continue
                                odds = {}
                                for outcome in offer.get('outcomes', []):
                                    label = outcome.get('label')
                                    odds[label] = outcome.get('oddsDecimal', outcome.get('odds', None))
                                match = {
                                    'event_id': event.get('id'),
                                    'competition': subgroup.get('name', group.get('name', '')),
                                    'home_team': event.get('homeName'),
                                    'away_team': event.get('awayName'),
                                    'start_time': event.get('start'),
                                    'odds_1': odds.get('1'),
                                    'odds_x': odds.get('X'),
                                    'odds_2': odds.get('2'),
                                    'raw_odds': odds
                                }
                                matches.append(match)
    except Exception as e:
        print(f'Fout bij extractie: {e}')
    return matches

def main():
    input_file = find_latest_unibet_file()
    if not input_file:
        print('Geen Unibet JSON bestand gevonden!')
        return
    print(f'Gevonden Unibet bestand: {input_file}')
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    matches = extract_unibet_matches(data)
    print(f'✅ Unibet wedstrijden geëxtraheerd: {len(matches)} entries')
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['event_id', 'competition', 'home_team', 'away_team', 'start_time', 'odds_1', 'odds_x', 'odds_2'])
        writer.writeheader()
        for m in matches:
            writer.writerow({
                'event_id': m['event_id'],
                'competition': m['competition'],
                'home_team': m['home_team'],
                'away_team': m['away_team'],
                'start_time': m['start_time'],
                'odds_1': m['odds_1'],
                'odds_x': m['odds_x'],
                'odds_2': m['odds_2']
            })
    print(f'➡️ Output: {OUTPUT_JSON}, {OUTPUT_CSV}')

if __name__ == '__main__':
    main()
