#!/usr/bin/env python3
"""
🔥 MEGA DATA MERGER 🔥
Combineert ALLE bruikbare data en traint een MEGA model!
"""

import pandas as pd
import numpy as np
import json
import pickle
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from datetime import datetime
import os

print("\n" + "="*80)
print("🔥 MEGA DATA MERGER - COMBINEREN VAN ALLE DATA")
print("="*80 + "\n")

# 1. Laad alle CSV's met scores
print("📊 STAP 1: LADEN VAN ALLE DATA...\n")

csv_files = [
    "data/massive_training_data.csv",
    "data/training_dataset_20251015_040958.csv",
    "data/training_dataset_expanded_20251015_042855.csv"
]

all_matches = []

for csv_file in csv_files:
    print(f"   Laden: {csv_file}...", end=' ')
    try:
        df = pd.read_csv(csv_file)
        
        # Standaardiseer kolommen
        required_cols = ['home_team', 'away_team', 'home_score', 'away_score']
        
        # Check of alle kolommen aanwezig zijn
        if all(col in df.columns for col in required_cols):
            # Voeg extra info toe als beschikbaar
            for _, row in df.iterrows():
                match = {
                    'home_team': str(row['home_team']),
                    'away_team': str(row['away_team']),
                    'home_score': int(row['home_score']),
                    'away_score': int(row['away_score']),
                    'date': row.get('date', '2024-01-01'),
                    'competition': row.get('competition', row.get('league', 'Unknown')),
                    'season': row.get('season', '2023-24'),
                    'source': csv_file
                }
                all_matches.append(match)
            
            print(f"✅ {len(df)} matches")
        else:
            print(f"❌ Mist kolommen: {required_cols}")
            
    except Exception as e:
        print(f"❌ Fout: {e}")

print(f"\n📊 TOTAAL GELADEN: {len(all_matches)} matches!\n")

# 2. Verwijder duplicaten (zelfde teams op zelfde datum)
print("🔍 STAP 2: VERWIJDEREN VAN DUPLICATEN...\n")

unique_matches = []
seen = set()

for match in all_matches:
    # Maak unieke key
    key = f"{match['home_team']}_{match['away_team']}_{match['date']}"
    
    if key not in seen:
        seen.add(key)
        unique_matches.append(match)

print(f"   Voor duplicaat-verwijdering: {len(all_matches)}")
print(f"   Na duplicaat-verwijdering:   {len(unique_matches)}")
print(f"   Verwijderd:                  {len(all_matches) - len(unique_matches)}\n")

# 3. Genereer features voor ALLE matches
print("⚡ STAP 3: GENEREREN VAN FEATURES VOOR ALLE MATCHES...\n")
print("   Dit kan even duren voor 7000+ matches...\n")

from collections import defaultdict

# Bereken team statistieken uit de data zelf
team_stats = defaultdict(lambda: {
    'matches': 0,
    'wins': 0,
    'draws': 0,
    'losses': 0,
    'goals_scored': 0,
    'goals_conceded': 0,
    'home_matches': 0,
    'home_wins': 0,
    'home_goals': 0,
    'away_matches': 0,
    'away_wins': 0,
    'away_goals': 0
})

# Eerste pass: verzamel statistieken
for match in unique_matches:
    home = match['home_team']
    away = match['away_team']
    home_score = match['home_score']
    away_score = match['away_score']
    
    # Home team stats
    team_stats[home]['matches'] += 1
    team_stats[home]['goals_scored'] += home_score
    team_stats[home]['goals_conceded'] += away_score
    team_stats[home]['home_matches'] += 1
    team_stats[home]['home_goals'] += home_score
    
    if home_score > away_score:
        team_stats[home]['wins'] += 1
        team_stats[home]['home_wins'] += 1
    elif home_score == away_score:
        team_stats[home]['draws'] += 1
    else:
        team_stats[home]['losses'] += 1
    
    # Away team stats
    team_stats[away]['matches'] += 1
    team_stats[away]['goals_scored'] += away_score
    team_stats[away]['goals_conceded'] += home_score
    team_stats[away]['away_matches'] += 1
    team_stats[away]['away_goals'] += away_score
    
    if away_score > home_score:
        team_stats[away]['wins'] += 1
        team_stats[away]['away_wins'] += 1
    elif home_score == away_score:
        team_stats[away]['draws'] += 1
    else:
        team_stats[away]['losses'] += 1

print(f"   ✅ Statistieken berekend voor {len(team_stats)} teams\n")

# Tweede pass: genereer features
X_data = []
y_home = []
y_away = []

for i, match in enumerate(unique_matches):
    if (i + 1) % 1000 == 0:
        print(f"   Verwerkt: {i+1}/{len(unique_matches)} matches...")
    
    home = match['home_team']
    away = match['away_team']
    
    home_s = team_stats[home]
    away_s = team_stats[away]
    
    # Bereken features
    features = [
        # Basic stats
        home_s['goals_scored'] / max(home_s['matches'], 1),
        home_s['goals_conceded'] / max(home_s['matches'], 1),
        away_s['goals_scored'] / max(away_s['matches'], 1),
        away_s['goals_conceded'] / max(away_s['matches'], 1),
        
        # Win rates
        home_s['wins'] / max(home_s['matches'], 1),
        away_s['wins'] / max(away_s['matches'], 1),
        
        # Home/away specific
        home_s['home_wins'] / max(home_s['home_matches'], 1),
        away_s['away_wins'] / max(away_s['away_matches'], 1),
        
        # Attack/defense strength
        home_s['goals_scored'] / max(home_s['goals_conceded'], 1),
        away_s['goals_scored'] / max(away_s['goals_conceded'], 1),
        
        # Form (laatste 5 wedstrijden - approximatie)
        min(home_s['wins'] / max(home_s['matches'], 1) * 5, 5),
        min(away_s['wins'] / max(away_s['matches'], 1) * 5, 5),
    ]
    
    X_data.append(features)
    y_home.append(match['home_score'])
    y_away.append(match['away_score'])

