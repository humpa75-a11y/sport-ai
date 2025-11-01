"""
Test API Key - Identify which API this belongs to
==================================================
"""

import requests
import json

api_key = "d5513a02070e4dbba002d3f5c9a78942"

print("="*80)
print("🔍 TESTING API KEY: d5513a02070e4dbba002d3f5c9a78942")
print("="*80)

# =============================================================================
# Test 1: The Odds API
# =============================================================================
print("\n1. Testing The Odds API...")
try:
    url = "https://api.the-odds-api.com/v4/sports"
    params = {'apiKey': api_key}
    response = requests.get(url, params=params, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ THE ODDS API - WORKING!")
        print(f"   Sports available: {len(data)}")
        print(f"   Sample sports: {[s['key'] for s in data[:3]]}")
        print(f"\n   This is THE ODDS API for betting odds!")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# =============================================================================
# Test 2: Football-Data.org
# =============================================================================
print("\n2. Testing Football-Data.org API...")
try:
    url = "https://api.football-data.org/v4/competitions"
    headers = {'X-Auth-Token': api_key}
    response = requests.get(url, headers=headers, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ FOOTBALL-DATA.ORG - WORKING!")
        print(f"   Competitions available: {len(data.get('competitions', []))}")
        print(f"\n   This is FOOTBALL-DATA.ORG for football data!")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# =============================================================================
# Test 3: FootyStats
# =============================================================================
print("\n3. Testing FootyStats API...")
try:
    url = f"https://api.footystats.org/leagues?key={api_key}"
    response = requests.get(url, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ FOOTYSTATS - WORKING!")
        print(f"   Data: {data}")
        print(f"\n   This is FOOTYSTATS for advanced statistics!")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# =============================================================================
# Test 4: Sportmonks
# =============================================================================
print("\n4. Testing Sportmonks API...")
try:
    url = "https://soccer.sportmonks.com/api/v2.0/leagues"
    params = {'api_token': api_key}
    response = requests.get(url, params=params, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SPORTMONKS - WORKING!")
        print(f"   Leagues available: {len(data.get('data', []))}")
        print(f"\n   This is SPORTMONKS for comprehensive sports data!")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# =============================================================================
# Test 5: API-Football (alternative endpoint)
# =============================================================================
print("\n5. Testing API-Football (RapidAPI)...")
try:
    url = "https://api-football-v1.p.rapidapi.com/v3/status"
    headers = {
        'X-RapidAPI-Key': api_key,
        'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
    }
    response = requests.get(url, headers=headers, timeout=5)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API-FOOTBALL (RapidAPI) - WORKING!")
        print(f"   Data: {data}")
        print(f"\n   This is API-FOOTBALL via RapidAPI!")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# =============================================================================
# Test 6: Generic API key test
# =============================================================================
print("\n6. Testing generic patterns...")
try:
    # Try as query parameter
    test_urls = [
        f"https://api.example.com/test?api_key={api_key}",
        f"https://api.example.com/test?apikey={api_key}",
        f"https://api.example.com/test?key={api_key}",
    ]
    print(f"   API key format analysis:")
    print(f"   Length: {len(api_key)} characters")
    print(f"   Format: {api_key[:8]}...{api_key[-8:]}")
    print(f"   Pattern: Looks like a MD5-style key (32 hex chars)")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*80)
print("🎯 API KEY IDENTIFICATION COMPLETE")
print("="*80)
print("\nIf one of the tests succeeded, we know which API to integrate!")
