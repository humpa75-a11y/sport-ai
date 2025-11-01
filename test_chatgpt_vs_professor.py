"""
🤖 CHATGPT VS PROFESSOR - HEAD-TO-HEAD VERGELIJKING 🎓

Test PROFESSOR op exact dezelfde matches als ChatGPT!
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:5000/api/predict"

# ChatGPT's matches (wat we weten)
test_matches = [
    {
        "home_team": "Netherlands",
        "away_team": "Malta",
        "chatgpt_prediction": "4-0",
        "actual_result": "4-0",
        "chatgpt_correct": True,
        "competition": "International"
    },
    {
        "home_team": "Germany",
        "away_team": "Poland",
        "chatgpt_prediction": "3-0",
        "actual_result": "3-0",
        "chatgpt_correct": True,
        "competition": "International"
    },
    {
        "home_team": "Wolfsburg",
        "away_team": "PSG",
        "chatgpt_prediction": "3-1",
        "actual_result": "???",  # Niet bekend - gebruiker moet invullen!
        "chatgpt_correct": False,  # "bijna goed"
        "competition": "Champions League"
    }
]

print("="*80)
print("🤖 CHATGPT VS PROFESSOR - HEAD-TO-HEAD COMPARISON")
print("="*80)

chatgpt_correct = 0
professor_correct = 0
professor_predictions = []

for i, match in enumerate(test_matches, 1):
    home = match['home_team']
    away = match['away_team']
    
    print(f"\n{'='*80}")
    print(f"Match {i}: {home} vs {away}")
    print(f"{'='*80}")
    print(f"   Competition: {match['competition']}")
    print(f"   ChatGPT voorspelling: {match['chatgpt_prediction']}")
    print(f"   Werkelijke uitslag: {match['actual_result']}")
    print(f"   ChatGPT correct: {'✅ JA' if match['chatgpt_correct'] else '❌ NEE'}")
    
    # PROFESSOR voorspelling
    try:
        response = requests.post(API_URL, json={
            "home_team": home,
            "away_team": away,
            "speelronde": 10
        })
        
        if response.status_code == 200:
            data = response.json()
            pred = data['prediction']
            
            professor_score = pred['most_likely_score']
            professor_conf = pred['confidence_factor']
            
            print(f"\n   🎓 PROFESSOR voorspelling: {professor_score}")
            print(f"   🎓 Confidence: {professor_conf:.1f}%")
            
            # Check if correct
            if match['actual_result'] != "???":
                is_correct = professor_score == match['actual_result']
                print(f"   🎓 PROFESSOR correct: {'✅ JA' if is_correct else '❌ NEE'}")
                
                if is_correct:
                    professor_correct += 1
            else:
                print(f"   ⚠️ Werkelijke uitslag onbekend - kan niet vergelijken!")
            
            professor_predictions.append({
                'match': f"{home} vs {away}",
                'prediction': professor_score,
                'confidence': professor_conf,
                'actual': match['actual_result']
            })
            
        else:
            print(f"   ❌ Fout: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   💡 Is de server running? Start met: python backend/app.py")

    if match['chatgpt_correct']:
        chatgpt_correct += 1

# RESULTATEN
print("\n" + "="*80)
print("📊 FINALE VERGELIJKING")
print("="*80)

known_matches = sum(1 for m in test_matches if m['actual_result'] != "???")

print(f"\nChatGPT:")
print(f"   ✅ Correct: {chatgpt_correct}/{len(test_matches)}")
print(f"   📊 Accuracy: {chatgpt_correct/len(test_matches)*100:.1f}%")

print(f"\nPROFESSOR:")
print(f"   ✅ Correct: {professor_correct}/{known_matches}")
if known_matches > 0:
    print(f"   📊 Accuracy: {professor_correct/known_matches*100:.1f}%")
else:
    print(f"   ⚠️ Geen bekende uitslagen om mee te vergelijken!")

print(f"\n{'='*80}")
print("💡 CONCLUSIES:")
print("="*80)

if known_matches >= 2:
    if professor_correct > chatgpt_correct:
        print("🎓 PROFESSOR wint! Betere voorspellingen op deze dataset.")
    elif professor_correct == chatgpt_correct:
        print("🤝 Gelijkspel! Beide modellen presteren vergelijkbaar.")
    else:
        print("🤖 ChatGPT wint op deze 3 matches!")
        print("   MAAR: 3 matches is te klein voor conclusies.")
        print("   PROFESSOR is getest op 30,167 matches!")

print("\n📌 BELANGRIJKE OPMERKINGEN:")
print("   • ChatGPT claimde 70% (7/10) NA 'optimaliseren'")
print("   • Voor optimalisatie: 20-30% (2-3/10 correct)")
print("   • PROFESSOR: 10.47% exact op 30,167 matches")
print("   • Landenwedstrijden (NL-Malta) zijn MAKKELIJKER dan clubs!")
print("   • 10 matches = te klein sample voor betrouwbare conclusies")
print("   • 'Optimaliseren' suggereert aanpassingen na de wedstrijden?")

print("\n🎯 EERLIJKE VERGELIJKING:")
print("   Test beide modellen op DEZELFDE 100+ matches!")
print("   Dan zie je de ECHTE difference!")
print("="*80)

# Save results
with open('chatgpt_vs_professor_results.json', 'w') as f:
    json.dump({
        'test_matches': test_matches,
        'professor_predictions': professor_predictions,
        'chatgpt_correct': chatgpt_correct,
        'professor_correct': professor_correct,
        'total_matches': len(test_matches),
        'known_results': known_matches
    }, f, indent=2)

print("\n✅ Resultaten opgeslagen in: chatgpt_vs_professor_results.json")