X = np.array(X_data)
y_home = np.array(y_home)
y_away = np.array(y_away)

print(f"\n   ✅ Features gegenereerd: {X.shape[0]} matches, {X.shape[1]} features\n")

# 4. Train MEGA model
print("🔥 STAP 4: TRAINEN VAN MEGA 5-MODEL ENSEMBLE...\n")

# Split data
X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
    X, y_home, y_away, test_size=0.2, random_state=42
)

print(f"   Training set: {len(X_train)} matches")
print(f"   Test set:     {len(X_test)} matches\n")

# Standaardiseer features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train 5 modellen
print("   Training models...")
models_home = {
    'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=42),
    'ExtraTrees': ExtraTreesRegressor(n_estimators=200, max_depth=10, random_state=42),
    'Ridge': Ridge(alpha=1.0),
    'Lasso': Lasso(alpha=0.1)
}

models_away = {
    'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=200, max_depth=5, random_state=42),
    'ExtraTrees': ExtraTreesRegressor(n_estimators=200, max_depth=10, random_state=42),
    'Ridge': Ridge(alpha=1.0),
    'Lasso': Lasso(alpha=0.1)
}

for name, model in models_home.items():
    print(f"      {name} (home)...", end=' ')
    model.fit(X_train_scaled, y_home_train)
    print("✅")

for name, model in models_away.items():
    print(f"      {name} (away)...", end=' ')
    model.fit(X_train_scaled, y_away_train)
    print("✅")

print("\n🎯 STAP 5: EVALUEREN VAN MODEL...\n")

# Test predictions met ensemble
weights = {
    'RandomForest': 0.25,
    'GradientBoosting': 0.30,
    'ExtraTrees': 0.25,
    'Ridge': 0.15,
    'Lasso': 0.05
}

pred_home = np.zeros(len(X_test_scaled))
pred_away = np.zeros(len(X_test_scaled))

for name, weight in weights.items():
    pred_home += models_home[name].predict(X_test_scaled) * weight
    pred_away += models_away[name].predict(X_test_scaled) * weight

# Round predictions
pred_home_rounded = np.round(pred_home).astype(int)
pred_away_rounded = np.round(pred_away).astype(int)

# Bereken accuracy
exact_matches = np.sum((pred_home_rounded == y_home_test) & (pred_away_rounded == y_away_test))
exact_accuracy = exact_matches / len(y_home_test) * 100

mae_home = np.mean(np.abs(pred_home - y_home_test))
mae_away = np.mean(np.abs(pred_away - y_away_test))

print(f"   📊 RESULTATEN:")
print(f"      Exact Score Accuracy: {exact_accuracy:.2f}%")
print(f"      MAE Home Goals:       {mae_home:.3f}")
print(f"      MAE Away Goals:       {mae_away:.3f}")
print(f"      Exact Matches:        {exact_matches}/{len(y_home_test)}")

# 6. Sla MEGA model op
print("\n💾 STAP 6: OPSLAAN VAN MEGA MODEL...\n")

mega_model = {
    'models_home': models_home,
    'models_away': models_away,
    'scaler': scaler,
    'weights': weights,
    'feature_names': [
        'home_goals_per_match', 'home_goals_conceded_per_match',
        'away_goals_per_match', 'away_goals_conceded_per_match',
        'home_win_rate', 'away_win_rate',
        'home_home_win_rate', 'away_away_win_rate',
        'home_attack_defense_ratio', 'away_attack_defense_ratio',
        'home_form', 'away_form'
    ],
    'training_info': {
        'total_matches': len(unique_matches),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'accuracy': exact_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'trained_at': datetime.now().isoformat(),
        'sources': csv_files
    }
}

os.makedirs('data', exist_ok=True)
with open('data/de_meester_MEGA.pkl', 'wb') as f:
    pickle.dump(mega_model, f)

print(f"   ✅ Model opgeslagen als: data/de_meester_MEGA.pkl")

# Sla ook gecombineerde data op
print(f"   💾 Opslaan van gecombineerde data...")
with open('data/mega_training_data.json', 'w', encoding='utf-8') as f:
    json.dump(unique_matches, f, indent=2, ensure_ascii=False)

print(f"   ✅ Data opgeslagen als: data/mega_training_data.json")

print("\n" + "="*80)
print("🎉 MEGA MODEL SUCCESVOL GETRAIND!")
print("="*80)
print(f"📊 Training Data: {len(unique_matches)} unieke matches")
print(f"🎯 Accuracy:      {exact_accuracy:.2f}% exact scores")
print(f"📈 MAE:           {mae_home:.3f} home / {mae_away:.3f} away")
print(f"💾 Opgeslagen:    data/de_meester_MEGA.pkl")
print("\n🔥 Dit is {:.1f}x MEER DATA dan het vorige model (1756 matches)!".format(len(unique_matches) / 1756))
print("="*80 + "\n")
