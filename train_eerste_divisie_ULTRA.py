#!/usr/bin/env python3
"""
🔥 EERSTE DIVISIE ULTRA TRAINER 🔥
Van 9.69% naar 15-17% accuracy in 1 DAG!

MEGA ENSEMBLE:
- 8 verschillende modellen
- Advanced feature engineering
- Eerste Divisie focus
- Continuous learning ready
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, AdaBoostRegressor
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import json
import os
from datetime import datetime

print("="*80)
print("🔥 EERSTE DIVISIE ULTRA TRAINER - START! 🔥")
print("="*80)

# =============================================================================
# LOAD DATA
# =============================================================================

print("\n📥 Laden van MEGA dataset...")

data_file = 'data/eerste_divisie_MEGA.json'

if not os.path.exists(data_file):
    print(f"❌ Data file niet gevonden: {data_file}")
    print("   Run eerst: python ultra_24hour_plan.py")
    exit(1)

with open(data_file, 'r') as f:
    matches = json.load(f)

print(f"✅ {len(matches)} wedstrijden geladen!")

# =============================================================================
# FEATURE ENGINEERING
# =============================================================================

print("\n🔧 Feature engineering...")

# Bereken team statistics
team_stats = {}

df = pd.DataFrame(matches)

for team in set(df['home_team'].tolist() + df['away_team'].tolist()):
    home_matches = df[df['home_team'] == team]
    away_matches = df[df['away_team'] == team]
    
    team_stats[team] = {
        'home_attack': home_matches['home_score'].mean() if len(home_matches) > 0 else 1.5,
        'home_defense': home_matches['away_score'].mean() if len(home_matches) > 0 else 1.0,
        'away_attack': away_matches['away_score'].mean() if len(away_matches) > 0 else 1.2,
        'away_defense': away_matches['home_score'].mean() if len(away_matches) > 0 else 1.5,
        'total_matches': len(home_matches) + len(away_matches),
        'win_rate': (len(home_matches[home_matches['home_score'] > home_matches['away_score']]) +
                    len(away_matches[away_matches['away_score'] > away_matches['home_score']])) / 
                    max(len(home_matches) + len(away_matches), 1)
    }

# Build feature matrix
X_features = []
y_home = []
y_away = []

for match in matches:
    home = match['home_team']
    away = match['away_team']
    
    # Get team stats
    h_stats = team_stats.get(home, team_stats[list(team_stats.keys())[0]])
    a_stats = team_stats.get(away, team_stats[list(team_stats.keys())[0]])
    
    # Create features (24 dimensions)
    features = [
        # Basic strengths (8)
        h_stats['home_attack'],
        h_stats['home_defense'],
        a_stats['away_attack'],
        a_stats['away_defense'],
        h_stats['win_rate'],
        a_stats['win_rate'],
        
        # Ratios (4)
        h_stats['home_attack'] / max(h_stats['home_defense'], 0.5),
        a_stats['away_attack'] / max(a_stats['away_defense'], 0.5),
        
        # Form (4)
        min(h_stats['win_rate'] * 5, 5),
        min(a_stats['win_rate'] * 5, 5),
        
        # Experience (2)
        h_stats['total_matches'] / 100,
        a_stats['total_matches'] / 100,
        
        # Advanced (6)
        h_stats['home_attack'] - a_stats['away_defense'],  # Expected advantage
        a_stats['away_attack'] - h_stats['home_defense'],
        abs(h_stats['win_rate'] - a_stats['win_rate']),  # Skill gap
        (h_stats['home_attack'] + a_stats['away_attack']) / 2,  # Match intensity
        h_stats['home_attack'] * (1 - a_stats['away_defense']/3),  # Weighted attack
        a_stats['away_attack'] * (1 - h_stats['home_defense']/3),
    ]
    
    X_features.append(features)
    y_home.append(match['home_score'])
    y_away.append(match['away_score'])

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
    X, y_home, y_away, test_size=0.2, random_state=42
)

print(f"   Train: {len(X_train)} wedstrijden")
print(f"   Test:  {len(X_test)} wedstrijden")

# Standardize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# =============================================================================
# ULTRA ENSEMBLE - 8 MODELLEN!
# =============================================================================

print("\n🤖 Training ULTRA Ensemble (8 modellen)...")

models_home = {}
models_away = {}

# Weights voor elk model (totaal = 100%)
weights = {
    'RandomForest': 0.20,      # 20% - Beste all-rounder
    'GradientBoosting': 0.25,  # 25% - Meest accurate
    'ExtraTrees': 0.15,        # 15% - Extra variance
    'AdaBoost': 0.10,          # 10% - Boosting extra
    'Ridge': 0.10,             # 10% - Linear baseline
    'Lasso': 0.05,             # 5%  - Feature selection
    'ElasticNet': 0.10,        # 10% - Hybrid linear
    'SVR': 0.05               # 5%  - Non-linear kernel
}

# Train elk model
model_configs = {
    'RandomForest': RandomForestRegressor(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=200, max_depth=7, learning_rate=0.1, random_state=42),
    'ExtraTrees': ExtraTreesRegressor(n_estimators=200, max_depth=15, min_samples_split=5, random_state=42, n_jobs=-1),
    'AdaBoost': AdaBoostRegressor(n_estimators=100, learning_rate=0.8, random_state=42),
    'Ridge': Ridge(alpha=1.0),
    'Lasso': Lasso(alpha=0.5),
    'ElasticNet': ElasticNet(alpha=0.5, l1_ratio=0.5),
    'SVR': SVR(kernel='rbf', C=1.0, epsilon=0.2)
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
    
    print(f"      ✅ {name} trained!")

# =============================================================================
# EVALUATE
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

print(f"\n🎯 RESULTATEN:")
print(f"   ✅ Exact score accuracy: {accuracy:.2f}%")
print(f"   ✅ Goal difference accuracy: {gd_accuracy:.2f}%")
print(f"   ✅ MAE Home: {mae_home:.3f}")
print(f"   ✅ MAE Away: {mae_away:.3f}")
print(f"   ✅ Exact matches: {exact_matches}/{len(y_home_test)}")

# =============================================================================
# SAVE MODEL
# =============================================================================

print(f"\n💾 Opslaan model...")

model_data = {
    'models_home': models_home,
    'models_away': models_away,
    'scaler': scaler,
    'weights': weights,
    'feature_names': [
        'home_attack', 'home_defense', 'away_attack', 'away_defense',
        'home_win_rate', 'away_win_rate', 
        'home_ratio', 'away_ratio',
        'home_form', 'away_form',
        'home_exp', 'away_exp',
        'attack_advantage', 'defense_advantage', 'skill_gap',
        'match_intensity', 'home_weighted_attack', 'away_weighted_attack'
    ],
    'training_info': {
        'total_matches': len(X),
        'train_samples': len(X_train),
        'test_samples': len(X_test),
        'accuracy': accuracy,
        'gd_accuracy': gd_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'trained_date': datetime.now().isoformat(),
        'model_count': len(models_home),
        'competition': 'Eerste Divisie ULTRA'
    }
}

os.makedirs('data', exist_ok=True)
with open('data/eerste_divisie_ULTRA.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print(f"   ✅ Model opgeslagen: data/eerste_divisie_ULTRA.pkl")

# Save metadata
with open('data/eerste_divisie_ULTRA_info.json', 'w') as f:
    json.dump({
        'accuracy': accuracy,
        'gd_accuracy': gd_accuracy,
        'mae_home': mae_home,
        'mae_away': mae_away,
        'total_matches': len(X),
        'trained_date': datetime.now().isoformat()
    }, f, indent=2)

print("\n" + "="*80)
print(f"🔥 EERSTE DIVISIE ULTRA MODEL COMPLEET! 🔥")
print(f"   📊 {len(X)} matches trained")
print(f"   🎯 {accuracy:.2f}% exact score accuracy")
print(f"   🎯 {gd_accuracy:.2f}% goal difference accuracy")
print(f"   🤖 8-model ensemble")
print("="*80)

# Show some example predictions
print("\n📊 Voorbeeld voorspellingen:")
for i in range(min(5, len(y_home_test))):
    print(f"   Voorspeld: {pred_home_int[i]}-{pred_away_int[i]} | Werkelijk: {y_home_test[i]}-{y_away_test[i]} " +
          ("✅" if pred_home_int[i] == y_home_test[i] and pred_away_int[i] == y_away_test[i] else "❌"))
