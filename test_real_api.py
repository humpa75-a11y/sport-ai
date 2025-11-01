"""
🔥 TEST REAL API - API-Sports.io Integration

Test met jouw API key voor ECHTE data
"""

import sys
sys.path.append('.')

from backend import multi_source_aggregator

print("="*80)
print("TEST REAL API MODE - API-SPORTS.IO")
print("="*80)
print("API Key: eec52f29ffbc24effa9bc0e7963a8cd9")
print("="*80)

# Test met echte API voor volgende paar dagen
print("\n1. Testing REAL API - Next 7 days across ALL leagues...")
df = multi_source_aggregator.run_full_analysis(
    league='bundesliga',
    days_ahead=7,
    demo_mode=False,
    use_real_api=True  # REAL DATA!
)

if not df.empty:
    print(f"\nSUCCESS! Got {len(df)} REAL matches from API")
    print("\nSample matches:")
    print(df[['match_date', 'match_time', 'home', 'away', 'tournament']].head(5).to_string(index=False))
    
    print("\nPredictions preview:")
    print(df[['match', 'odds_1x2', 'best_bet']].head(3).to_string(index=False))
else:
    print("\nNo matches found (might be off-season)")

print("\n" + "="*80)
print("REAL API INTEGRATION COMPLETE!")
print("="*80)
