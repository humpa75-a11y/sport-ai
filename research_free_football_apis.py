"""
ONDERZOEK: Gratis Voetbal APIs voor Sport AI
==============================================

We hebben nu:
- API-Football (100 calls/dag) ✅ WORKING
- Sofascore (403 Forbidden) ❌ BLOCKED

Laten we testen welke andere APIs we kunnen gebruiken:
"""

import requests
import json
from datetime import datetime

print("="*80)
print("🔍 TESTING FREE FOOTBALL APIs")
print("="*80)

# =============================================================================
# 1. FOOTBALL-DATA.ORG (Gratis tier beschikbaar)
# =============================================================================
print("\n1. Testing Football-Data.org API...")
print("-"*80)
try:
    # Gratis tier: 10 calls/minuut, alleen competitions endpoints
    headers = {
        'X-Auth-Token': 'YOUR_TOKEN_HERE'  # User moet token aanvragen
    }
    response = requests.get(
        'https://api.football-data.org/v4/competitions',
        headers=headers,
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ WORKING! Competitions available: {len(data.get('competitions', []))}")
    elif response.status_code == 401:
        print("⚠️  Needs API token (free tier beschikbaar)")
        print("   Sign up: https://www.football-data.org/client/register")
        print("   Features: Live scores, fixtures, standings, player stats")
        print("   Free tier: 10 calls/minute")
except Exception as e:
    print(f"❌ Error: {e}")

# =============================================================================
# 2. THE ODDS API (Voor betting odds)
# =============================================================================
print("\n2. Testing The Odds API...")
print("-"*80)
try:
    # 500 requests per month gratis
    api_key = 'YOUR_ODDS_API_KEY'  # User moet key aanvragen
    response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/soccer_epl/odds',
        params={
            'apiKey': api_key,
            'regions': 'eu',
            'markets': 'h2h,spreads,totals'
        },
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ WORKING! Real-time betting odds")
    elif response.status_code == 401:
        print("⚠️  Needs API key (free tier: 500 requests/month)")
        print("   Sign up: https://the-odds-api.com/")
        print("   Features: Live betting odds from 80+ bookmakers")
except Exception as e:
    print(f"❌ Error: {e}")

# =============================================================================
# 3. OPENLIGADB (Duits voetbal - VOLLEDIG GRATIS!)
# =============================================================================
print("\n3. Testing OpenLigaDB (German football - FREE)...")
print("-"*80)
try:
    # Geen API key nodig! Volledig gratis
    response = requests.get(
        'https://api.openligadb.de/getmatchdata/bl1/2024',
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ WORKING! Bundesliga matches found: {len(data)}")
        if data:
            match = data[0]
            print(f"   Example: {match['team1']['teamName']} vs {match['team2']['teamName']}")
            print(f"   Date: {match.get('matchDateTime', 'N/A')}")
        print("   Features: Bundesliga 1 & 2, live scores, fixtures")
        print("   Rate limit: Geen limiet! Volledig gratis!")
except Exception as e:
    print(f"❌ Error: {e}")

# =============================================================================
# 4. FOOTYSTATS (Gratis tier met statistieken)
# =============================================================================
print("\n4. Testing FootyStats API...")
print("-"*80)
try:
    api_key = 'YOUR_FOOTYSTATS_KEY'  # Gratis tier beschikbaar
    response = requests.get(
        f'https://api.footystats.org/leagues?key={api_key}',
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ WORKING! Advanced football statistics")
    elif response.status_code in [401, 403]:
        print("⚠️  Needs API key (free tier beschikbaar)")
        print("   Sign up: https://footystats.org/api/")
        print("   Features: xG, team stats, predictions, trends")
        print("   Free tier: 100 calls/day")
except Exception as e:
    print(f"❌ Error: {e}")

# =============================================================================
# 5. UNDERSTAT (Scraping mogelijk - xG data!)
# =============================================================================
print("\n5. Testing Understat (xG specialist)...")
print("-"*80)
try:
    # Geen officiële API maar wel scraping mogelijk
    response = requests.get(
        'https://understat.com/league/EPL/2024',
        timeout=5
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Website bereikbaar - scraping mogelijk")
        print("   Features: xG, xA, shot maps, detailed analytics")
        print("   Method: Web scraping (geen officiële API)")
        print("   Note: Check robots.txt en rate limiting")
except Exception as e:
    print(f"❌ Error: {e}")

# =============================================================================
# 6. LIVESCORE (Mogelijk voor live data)
# =============================================================================
print("\n6. Testing LiveScore alternatives...")
print("-"*80)
print("⚠️  LiveScore heeft geen officiële API")
print("   Alternatieven:")
print("   - FlashScore (scraping)")
print("   - SofaScore (blocked voor ons)")
print("   - ESPN API (unofficial endpoints)")

# =============================================================================
# SAMENVATTING
# =============================================================================
print("\n" + "="*80)
print("📊 SAMENVATTING - BESTE OPTIES")
print("="*80)
print("""
MEEST VEELBELOVEND:

1. ✅ OPENLIGADB (Bundesliga)
   - VOLLEDIG GRATIS, geen limiet
   - Live scores + fixtures
   - Direct te integreren
   
2. ⭐ FOOTBALL-DATA.ORG
   - Gratis tier: 10 calls/minuut
   - Veel competities
   - Player stats, standings
   
3. ⭐ THE ODDS API
   - 500 requests/maand gratis
   - Real betting odds van 80+ bookmakers
   - Perfect voor ons systeem!
   
4. ⭐ FOOTYSTATS
   - 100 calls/dag gratis
   - xG + advanced stats
   - Goede aanvulling op API-Football

ACTIE:
Welke wil je dat ik integreer? OpenLigaDB kan ik direct doen (geen key nodig).
Voor de anderen heb je alleen een gratis account nodig.
""")

print("\n🚀 Wil je dat ik een van deze APIs integreer?")
print("   1. OpenLigaDB (direct, geen key)")
print("   2. The Odds API (beste odds data)")
print("   3. FootyStats (beste xG data)")
print("   4. Alles van bovenstaande")
