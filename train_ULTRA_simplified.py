#!/usr/bin/env python3
"""
🔥 EERSTE DIVISIE DOMINATION - SIMPLIFIED! 🔥
Gebruik BESTAANDE 6548 matches en train een ULTRA MODEL!

Target: 15-17% accuracy in ÉÉN DAG!
"""

import pickle
import numpy as np
import json
import os
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, AdaBoostRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error

print("="*80)
print("🔥 EERSTE DIVISIE ULTRA DOMINATION - START! 🔥")
print("="*80)

# =============================================================================
# LOAD EXISTING MEGA DATA
# =============================================================================

print("\n📥 Laden van BESTAANDE MEGA dataset...")

data_file = 'data/mega_training_data.json'

if not os.path.exists(data_file):
    print(f"❌ Data file niet gevonden: {data_file}")
    print("   Probeer een ander bestand...")
    exit(1)

with open(data_file, 'r', encoding='utf-8') as f:
    matches = json.load(f)

print(f"✅ {len(matches)} wedstrijden geladen!")

# =============================================================================
# FEATURE ENGINEERING - ADVANCED!
# =============================================================================

print("\n🔧 Advanced Feature Engineering...")

# Bereken team statistics
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

print(f"✅ {len(team_stats)} teams geanalyseerd")

# Build feature matrix with 30 features!
X_features = []
y_home = []
y_away = []

for match in matches:
    home = match.get('home_team', '')
    away = match.get('away_team', '')
    
    if not home or not away:
        continue
    
    # Get team stats (met defaults)
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
    
    # Create 30 ADVANCED features!
    features = [
        # Basic strengths (8)
        h_stats['avg_goals_scored_home'],
        h_stats['avg_goals_conceded_home'],
        a_stats['avg_goals_scored_away'],
        a_stats['avg_goals_conceded_away'],
        h_stats['win_rate'],
        a_stats['win_rate'],
        h_stats['draw_rate'],
        a_stats['draw_rate'],
        
        # Attack/Defense ratios (4)
        h_stats['avg_goals_scored_home'] / max(h_stats['avg_goals_conceded_home'], 0.5),
        a_stats['avg_goals_scored_away'] / max(a_stats['avg_goals_conceded_away'], 0.5),
        h_stats['avg_goals_scored_home'] / max(a_stats['avg_goals_conceded_away'], 0.5),  # Home attack vs Away defense
        a_stats['avg_goals_scored_away'] / max(h_stats['avg_goals_conceded_home'], 0.5),  # Away attack vs Home defense
        
        # Form indicators (4)
        min(h_stats['win_rate'] * 5, 5),
        min(a_stats['win_rate'] * 5, 5),
        h_stats['total'] / 100,  # Experience
        a_stats['total'] / 100,
        
        # Advanced metrics (8)
        h_stats['avg_goals_scored_home'] - a_stats['avg_goals_conceded_away'],  # Expected advantage
        a_stats['avg_goals_scored_away'] - h_stats['avg_goals_conceded_home'],
        abs(h_stats['win_rate'] - a_stats['win_rate']),  # Skill gap
        (h_stats['avg_goals_scored_home'] + a_stats['avg_goals_scored_away']) / 2,  # Match intensity
        h_stats['avg_goals_scored_home'] * (1 - a_stats['avg_goals_conceded_away']/3),  # Weighted attack
        a_stats['avg_goals_scored_away'] * (1 - h_stats['avg_goals_conceded_home']/3),
        (h_stats['avg_goals_scored_home'] + h_stats['avg_goals_scored_away']) / 2,  # Overall attack
        (h_stats['avg_goals_conceded_home'] + h_stats['avg_goals_conceded_away']) / 2,  # Overall defense
        
        # Combo features (6)
        h_stats['win_rate'] * h_stats['avg_goals_scored_home'],  # Quality attack
        a_stats['win_rate'] * a_stats['avg_goals_scored_away'],
        (1 - h_stats['draw_rate']) * h_stats['avg_goals_scored_home'],  # Decisive attack
        (1 - a_stats['draw_rate']) * a_stats['avg_goals_scored_away'],
        h_stats['avg_goals_scored_home'] + a_stats['avg_goals_conceded_away'],  # Combined metric
        a_stats['avg_goals_scored_away'] + h_stats['avg_goals_conceded_home'],
    ]
    
    X_features.append(features)
    y_home.append(match.get('home_score', 0))
    y_away.append(match.get('away_score', 0))

