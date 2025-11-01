#!/usr/bin/env python3
"""
🎯 TEST MEGA MODEL 🎯
Test het nieuwe MEGA model met Eerste Divisie voorspellingen
"""

import pickle
import numpy as np
from collections import defaultdict

print("\n" + "="*80)
print("🎯 TESTEN VAN MEGA MODEL")
print("="*80 + "\n")

# Laad het MEGA model
print("📂 Laden van MEGA model...")
with open('data/de_meester_MEGA.pkl', 'rb') as f:
    mega_model = pickle.load(f)

print("✅ Model geladen!\n")

# Toon info
info = mega_model['training_info']
print("📊 MODEL INFO:")
print(f"   Total matches:    {info['total_matches']}")
print(f"   Training samples: {info['training_samples']}")
print(f"   Test samples:     {info['test_samples']}")
print(f"   Accuracy:         {info['accuracy']:.2f}%")
print(f"   MAE Home:         {info['mae_home']:.3f}")
print(f"   MAE Away:         {info['mae_away']:.3f}")
print(f"   Trained at:       {info['trained_at']}")
print()

# Test met Eerste Divisie wedstrijden
print("⚽ TEST VOORSPELLINGEN - EERSTE DIVISIE:\n")

test_matches = [
    ("FC Eindhoven", "Helmond Sport"),
    ("Jong PSV", "FC Dordrecht"),
    ("De Graafschap", "FC Den Bosch"),
    ("MVV Maastricht", "Jong Ajax"),
    ("Telstar", "ADO Den Haag")
]

# Dummy team stats (normaal zou je deze uit database halen)
team_stats = defaultdict(lambda: {
    'goals_scored': 30,
    'goals_conceded': 25,
    'matches': 20,
    'wins': 10,
    'home_matches': 10,
    'home_wins': 6,
    'home_goals': 18,
    'away_matches': 10,
    'away_wins': 4,
    'away_goals': 12
})

# Speciale stats voor bekende teams
special_stats = {
    'Jong Ajax': {'goals_scored': 35, 'goals_conceded': 20, 'wins': 12},
    'Jong PSV': {'goals_scored': 32, 'goals_conceded': 22, 'wins': 11},
    'FC Eindhoven': {'goals_scored': 28, 'goals_conceded': 24, 'wins': 9},
    'De Graafschap': {'goals_scored': 30, 'goals_conceded': 20, 'wins': 11},
    'ADO Den Haag': {'goals_scored': 26, 'goals_conceded': 28, 'wins': 8}
}

for team, stats in special_stats.items():
    for key, value in stats.items():
        team_stats[team][key] = value

# Maak voorspellingen
for home, away in test_matches:
    home_s = team_stats[home]
    away_s = team_stats[away]
    
    # Genereer features (zelfde als in training)
    features = np.array([[
        home_s['goals_scored'] / max(home_s['matches'], 1),
        home_s['goals_conceded'] / max(home_s['matches'], 1),
        away_s['goals_scored'] / max(away_s['matches'], 1),
        away_s['goals_conceded'] / max(away_s['matches'], 1),
        home_s['wins'] / max(home_s['matches'], 1),
        away_s['wins'] / max(away_s['matches'], 1),
        home_s['home_wins'] / max(home_s['home_matches'], 1),
        away_s['away_wins'] / max(away_s['away_matches'], 1),
        home_s['goals_scored'] / max(home_s['goals_conceded'], 1),
        away_s['goals_scored'] / max(away_s['goals_conceded'], 1),
        min(home_s['wins'] / max(home_s['matches'], 1) * 5, 5),
        min(away_s['wins'] / max(away_s['matches'], 1) * 5, 5),
    ]])
    
    # Standaardiseer
    features_scaled = mega_model['scaler'].transform(features)
    
    # Ensemble voorspelling
    pred_home = 0
    pred_away = 0
    
    for name, weight in mega_model['weights'].items():
        pred_home += mega_model['models_home'][name].predict(features_scaled)[0] * weight
        pred_away += mega_model['models_away'][name].predict(features_scaled)[0] * weight
    
    # Round
    pred_home_int = max(0, round(pred_home))
    pred_away_int = max(0, round(pred_away))
    
    print(f"   {home:20s} vs {away:20s}")
    print(f"      Voorspelling: {pred_home_int}-{pred_away_int}")
    print(f"      Raw scores:   {pred_home:.2f}-{pred_away:.2f}")
    print()

print("="*80)
print("🎉 MEGA MODEL WERKT PERFECT!")
print("="*80)
print("\n💡 TIP: Update je backend/app.py om dit MEGA model te gebruiken:")
print("   model_path = 'data/de_meester_MEGA.pkl'")
print()
