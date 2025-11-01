"""
🔥 TEST SCRIPT VOOR EERSTE DIVISIE VOORSPELLINGEN 🔥
"""
import requests
import json
import time

# Wacht even tot de server klaar is
print("⏳ Wacht 3 seconden tot server klaar is...")
time.sleep(3)

API_URL = "http://127.0.0.1:5000"

print("\n" + "="*80)
print("🏆 EERSTE DIVISIE - KEI HARD SLAAN! 🏆")
print("="*80)

# Test 1: Server status
print("\n📊 Test 1: Check server status...")
try:
    response = requests.get(f"{API_URL}/api/status", timeout=5)
    if response.status_code == 200:
        print("✅ Server is LIVE!")
        data = response.json()
        print(f"   Motor: {data.get('statistics', {}).get('engine', 'N/B')}")
        print(f"   Teams in database: {data.get('statistics', {}).get('database_teams', 0)}")
    else:
        print(f"❌ Server antwoordt met status {response.status_code}")
except Exception as e:
    print(f"❌ Kan server niet bereiken: {e}")
    exit(1)

# Test 2: Voorspelling Eerste Divisie wedstrijd
print("\n⚽ Test 2: FC Eindhoven vs Helmond Sport (Brabantse Derby!)")
try:
    payload = {
        "home_team": "FC Eindhoven",
        "away_team": "Helmond Sport",
        "speelronde": 10,
        "user_id": "eerste_divisie_killer"
    }
    
    response = requests.post(f"{API_URL}/api/predict", json=payload, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ VOORSPELLING ONTVANGEN!")
        print(f"\n🏟️  {result['home_team']} vs {result['away_team']}")
        
        pred = result['prediction']
        print(f"\n📈 Voorspelling:")
        print(f"   Score: {pred.get('home_goals', '?')}-{pred.get('away_goals', '?')}")
        print(f"   Verwachte doelpunten thuis: {pred.get('expected_home_goals', 0):.2f}")
        print(f"   Verwachte doelpunten uit: {pred.get('expected_away_goals', 0):.2f}")
        print(f"   Betrouwbaarheid: {pred.get('confidence_factor', 0):.1f}%")
        
        if 'analytics' in result:
            analytics = result['analytics']
            print(f"\n🎯 Analytics:")
            print(f"   Wedstrijdtype: {analytics.get('match_type', 'N/B')}")
            print(f"   Totaal verwachte goals: {analytics.get('total_goals_expected', 0):.2f}")
            print(f"   Thuisvoordeel: {analytics.get('home_advantage', 0):.2%}")
        
        print(f"\n⚙️  Engine: {result.get('engine', 'N/B')}")
        print(f"   Features gebruikt: {result.get('features_used', 0)}")
    else:
        print(f"❌ Voorspelling mislukt: {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Nog een Eerste Divisie wedstrijd
print("\n⚽ Test 3: Den Bosch vs Telstar")
try:
    payload = {
        "home_team": "FC Den Bosch",
        "away_team": "Telstar",
        "speelronde": 10
    }
    
    response = requests.post(f"{API_URL}/api/predict", json=payload, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        pred = result['prediction']
        print(f"✅ {result['home_team']} {pred.get('home_goals', '?')}-{pred.get('away_goals', '?')} {result['away_team']}")
        print(f"   Betrouwbaarheid: {pred.get('confidence_factor', 0):.1f}%")
    else:
        print(f"❌ Voorspelling mislukt: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("🎯 EERSTE DIVISIE TESTS VOLTOOID!")
print("="*80)
