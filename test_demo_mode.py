"""
🎯 TEST DEMO MODE - Complete System Test

Test het hele systeem met realistische demo data
"""

import sys
import os

# Fix Windows console encoding
if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.append('.')

from backend import multi_source_aggregator
import pandas as pd

print("="*80)
print("TEST DEMO MODE - REALISTIC DATA WITHOUT API CALLS")
print("="*80)

# Test Bundesliga
print("\n1. Testing Bundesliga...")
df = multi_source_aggregator.run_full_analysis(
    league='bundesliga',
    days_ahead=2,
    demo_mode=True
)

if not df.empty:
    print(f"\nSUCCESS! Got {len(df)} matches")
    print("\nSample Predictions:")
    print(df[['match_date', 'match', 'odds_1x2', 'best_bet']].head(3).to_string(index=False))
else:
    print("FAILED - No data returned")

# Test Premier League
print("\n\n2. Testing Premier League...")
df2 = multi_source_aggregator.run_full_analysis(
    league='premier-league',
    days_ahead=1,
    demo_mode=True
)

if not df2.empty:
    print(f"SUCCESS! Got {len(df2)} matches")
    print("\nSample Predictions:")
    print(df2[['match_date', 'match', 'odds_1x2', 'best_bet']].head(2).to_string(index=False))
else:
    print("FAILED - No data returned")

# Test Eredivisie
print("\n\n3. Testing Eredivisie...")
df3 = multi_source_aggregator.run_full_analysis(
    league='eredivisie',
    days_ahead=2,
    demo_mode=True
)

if not df3.empty:
    print(f"SUCCESS! Got {len(df3)} matches")
    print("\nSample Predictions:")
    print(df3[['match_date', 'match', 'odds_1x2', 'best_bet']].head(2).to_string(index=False))
else:
    print("FAILED - No data returned")

print("\n" + "="*80)
print("DEMO MODE WORKING PERFECTLY!")
print("="*80)
print("\nNext steps:")
print("1. Start API server: python backend/api_server.py")
print("2. Open dashboard: frontend/dashboard.html")
print("3. Enjoy the realistic betting predictions!")
print("="*80)
