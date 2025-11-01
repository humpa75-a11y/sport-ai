"""
🔥 PRODUCTION SETUP - ECHTE DATA
Gebruik API-Sports.io met jouw key voor ECHTE wedstrijden
"""

import sys
sys.path.append('.')

from backend import multi_source_aggregator
import pandas as pd

print("="*80)
print("PRODUCTION MODE - REAL API DATA")
print("="*80)
print("\nAPI: API-Sports.io")
print("Key: eec52f29ffbc24effa9bc0e7963a8cd9")
print("Limit: 100 calls/day")
print("="*80)

# Haal ECHTE fixtures van ALLE competities voor komende week
print("\n1. Fetching REAL fixtures for next 7 days...")
print("   Testing multiple leagues...\n")

leagues_to_test = [
    ('premier-league', 'Premier League'),
    ('bundesliga', 'Bundesliga'),
    ('la-liga', 'La Liga'),
    ('serie-a', 'Serie A'),
    ('eredivisie', 'Eredivisie')
]

all_matches = []

for league_code, league_name in leagues_to_test:
    print(f"\n📊 {league_name}:")
    
    df = multi_source_aggregator.run_full_analysis(
        league=league_code,
        days_ahead=7,
        demo_mode=False,
        use_real_api=True
    )
    
    if not df.empty:
        # Check if it's real data (has fixture_id) or demo fallback
        if 'fixture_id' in df.columns:
            print(f"   ✅ REAL DATA: {len(df)} matches")
            all_matches.extend(df.to_dict('records'))
        else:
            print(f"   ⚠️ No matches (using demo fallback)")
    else:
        print(f"   ⚠️ No matches found")

print("\n" + "="*80)
if len(all_matches) > 0:
    print(f"✅ TOTAL REAL MATCHES: {len(all_matches)}")
    print("\nSample real matches:")
    for i, match in enumerate(all_matches[:5], 1):
        print(f"{i}. {match.get('match', 'N/A')} - {match.get('match_date', 'N/A')}")
else:
    print("⚠️ No real matches in next 7 days (might be international break)")
    print("\nTIP: Try expanding date range or check match schedule:")
    print("   - November is often international break")
    print("   - Try days_ahead=14 for more fixtures")

print("="*80)
