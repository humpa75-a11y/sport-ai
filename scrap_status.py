import os
import json
from datetime import datetime

SCRAPER_FILES = [
    'unibet_matches.json',
    'toto_matches.json',
    'flashscore_matches.json',
    'hollandcasino_matches.json',
    'jacks_matches.json'
]
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def check_scrap_status():
    status = []
    for fname in SCRAPER_FILES:
        fpath = os.path.join(DATA_DIR, fname)
        info = {
            'source': fname.replace('_matches.json',''),
            'file': fname,
            'match_count': 0,
            'last_update': None
        }
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    info['match_count'] = len(data)
                info['last_update'] = datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat()
            except Exception as e:
                info['error'] = str(e)
        else:
            info['error'] = 'File not found'
        status.append(info)
    return status

if __name__ == '__main__':
    print('--- SCRAPER STATUS OVERVIEW ---')
    for s in check_scrap_status():
        print(f"Source: {s['source']}")
        print(f"  File: {s['file']}")
        print(f"  Matches: {s['match_count']}")
        print(f"  Last update: {s['last_update']}")
        if 'error' in s:
            print(f"  Error: {s['error']}")
        print('-'*40)
