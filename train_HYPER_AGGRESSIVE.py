#!/usr/bin/env python3
"""
🔥 HYPER-AGGRESSIVE TUNING! 🔥
DOEL: 12-15% exact + 60%+ result accuracy!

STRATEGIE:
- VEEL meer trees (500+)
- Diepere depth (30+)
- Lagere learning rates voor stability
- Cross-validation
"""

import pickle
import numpy as np
import json
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

print("="*80)
print("🔥 HYPER-AGGRESSIVE TUNING - TARGET: 15%+ ACCURACY! 🔥")
print("="*80)

# Load data
with open('data/mega_training_data.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"✅ {len(matches)} wedstrijden geladen!")

# Feature engineering (same as before, maar nu met BETERE features)
team_stats = {}

for match in matches:
    for team_type in ['home', 'away']:
        team = match.get(f'{team_type}_team', '')
        if not team:
            continue
        
        if team not in team_stats:
            team_stats[team] = {
                'goals_scored_home': [],
                'goals_conceded_home': [],
                'goals_scored_away': [],
                'goals_conceded_away': [],
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'total': 0
            }
        
        if team_type == 'home':
            team_stats[team]['goals_scored_home'].append(match.get('home_score', 0))
            team_stats[team]['goals_conceded_home'].append(match.get('away_score', 0))
        else:
            team_stats[team]['goals_scored_away'].append(match.get('away_score', 0))
            team_stats[team]['goals_conceded_away'].append(match.get('home_score', 0))
        
        # Result
        if team_type == 'home':
            if match.get('home_score', 0) > match.get('away_score', 0):
                team_stats[team]['wins'] += 1
            elif match.get('home_score', 0) == match.get('away_score', 0):
                team_stats[team]['draws'] += 1
            else:
                team_stats[team]['losses'] += 1
        else:
            if match.get('away_score', 0) > match.get('home_score', 0):
                team_stats[team]['wins'] += 1
            elif match.get('away_score', 0) == match.get('home_score', 0):
                team_stats[team]['draws'] += 1
            else:
                team_stats[team]['losses'] += 1
        
        team_stats[team]['total'] += 1

# Calculate aggregated stats
for team in team_stats:
    stats = team_stats[team]
    stats['avg_goals_scored_home'] = np.mean(stats['goals_scored_home']) if stats['goals_scored_home'] else 1.5
    stats['avg_goals_conceded_home'] = np.mean(stats['goals_conceded_home']) if stats['goals_conceded_home'] else 1.0
    stats['avg_goals_scored_away'] = np.mean(stats['goals_scored_away']) if stats['goals_scored_away'] else 1.2
    stats['avg_goals_conceded_away'] = np.mean(stats['goals_conceded_away']) if stats['goals_conceded_away'] else 1.5
    stats['win_rate'] = stats['wins'] / max(stats['total'], 1)
    stats['draw_rate'] = stats['draws'] / max(stats['total'], 1)

# Build features (12 simple but POWERFUL features)
X_features = []
y_home = []
y_away = []

for match in matches:
    home = match.get('home_team', '')
    away = match.get('away_team', '')
    
    if not home or not away:
        continue
    
    h_stats = team_stats.get(home, {
        'avg_goals_scored_home': 1.5,
        'avg_goals_conceded_home': 1.0,
        'avg_goals_scored_away': 1.2,
        'avg_goals_conceded_away': 1.5,
        'win_rate': 0.5,
        'draw_rate': 0.25,
        'total': 10
    })
    
    a_stats = team_stats.get(away, {
        'avg_goals_scored_home': 1.5,
        'avg_goals_conceded_home': 1.0,
        'avg_goals_scored_away': 1.2,
        'avg_goals_conceded_away': 1.5,
        'win_rate': 0.5,
        'draw_rate': 0.25,
        'total': 10
    })
    
    # 12 KILLER features
    features = [
        h_stats['avg_goals_scored_home'],
        h_stats['avg_goals_conceded_home'],
        a_stats['avg_goals_scored_away'],
        a_stats['avg_goals_conceded_away'],
        h_stats['win_rate'],
        a_stats['win_rate'],
        h_stats['avg_goals_scored_home'] / max(h_stats['avg_goals_conceded_home'], 0.5),
        a_stats['avg_goals_scored_away'] / max(a_stats['avg_goals_conceded_away'], 0.5),
        min(h_stats['win_rate'] * 5, 5),
        min(a_stats['win_rate'] * 5, 5),
        h_stats['total'] / 100,
        a_stats['total'] / 100,
    ]
    
    X_features.append(features)
    y_home.append(match.get('home_score', 0))
    y_away.append(match.get('away_score', 0))

X = np.array(X_features)
y_home = np.array(y_home)
y_away = np.array(y_away)

print(f"✅ Feature matrix: {X.shape}")

# Train/test split - 10% test voor MEER training data!
X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
    X, y_home, y_away, test_size=0.10, random_state=42
)

print(f"   Train: {len(X_train)} wedstrijden")
print(f"   Test:  {len(X_test)} wedstrijden")

# Standardize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =============================================================================
# HYPER-AGGRESSIVE MODELS!
# =============================================================================

print("\n🔥 Training HYPER-AGGRESSIVE models...")

models_home = {}
models_away = {}

# AGGRESSIVE weights - focus op beste modellen
weights = {
    'RandomForest': 0.30,       # 30% - Best performer
    'GradientBoosting': 0.35,   # 35% - Most accurate
    'ExtraTrees': 0.25,         # 25% - Extra variance
    'Ridge': 0.10               # 10% - Baseline stability
}

