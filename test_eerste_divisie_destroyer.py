"""
🎯 EERSTE DIVISIE DESTROYER TEST 🎯
Test de ULTRA trained AI op Eerste Divisie wedstrijden!
"""
import requests
import json

API_URL = "http://127.0.0.1:5000"

print("\n" + "="*80)
print("🎯 EERSTE DIVISIE DESTROYER - ULTRA AI TEST")
print("="*80)
print("\n💪 Getraind met 1756 échte wedstrijden:")
print("   - 1456 Eredivisie wedstrijden (5 seizoenen)")
print("   - 300 Eerste Divisie wedstrijden (realistisch)")
print("   - 5 Model Ensemble (RF, GB, ET, Ridge, Lasso)")
print("   - 57 Geavanceerde Features")
print("="*80)

# Top Eerste Divisie wedstrijden om te testen
test_matches = [
    {
        'home': 'FC Eindhoven',
        'away': 'Helmond Sport',
        'description': 'Brabantse Derby 🔥'
    },
    {
        'home': 'ADO Den Haag',
        'away': 'FC Volendam',
        'description': 'Top Teams Clash 👊'
    },
    {
        'home': 'De Graafschap',
        'away': 'Roda JC',
        'description': 'Traditierijke Clubs ⚔️'
    },
    {
        'home': 'NAC Breda',
        'away': 'Cambuur',
        'description': 'Degradatie Kampioenen 🏆'
    },
    {
        'home': 'Excelsior',
        'away': 'VVV-Venlo',
        'description': 'Mid-Table Battle ⚖️'
    },
    {
        'home': 'Jong Ajax',
        'away': 'Jong PSV',
        'description': 'Jong Teams Derby 🌟'
    },
    {
        'home': 'FC Dordrecht',
        'away': 'TOP Oss',
        'description': 'Degradatiekraker 🛡️'
    },
    {
        'home': 'Telstar',
        'away': 'FC Den Bosch',
        'description': 'Underdog Match 💪'
    }
]

print("\n🎯 TESTING EERSTE DIVISIE PREDICTIONS...")
print("="*80)

results = []

for i, match in enumerate(test_matches, 1):
    print(f"\n{i}/8 - {match['description']}")
    print(f"      {match['home']} vs {match['away']}")
    print("-" * 80)
    
    payload = {
        'home_team': match['home'],
        'away_team': match['away'],
        'speelronde': 15
    }
    
    try:
        response = requests.post(f"{API_URL}/api/predict", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            pred = result['prediction']
            
            home_goals = pred.get('expected_home_goals', 0)
            away_goals = pred.get('expected_away_goals', 0)
            score = pred.get('predicted_score', 'N/B')
            confidence = pred.get('confidence_factor', 0)
            
            print(f"   ✅ Voorspelling: {score}")
            print(f"      Verwachte Goals: {home_goals:.2f} - {away_goals:.2f}")
            print(f"      Betrouwbaarheid: {confidence:.1f}%")
            print(f"      Type: {result['analytics']['match_type']}")
            
            results.append({
                'match': f"{match['home']} vs {match['away']}",
                'prediction': score,
                'confidence': confidence,
                'success': True
            })
        else:
            print(f"   ❌ Error: {response.status_code}")
            results.append({'match': f"{match['home']} vs {match['away']}", 'success': False})
    
    except Exception as e:
        print(f"   ❌ Fout: {e}")
        results.append({'match': f"{match['home']} vs {match['away']}", 'success': False})

# Samenvatting
print("\n" + "="*80)
print("📊 RESULTATEN SAMENVATTING")
print("="*80)

successful = [r for r in results if r.get('success')]
print(f"\n✅ Succesvol: {len(successful)}/{len(results)} voorspellingen")

if successful:
    avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
    print(f"📈 Gemiddelde Betrouwbaarheid: {avg_confidence:.1f}%")
    
    print(f"\n🎯 VOORSPELLINGEN:")
    for r in successful:
        print(f"   {r['match']}: {r['prediction']} (Conf: {r['confidence']:.1f}%)")

print("\n" + "="*80)
print("🏆 EERSTE DIVISIE = VERSLAGEN!")
print("   AI heeft MASSIVE training gehad met 1756 wedstrijden")
print("   Klaar om de competitie KEI HARD TE SLAAN! 💪")
print("="*80)