X = np.array(X_features)
y_home = np.array(y_home)
y_away = np.array(y_away)

print(f"✅ Feature matrix: {X.shape}")
print(f"   Features: {X.shape[1]} dimensions")
print(f"   Samples: {X.shape[0]} wedstrijden")

# =============================================================================
# TRAIN/TEST SPLIT
# =============================================================================

print("\n📊 Train/test split...")

X_train, X_test, y_home_train, y_home_test, y_away_train, y_away_test = train_test_split(
    X, y_home, y_away, test_size=0.15, random_state=42  # 15% test voor meer training data
)

print(f"   Train: {len(X_train)} wedstrijden")
print(f"   Test:  {len(X_test)} wedstrijden")

# Standardize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =============================================================================
# ULTRA ENSEMBLE - 8 MODELLEN + OPTIMIZED HYPERPARAMETERS!
# =============================================================================

print("\n🤖 Training ULTRA Ensemble (8 geoptimaliseerde modellen)...")

models_home = {}
models_away = {}

# OPTIMIZED Weights (na experimenten)
weights = {
    'RandomForest': 0.22,      # 22% - Beste all-rounder
    'GradientBoosting': 0.28,  # 28% - MEEST accurate
    'ExtraTrees': 0.18,        # 18% - Extra variance
    'AdaBoost': 0.08,          # 8%  - Boosting extra
    'Ridge': 0.10,             # 10% - Linear baseline
    'Lasso': 0.04,             # 4%  - Feature selection
    'ElasticNet': 0.08,        # 8%  - Hybrid linear
    'SVR': 0.02                # 2%  - Non-linear kernel (klein gewicht)
}

# OPTIMIZED model configs
model_configs = {
    'RandomForest': RandomForestRegressor(
        n_estimators=300, max_depth=20, min_samples_split=3, 
        min_samples_leaf=2, random_state=42, n_jobs=-1
    ),
    'GradientBoosting': GradientBoostingRegressor(
        n_estimators=250, max_depth=8, learning_rate=0.08, 
        subsample=0.8, random_state=42
    ),
    'ExtraTrees': ExtraTreesRegressor(
        n_estimators=300, max_depth=20, min_samples_split=3,
        min_samples_leaf=2, random_state=42, n_jobs=-1
    ),
    'AdaBoost': AdaBoostRegressor(
        n_estimators=150, learning_rate=0.7, random_state=42
    ),
    'Ridge': Ridge(alpha=0.8),
    'Lasso': Lasso(alpha=0.3),
    'ElasticNet': ElasticNet(alpha=0.4, l1_ratio=0.5),
    'SVR': SVR(kernel='rbf', C=1.5, epsilon=0.15)
}

for name, model in model_configs.items():
    print(f"\n   🔧 Training {name}...")
    
    # Train home goals model
    model_home = model
    model_home.fit(X_train_scaled, y_home_train)
    models_home[name] = model_home
    
    # Train away goals model (nieuwe instance!)
    from copy import deepcopy
    model_away = deepcopy(model)
    model_away.fit(X_train_scaled, y_away_train)
    models_away[name] = model_away
    
    # Quick validation
    pred_h = model_home.predict(X_test_scaled)
    pred_a = model_away.predict(X_test_scaled)
    mae_h = mean_absolute_error(y_home_test, pred_h)
    mae_a = mean_absolute_error(y_away_test, pred_a)
    
    print(f"      ✅ {name} - MAE: {mae_h:.3f} home / {mae_a:.3f} away")

# =============================================================================
# EVALUATE ENSEMBLE
# =============================================================================

print("\n📊 Evaluatie op test set...")

# Ensemble predictions
pred_home_ensemble = np.zeros(len(X_test_scaled))
pred_away_ensemble = np.zeros(len(X_test_scaled))

for name, weight in weights.items():
    pred_home_ensemble += models_home[name].predict(X_test_scaled) * weight
    pred_away_ensemble += models_away[name].predict(X_test_scaled) * weight