# HYPER-AGGRESSIVE configs
model_configs = {
    'RandomForest': RandomForestRegressor(
        n_estimators=500,        # 500 trees!
        max_depth=35,            # Zeer diep
        min_samples_split=2,     # Maximale splits
        min_samples_leaf=1,      # Minimale leaf size
        max_features='sqrt',     # Feature subsampling
        random_state=42,
        n_jobs=-1
    ),
    'GradientBoosting': GradientBoostingRegressor(
        n_estimators=400,        # 400 iterations
        max_depth=10,            # Diep genoeg
        learning_rate=0.05,      # LAGE learning rate voor stability
        subsample=0.9,           # Hoog subsample
        min_samples_split=2,
        random_state=42
    ),
    'ExtraTrees': ExtraTreesRegressor(
        n_estimators=500,        # 500 trees
        max_depth=35,            # Zeer diep
        min_samples_split=2,
        min_samples_leaf=1,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    ),
    'Ridge': Ridge(alpha=0.5)    # Lichte regularization
}

for name, model in model_configs.items():
    print(f"\n   🔧 Training {name}...")
    
    # Train home
    model_home = model
    model_home.fit(X_train_scaled, y_home_train)
    models_home[name] = model_home
    
    # Train away
    from copy import deepcopy
    model_away = deepcopy(model)
    model_away.fit(X_train_scaled, y_away_train)
    models_away[name] = model_away
    
    # Validate
    pred_h = model_home.predict(X_test_scaled)
    pred_a = model_away.predict(X_test_scaled)
    mae_h = mean_absolute_error(y_home_test, pred_h)
    mae_a = mean_absolute_error(y_away_test, pred_a)
    
    print(f"      ✅ MAE: {mae_h:.3f} home / {mae_a:.3f} away")

# =============================================================================
# EVALUATE
# =============================================================================

print("\n📊 Evaluatie...")

# Ensemble predictions
pred_home_ensemble = np.zeros(len(X_test_scaled))
pred_away_ensemble = np.zeros(len(X_test_scaled))

for name, weight in weights.items():
    pred_home_ensemble += models_home[name].predict(X_test_scaled) * weight
    pred_away_ensemble += models_away[name].predict(X_test_scaled) * weight

# Clip and round
pred_home_ensemble = np.maximum(0, pred_home_ensemble)
pred_away_ensemble = np.maximum(0, pred_away_ensemble)
pred_home_int = np.round(pred_home_ensemble).astype(int)
pred_away_int = np.round(pred_away_ensemble).astype(int)

# Metrics
mae_home = mean_absolute_error(y_home_test, pred_home_ensemble)
mae_away = mean_absolute_error(y_away_test, pred_away_ensemble)

exact_matches = sum((pred_home_int == y_home_test) & (pred_away_int == y_away_test))
accuracy = (exact_matches / len(y_home_test)) * 100

gd_pred = pred_home_int - pred_away_int
gd_actual = y_home_test - y_away_test
gd_correct = sum(np.sign(gd_pred) == np.sign(gd_actual))
gd_accuracy = (gd_correct / len(y_home_test)) * 100

result_correct = sum(
    ('H' if pred_home_int[i] > pred_away_int[i] else ('A' if pred_home_int[i] < pred_away_int[i] else 'D')) ==
    ('H' if y_home_test[i] > y_away_test[i] else ('A' if y_home_test[i] < y_away_test[i] else 'D'))
    for i in range(len(y_home_test))
)
result_accuracy = (result_correct / len(y_home_test)) * 100

print(f"\n🎯 HYPER-AGGRESSIVE RESULTATEN:")
print(f"   ✅ Exact score: {accuracy:.2f}%")
print(f"   ✅ Goal difference: {gd_accuracy:.2f}%")
print(f"   ✅ Result (W/D/L): {result_accuracy:.2f}%")
print(f"   ✅ MAE: {mae_home:.3f} home / {mae_away:.3f} away")
print(f"   ✅ Exact: {exact_matches}/{len(y_home_test)}")

# =============================================================================
# SAVE
# =============================================================================

model_data = {
    'models_home': models_home,
    'models_away': models_away,
    'scaler': scaler,
    'weights': weights,
    'feature_names': ['feature_' + str(i) for i in range(12)],
    'training_info': {
        'total_matches': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'accuracy': accuracy,
        'gd_accuracy': gd_accuracy,
        'result_accuracy': result_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'trained_date': datetime.now().isoformat(),
        'model_count': 4,
        'competition': 'HYPER-AGGRESSIVE PROFESSOR - 4 Deep Models'
    }
}

with open('data/de_meester_HYPER.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print(f"\n✅ Model opgeslagen: data/de_meester_HYPER.pkl")

print("\n" + "="*80)
print(f"🔥 HYPER-AGGRESSIVE MODEL KLAAR! 🔥")
print(f"   📊 {len(X)} matches | {accuracy:.2f}% exact")
print(f"   🎯 {result_accuracy:.2f}% result accuracy!")
print(f"   🔥 IMPROVEMENT: +{accuracy - 9.69:.2f}% vs oude model!")
if accuracy >= 12:
    print(f"   🏆🏆🏆 TARGET BEREIKT! 12%+ ACCURACY! 🏆🏆🏆")
print("="*80)

# Examples
print("\n📊 TOP 10 voorspellingen:")
for i in range(min(10, len(y_home_test))):
    correct = "✅" if pred_home_int[i] == y_home_test[i] and pred_away_int[i] == y_away_test[i] else "❌"
    print(f"   {pred_home_int[i]}-{pred_away_int[i]} vs {y_home_test[i]}-{y_away_test[i]} {correct}")
