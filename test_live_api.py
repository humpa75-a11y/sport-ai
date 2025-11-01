"""
🧪 TEST SCRIPT - Live Matches API
"""

import sys
sys.path.append('backend')

from live_matches_api import LiveMatchesAPI

print("="*80)
print("🧪 TESTING LIVE MATCHES API")
print("="*80)

# Test API
api = LiveMatchesAPI()
matches = api.get_todays_matches()

print(f"\n✅ Total matches found: {len(matches)}")
print("\n📅 UPCOMING MATCHES (TODAY/TOMORROW):\n")

for i, match in enumerate(matches[:15], 1):
    from datetime import datetime
    kickoff = datetime.fromisoformat(match['commence_time'])
    
    print(f"{i:2}. {match['competition']:20} | {match['home_team']:25} vs {match['away_team']:25}")
    print(f"    ⏰ {kickoff.strftime('%A %d %B, %H:%M')}")
    print()

print("="*80)
print("✅ TEST COMPLETE!")
print("="*80)