# Clip negative predictions
pred_home_ensemble = np.maximum(0, pred_home_ensemble)
pred_away_ensemble = np.maximum(0, pred_away_ensemble)

# Round to integers
pred_home_int = np.round(pred_home_ensemble).astype(int)
pred_away_int = np.round(pred_away_ensemble).astype(int)

# Calculate metrics
mae_home = mean_absolute_error(y_home_test, pred_home_ensemble)
mae_away = mean_absolute_error(y_away_test, pred_away_ensemble)

# Exact score accuracy
exact_matches = sum((pred_home_int == y_home_test) & (pred_away_int == y_away_test))
accuracy = (exact_matches / len(y_home_test)) * 100

# Goal difference accuracy
gd_pred = pred_home_int - pred_away_int
gd_actual = y_home_test - y_away_test
gd_correct = sum(np.sign(gd_pred) == np.sign(gd_actual))
gd_accuracy = (gd_correct / len(y_home_test)) * 100

# Result accuracy (win/draw/loss)
result_correct = 0
for i in range(len(y_home_test)):
    pred_result = 'H' if pred_home_int[i] > pred_away_int[i] else ('A' if pred_home_int[i] < pred_away_int[i] else 'D')
    actual_result = 'H' if y_home_test[i] > y_away_test[i] else ('A' if y_home_test[i] < y_away_test[i] else 'D')
    if pred_result == actual_result:
        result_correct += 1
result_accuracy = (result_correct / len(y_home_test)) * 100

print(f"\n🎯 RESULTATEN:")
print(f"   ✅ Exact score accuracy: {accuracy:.2f}%")
print(f"   ✅ Goal difference accuracy: {gd_accuracy:.2f}%")
print(f"   ✅ Result accuracy (W/D/L): {result_accuracy:.2f}%")
print(f"   ✅ MAE Home: {mae_home:.3f}")
print(f"   ✅ MAE Away: {mae_away:.3f}")
print(f"   ✅ Exact matches: {exact_matches}/{len(y_home_test)}")

# =============================================================================
# SAVE MODEL
# =============================================================================

print(f"\n💾 Opslaan ULTRA model...")

model_data = {
    'models_home': models_home,
    'models_away': models_away,
    'scaler': scaler,
    'weights': weights,
    'feature_names': [f'feature_{i}' for i in range(30)],
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
        'model_count': len(models_home),
        'competition': 'ULTRA PROFESSOR - 8 Models + 30 Features'
    }
}

os.makedirs('data', exist_ok=True)
with open('data/de_meester_ULTRA.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print(f"   ✅ Model opgeslagen: data/de_meester_ULTRA.pkl")

# Save metadata
with open('data/de_meester_ULTRA_info.json', 'w') as f:
    json.dump({
        'accuracy': accuracy,
        'gd_accuracy': gd_accuracy,
        'result_accuracy': result_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'total_matches': len(X),
        'trained_date': datetime.now().isoformat()
    }, f, indent=2)

print("\n" + "="*80)
print(f"🔥 ULTRA PROFESSOR MODEL COMPLEET! 🔥")
print(f"   📊 {len(X)} matches trained")
print(f"   🎯 {accuracy:.2f}% exact score accuracy")
print(f"   🎯 {gd_accuracy:.2f}% goal difference accuracy")
print(f"   🎯 {result_accuracy:.2f}% result accuracy")
print(f"   🤖 8-model ensemble + 30 features")
print(f"   🔥 IMPROVEMENT: {accuracy - 9.69:.2f}% boven oude model!")
print("="*80)

# Show some example predictions
print("\n📊 Voorbeeld voorspellingen:")
for i in range(min(10, len(y_home_test))):
    conf_home = abs(pred_home_ensemble[i] - pred_home_int[i])
    conf_away = abs(pred_away_ensemble[i] - pred_away_int[i])
    confidence = 100 - (conf_home + conf_away) * 50
    
    correct = "✅" if pred_home_int[i] == y_home_test[i] and pred_away_int[i] == y_away_test[i] else "❌"
    
    print(f"   Voorspeld: {pred_home_int[i]}-{pred_away_int[i]} | " +
          f"Werkelijk: {y_home_test[i]}-{y_away_test[i]} | " +
          f"Conf: {confidence:.1f}% {correct}")
