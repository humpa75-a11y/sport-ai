"""
🎯 BETTING MARKETS & PERIODS
Complete market definitions for football betting

All available bet types across different time periods
"""

BETTING_PERIODS = {
    0: {
        "name": "Full Match",
        "markets": ["1X2", "Handicap", "Over/Under", "BTTS", "Team Goals"]
    },
    1: {
        "name": "1st Half",
        "markets": ["1H 1X2", "1H Handicap", "1H O/U", "1H Goals"]
    },
    2: {
        "name": "2nd Half",
        "markets": ["2H 1X2", "2H Handicap", "2H O/U", "2H Goals"]
    }
}

# Time-based markets
TIME_PERIODS = [
    {"period": "0-15", "minutes": "00:00 - 14:59"},
    {"period": "15-30", "minutes": "15:00 - 29:59"},
    {"period": "30-HT", "minutes": "30:00 - Halftime"},
    {"period": "HT-60", "minutes": "Halftime - 59:59"},
    {"period": "60-75", "minutes": "60:00 - 74:59"},
    {"period": "75-FT", "minutes": "75:00 - Fulltime"}
]

# Market types voor ons systeem
OUR_MARKETS = [
    "1X2",              # Match winner
    "Over/Under 2.5",   # Total goals
    "Over/Under 1.5",   
    "BTTS",             # Both teams to score
    "1H 1X2",           # First half winner
    "Handicap"          # Asian handicap
]

print("✅ Betting markets loaded")
print(f"   - {len(BETTING_PERIODS)} periods")
print(f"   - {len(TIME_PERIODS)} time periods")
print(f"   - {len(OUR_MARKETS)} market types")
